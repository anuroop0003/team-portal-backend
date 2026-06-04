import smtplib
import logging
from email.message import EmailMessage
from typing import Optional

from src.config import settings
from src.mail.config import mail_config
from src.mail.exceptions import MailSendError

logger = logging.getLogger(__name__)


def send_email(
    to_email: str,
    subject: str,
    html_content: str,
    text_content: Optional[str] = None,
) -> None:
    """
    Sends an email using standard smtplib and EmailMessage formats.

    Args:
        to_email (str): Recipient email address.
        subject (str): Email subject.
        html_content (str): Rich HTML email body.
        text_content (str, optional): Plain text fallback body.

    Raises:
        MailSendError: If sending email fails.
    """

    if not mail_config.SMTP_SENDER_EMAIL or not mail_config.SMTP_APP_PASSWORD:
        logger.warning(
            "SMTP credentials not configured. Skipping email sending. Logged content:\n"
            f"To: {to_email}\nSubject: {subject}\nBody: {html_content}"
        )
        return

    msg = EmailMessage()

    msg["Subject"] = subject
    msg["From"] = f"{mail_config.SMTP_FROM_NAME} <{mail_config.SMTP_SENDER_EMAIL}>"
    msg["To"] = to_email

    if text_content:
        msg.set_content(text_content)

    else:
        msg.set_content(
            "Please use an HTML-compatible email client to read this message."
        )

    msg.add_alternative(html_content, subtype="html")

    try:
        with smtplib.SMTP(mail_config.SMTP_HOST, mail_config.SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(mail_config.SMTP_SENDER_EMAIL, mail_config.SMTP_APP_PASSWORD)
            server.send_message(msg)
            logger.info(
                f"Email successfully sent to {to_email} with subject: '{subject}'"
            )

    except Exception as e:
        logger.error(f"Error sending SMTP email to {to_email}: {e}")
        raise MailSendError(detail=f"Failed to send email to {to_email}: {str(e)}")


def _get_base_template(title: str, preheader: str, body_html: str) -> str:
    """
    Returns a responsive, premium HTML email wrapper with clean, modern layout.
    """

    return f"""<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
    <title>{title}</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
        body {{
            background-color: #f8fafc;
            font-family: 'Outfit', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            -webkit-font-smoothing: antialiased;
            font-size: 16px;
            line-height: 1.6;
            margin: 0;
            padding: 0;
            -ms-text-size-adjust: 100%;
            -webkit-text-size-adjust: 100%;
        }}
        .wrapper {{
            width: 100%;
            background-color: #f8fafc;
            padding: 40px 0;
        }}
        .container {{
            max-width: 580px;
            margin: 0 auto;
            padding: 10px;
            width: 580px;
        }}
        .content {{
            box-sizing: border-box;
            display: block;
            margin: 0 auto;
            max-width: 580px;
            padding: 10px;
        }}
        .card {{
            background: #ffffff;
            border-radius: 16px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
            padding: 40px;
            border: 1px solid #e2e8f0;
        }}
        .logo-area {{
            text-align: center;
            margin-bottom: 30px;
        }}
        .logo-text {{
            font-weight: 700;
            font-size: 24px;
            color: #4f46e5;
            display: inline-block;
        }}
        h1 {{
            color: #0f172a;
            font-size: 24px;
            font-weight: 700;
            line-height: 1.3;
            margin: 0 0 20px 0;
            text-align: center;
        }}
        p {{
            color: #475569;
            margin: 0 0 20px 0;
            font-size: 16px;
        }}
        .btn-container {{
            text-align: center;
            margin: 30px 0;
        }}
        .btn-primary {{
            background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
            border: none;
            border-radius: 8px;
            color: #ffffff !important;
            display: inline-block;
            font-weight: 600;
            padding: 14px 30px;
            text-decoration: none;
            box-shadow: 0 4px 12px rgba(79, 70, 229, 0.2);
            transition: all 0.3s ease;
        }}
        .footer {{
            clear: both;
            margin-top: 30px;
            text-align: center;
            width: 100%;
        }}
        .footer p {{
            color: #94a3b8;
            font-size: 12px;
            margin-bottom: 8px;
        }}
        .preheader {{
            color: transparent;
            display: none;
            height: 0;
            max-height: 0;
            max-width: 0;
            opacity: 0;
            overflow: hidden;
            mso-hide: all;
            visibility: hidden;
            width: 0;
        }}
    </style>
</head>
<body>
    <span class="preheader">{preheader}</span>
    <div class="wrapper">
        <div class="container">
            <div class="content">
                <div class="card">
                    <div class="logo-area">
                        <span class="logo-text">{mail_config.SMTP_FROM_NAME}</span>
                    </div>
                    {body_html}
                </div>
                <div class="footer">
                    <p>&copy; {mail_config.SMTP_FROM_NAME}. All rights reserved.</p>
                    <p>If you have any questions, contact us at <a href="mailto:{settings.SUPPORT_EMAIL}" style="color: #6366f1; text-decoration: none;">{settings.SUPPORT_EMAIL}</a>.</p>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""


async def send_verification_mail(email: str, verification_link: str) -> None:
    """
    Sends the verification email to the user.

    Args:
        email (str): Recipient email address.
        verification_link (str): The email verification URL.
    """

    subject = "Verify your email address"

    body_html = f"""
    <h1>Confirm Your Email Address</h1>
    <p>Welcome to {mail_config.SMTP_FROM_NAME}! To complete your registration and secure your account, please verify your email address by clicking the button below.</p>
    <div class="btn-container">
        <a href="{verification_link}" class="btn-primary" target="_blank">Verify Email Address</a>
    </div>
    <p>This verif
    ication link will expire in 24 hours. If you did not sign up for {mail_config.SMTP_FROM_NAME}, you can safely ignore this email.</p>
    """
    html = _get_base_template(
        subject,
        "Please verify your email address to continue setting up your account.",
        body_html,
    )

    send_email(email, subject, html)


async def send_password_reset_mail(email: str, reset_link: str) -> None:
    """
    Sends the password reset email to the user.

    Args:
        email (str): Recipient email address.
        reset_link (str): The password reset URL.
    """

    subject = "Reset your password"

    body_html = f"""
    <h1>Password Reset Request</h1>
    <p>We received a request to reset the password for your account. Click the button below to choose a new password.</p>
    <div class="btn-container">
        <a href="{reset_link}" class="btn-primary" target="_blank">Reset Password</a>
    </div>
    <p>This password reset link is valid for 1 hour. If you did not request a password reset, no further action is required.</p>
    """

    html = _get_base_template(subject, "Reset your password link.", body_html)

    send_email(email, subject, html)


async def send_invitation_mail(email: str, onboarding_link: str) -> None:
    """
    Sends an invitation email for user onboarding.

    Args:
        email (str): Recipient email address.
        onboarding_link (str): The onboarding URL.
    """

    subject = f"You are invited to join {mail_config.SMTP_FROM_NAME}"

    body_html = f"""
    <h1>Join Your Team</h1>
    <p>You have been invited to join your team portal on {mail_config.SMTP_FROM_NAME}. Get started and join your colleagues by setting up your profile.</p>
    <div class="btn-container">
        <a href="{onboarding_link}" class="btn-primary" target="_blank">Accept Invitation</a>
    </div>
    <p>Click the button above to activate your account and complete your profile setup.</p>
    """

    html = _get_base_template(subject, "Join your team portal.", body_html)

    send_email(email, subject, html)
