"""SMTP mailer using aiosmtplib for the notification-service."""
from __future__ import annotations

import logging
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import aiosmtplib

logger = logging.getLogger(__name__)

SMTP_HOST: str = os.getenv("SMTP_HOST", "mailhog")
SMTP_PORT: int = int(os.getenv("SMTP_PORT", "1025"))
SMTP_FROM: str = os.getenv("SMTP_FROM", "noreply@library.org")
SMTP_USERNAME: str = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
SMTP_USE_TLS: bool = os.getenv("SMTP_USE_TLS", "false").lower() == "true"


def _build_checkout_html(book_title: str, due_date: str, record_id: int) -> str:
    return f"""
    <html><body>
    <h2>📚 Checkout Confirmation</h2>
    <p>You have successfully checked out <strong>{book_title}</strong>.</p>
    <p><strong>Due Date:</strong> {due_date}</p>
    <p><strong>Record ID:</strong> {record_id}</p>
    <p>Please return it on time to avoid fines.</p>
    <footer><small>Library Management System</small></footer>
    </body></html>
    """


def _build_return_html(book_title: str, fine_amount: float, record_id: int) -> str:
    fine_msg = f"<p><strong>Fine:</strong> \${fine_amount:.2f}</p>" if fine_amount > 0 else "<p>No fine — returned on time!</p>"
    return f"""
    <html><body>
    <h2>✅ Return Confirmation</h2>
    <p>You have returned <strong>{book_title}</strong>.</p>
    {fine_msg}
    <p><strong>Record ID:</strong> {record_id}</p>
    <footer><small>Library Management System</small></footer>
    </body></html>
    """


async def send_email(to_email: str, subject: str, html_body: str) -> None:
    msg = MIMEMultipart("alternative")
    msg["From"] = SMTP_FROM
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(html_body, "html"))

    try:
        await aiosmtplib.send(
            msg,
            hostname=SMTP_HOST,
            port=SMTP_PORT,
            username=SMTP_USERNAME or None,
            password=SMTP_PASSWORD or None,
            use_tls=SMTP_USE_TLS,
        )
        logger.info("Email sent to %s — %s", to_email, subject)
    except Exception as exc:
        logger.error("Failed to send email to %s: %s", to_email, exc)
        raise


async def send_checkout_notification(email: str, book_title: str, due_date: str, record_id: int) -> None:
    html = _build_checkout_html(book_title, due_date, record_id)
    await send_email(email, f"Checkout: {book_title}", html)


async def send_return_notification(email: str, book_title: str, fine_amount: float, record_id: int) -> None:
    html = _build_return_html(book_title, fine_amount, record_id)
    await send_email(email, f"Return: {book_title}", html)
