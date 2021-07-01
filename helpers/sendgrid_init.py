import os

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


def sendgrid_init(message: Mail):
    sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
    sg.send(message)
