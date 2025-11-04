from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import User, Checkin, Reframe, A2AMessage
from .utils import detect_sentiment, detect_risk, gemini_reframe
from django.utils import timezone
from datetime import timedelta
import google.generativeai as genai
import os
import logging
from django.db import DatabaseError
from .serializers import A2AMessageSerializer

logger = logging.getLogger(__name__)

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

@api_view(["POST"])
def handle_message(request):
    """
    Unified A2A endpoint — now with short-term memory context.
    Gemini sees the last few messages for more natural responses.
    """
    try:
        data = request.data or {}
        text = (data.get("message") or "").strip()
        telex_user_id = data.get("user_id") or data.get("sender") or "anonymous"

        # --- Get or create user ---
        try:
            user, _ = User.objects.get_or_create(telex_id=telex_user_id)
        except DatabaseError as db_err:
            logger.error(f"Database error creating/fetching user: {db_err}")
            return Response(
                {"response": "Sorry, there was an issue accessing user data."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # --- Empty message fallback ---
        if not text:
            msg = (
                "Hi 👋 I'm PocketTherapist — your AI check-in buddy.\n"
                "You can say things like:\n"
                "- 'I feel anxious today'\n"
                "- 'I'm happy this morning!'\n"
                "I'll listen, respond with empathy, and offer CBT-based reframes 💛"
            )
            A2AMessage.objects.create(role="assistant", content=msg, user=user)
            return Response({"response": msg})

        # --- Record user message ---
        A2AMessage.objects.create(role="user", content=text, user=user)

        # --- SAFETY / RISK DETECTION ---
        if detect_risk(text):
            try:
                Checkin.objects.create(user=user, text=text, sentiment="risk")
            except DatabaseError:
                logger.warning("Failed to log risk checkin.")
            crisis_msg = (
                "I'm really sorry you're feeling this way 💛. "
                "I’m not a crisis service, but I want you to be safe. "
                "If you’re in immediate danger, please call your local emergency number. "
                "In Kenya, you can reach Befrienders at +254 722 178 177."
            )
            A2AMessage.objects.create(role="assistant", content=crisis_msg, user=user)
            return Response({"response": crisis_msg})

        # --- SENTIMENT DETECTION ---
        sentiment = detect_sentiment(text)
        try:
            Checkin.objects.create(user=user, text=text, sentiment=sentiment)
        except DatabaseError:
            logger.error("Error saving checkin to database.")

        # --- Fetch recent chat history for context ---
        recent_msgs = (
            A2AMessage.objects.filter(user=user)
            .order_by("-created_at")[:6]
            .values_list("role", "content")
        )
        recent_msgs = list(reversed(recent_msgs))  # chronological order

        # Format as conversation text
        history_text = "\n".join(
            f"{'User' if r == 'user' else 'Assistant'}: {c}" for r, c in recent_msgs
        )

        # --- Determine AI Response Path ---
        if sentiment.lower() in ["negative", "sad", "depressed", "angry", "anxious"]:
            # Use Gemini Reframe from utils, but include recent context
            try:
                model = genai.GenerativeModel("gemini-2.5-flash")
                prompt = (
                    "You are PocketTherapist, a compassionate CBT-based AI.\n"
                    "Here's the recent conversation:\n"
                    f"{history_text}\n\n"
                    f"User's latest message: \"{text}\"\n"
                    "Reframe their negative thought empathetically. Keep it short and warm."
                )
                response = model.generate_content(prompt)
                ai_reply = response.text.strip()
            except Exception as e:
                logger.error(f"Gemini error (reframe): {e}")
                ai_reply = gemini_reframe(text)

            # Save reframe
            try:
                Reframe.objects.create(user=user, original_text=text, reframed_text=ai_reply)
            except DatabaseError:
                logger.warning("Failed to save reframe record.")

        else:
            # Neutral or positive — friendly chat
            try:
                model = genai.GenerativeModel("gemini-2.5-flash")
                prompt = (
                    "You are PocketTherapist, a kind and conversational AI.\n"
                    f"Recent conversation:\n{history_text}\n\n"
                    f"User: {text}\n"
                    "Respond in 3–4 sentences. Stay warm, reflective, and encouraging."
                )
                response = model.generate_content(prompt)
                ai_reply = response.text.strip()
            except Exception as e:
                logger.error(f"Gemini error (chat): {e}")
                ai_reply = "I'm here with you, but I’m having trouble responding right now 💛."

        # --- Record assistant reply ---
        A2AMessage.objects.create(role="assistant", content=ai_reply, user=user)

        return Response({"response": ai_reply})

    except Exception as e:
        logger.exception(f"Unhandled error in handle_message: {e}")
        return Response(
            {"response": "Something went wrong on our end. Please try again later."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET", "POST"])
def weekly_summary(request):
    """AI-generated weekly reflection of user check-ins."""
    telex_user_id = (
        request.data.get("user_id")
        if request.method == "POST"
        else request.GET.get("user_id")
    ) or "anonymous"

    try:
        user = User.objects.get(telex_id=telex_user_id)
    except User.DoesNotExist:
        return Response({"response": "No data for that user."}, status=status.HTTP_404_NOT_FOUND)

    week_ago = timezone.now() - timedelta(days=7)
    checkins = user.checkins.filter(created_at__gte=week_ago).order_by("created_at")

    if not checkins.exists():
        return Response({"response": "No check-ins in the last 7 days."})

    # Build Gemini input
    lines = [f"{c.created_at.date()}: {c.text} [sentiment: {c.sentiment}]" for c in checkins]
    prompt_body = (
        "Here are the user's checkins for the past 7 days:\n"
        + "\n".join(lines)
        + "\n\nProvide a 120-word summary highlighting emotional trends, 3 recurring themes, "
          "and 3 practical mental health tips."
    )

    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt_body)
        text = response.text.strip()
    except Exception:
        text = "Sorry, unable to generate your summary right now."

    return Response({"response": text}, status=status.HTTP_200_OK)


@api_view(["GET"])
def message_history(request):
    messages = A2AMessage.objects.order_by("-created_at")[:20]
    serializer = A2AMessageSerializer(messages, many=True)
    return Response(serializer.data)
