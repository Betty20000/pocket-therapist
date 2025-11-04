from django.urls import path
from . import views

urlpatterns = [
    path("", views.handle_message, name="handle_message"),           # POST: send message, get Gemini reply
    path("weekly-summary/", views.weekly_summary, name="weekly_summary"), # GET: summary
    path("history/", views.message_history, name="message_history"),      # GET: chat history
]
