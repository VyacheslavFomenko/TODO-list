from celery import shared_task
from celery.utils.log import get_task_logger
from django.core.mail import EmailMessage

logger = get_task_logger(__name__)


@shared_task(name="send_email_task")
def send_email_task(subject, message, email_from, recipient_list):
    msg = EmailMessage(subject, message, email_from, recipient_list)
    msg.content_subtype = "html"
    msg.send()
