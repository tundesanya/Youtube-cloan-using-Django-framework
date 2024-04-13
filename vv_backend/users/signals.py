# FOR TESTING ONLY
from django.conf import settings
import requests
ntfy_topic = settings.NTFY_TOPIC
dhost_url = settings.DHOST_URL

# from urllib.parse import urlencode

from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver

from users.models import EmailVerification, PasswordReset


# TODO: Nishil: Move to Celery & add .delay? async?
@receiver(post_save, sender=EmailVerification)
def send_email_verification(sender, instance, created, **kwargs):
    if created:
        message = f"{dhost_url}/user/verify-email?sent_to={instance.user.email}&token={instance.token}"
        send_mail(
            "Email Verification",
            f"{message}",
            "from@example.com:",
            [instance.sent_to],
            fail_silently=False,
        )
        _ = requests.post(
            f"https://ntfy.sh/{ntfy_topic}",
            data=message.encode("utf-8"),
            headers={"Title": "Email Verification"}
        )

@receiver(post_save, sender=PasswordReset)
def send_reset_password(sender, instance, created, **kwargs):
    if created:
        message = f"{dhost_url}/user/reset-password?sent_to={instance.user.email}&token={instance.token}"
        send_mail(
            "Reset Password",
            f"{message}",
            "from@example.com",
            [instance.user.email],
            fail_silently=False,
        )
        _ = requests.post(
            f"https://ntfy.sh/{ntfy_topic}",
            data=message.encode("utf-8"),
            headers={"Title": "Reset Password"}
        )
