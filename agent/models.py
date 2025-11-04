from django.db import models
import uuid


class A2AMessage(models.Model):
    """Stores user–AI or AI–AI messages for context and analysis."""
    ROLE_CHOICES = [
        ("user", "User"),
        ("assistant", "Assistant"),
        ("system", "System"),
    ]

    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="messages", null=True,  # ✅ Allow null for now
    blank=True)  # ✅ ADD THIS
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    session_id = models.CharField(
        max_length=64, blank=True, null=True,
        help_text="Optional session or conversation ID"
    )


    def __str__(self):
        return f"[{self.role}] {self.content[:40]}..."

class User(models.Model):
    """Represents a Telex user interacting with the AI agent."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    telex_id = models.CharField(max_length=200, unique=True)
    name = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.name or self.telex_id


class Checkin(models.Model):
    """Stores user mood check-ins and detected sentiment."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="checkins")
    text = models.TextField()
    mood = models.CharField(max_length=50, blank=True, null=True)
    sentiment = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Checkin for {self.user.telex_id} on {self.created_at.strftime('%Y-%m-%d')}"


class Reframe(models.Model):
    """Stores reframed negative thoughts from the AI agent."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reframes")
    original_text = models.TextField()
    reframed_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Reframe for {self.user.telex_id} ({self.created_at.strftime('%Y-%m-%d')})"
