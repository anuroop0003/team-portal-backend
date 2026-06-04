import pytest
from unittest.mock import MagicMock, patch
from src.mail.service import send_email, send_verification_mail, send_password_reset_mail, send_invitation_mail
from src.mail.exceptions import MailSendError
from src.mail.config import mail_config


@patch("smtplib.SMTP")
def test_send_email_success(mock_smtp_class):
    """
    Test that send_email successfully connects to SMTP and calls send_message.
    """
    
    mock_smtp_instance = MagicMock()
    mock_smtp_class.return_value.__enter__.return_value = mock_smtp_instance

    # Ensure config has dummy values
    mail_config.SMTP_SENDER_EMAIL = "test_user@example.com"
    mail_config.SMTP_APP_PASSWORD = "test_password"
    mail_config.SMTP_HOST = "localhost"
    mail_config.SMTP_PORT = 2525

    send_email(
        to_email="receiver@example.com",
        subject="Test Subject",
        html_content="<p>Test HTML</p>",
        text_content="Test Text"
    )

    # Verify connect, login, send_message
    mock_smtp_class.assert_called_once_with("localhost", 2525)
    mock_smtp_instance.login.assert_called_once_with("test_user@example.com", "test_password")
    mock_smtp_instance.send_message.assert_called_once()
    args, kwargs = mock_smtp_instance.send_message.call_args
    sent_msg = args[0]
    assert sent_msg["Subject"] == "Test Subject"
    assert sent_msg["To"] == "receiver@example.com"


@patch("smtplib.SMTP")
def test_send_email_smtp_failure(mock_smtp_class):
    """
    Test that send_email correctly raises MailSendError on SMTP connection failure.
    """
    mock_smtp_class.side_effect = Exception("SMTP Error")

    mail_config.SMTP_SENDER_EMAIL = "test_user@example.com"
    mail_config.SMTP_APP_PASSWORD = "test_password"

    with pytest.raises(MailSendError) as exc_info:
        send_email(
            to_email="receiver@example.com",
            subject="Test Subject",
            html_content="<p>Test HTML</p>"
        )

    assert "Failed to send email to receiver@example.com" in str(exc_info.value.detail)


@patch("src.mail.service.send_email")
@pytest.mark.anyio
async def test_send_verification_mail(mock_send_email):
    """
    Test send_verification_mail calls send_email with correctly structured content.
    """
    await send_verification_mail("test@example.com", "http://verify-link")
    mock_send_email.assert_called_once()
    args, kwargs = mock_send_email.call_args
    assert args[0] == "test@example.com"
    assert args[1] == "Verify your email address"
    assert "http://verify-link" in args[2]


@patch("src.mail.service.send_email")
@pytest.mark.anyio
async def test_send_password_reset_mail(mock_send_email):
    """
    Test send_password_reset_mail calls send_email with correctly structured content.
    """
    await send_password_reset_mail("test@example.com", "http://reset-link")
    mock_send_email.assert_called_once()
    args, kwargs = mock_send_email.call_args
    assert args[0] == "test@example.com"
    assert args[1] == "Reset your password"
    assert "http://reset-link" in args[2]


@patch("src.mail.service.send_email")
@pytest.mark.anyio
async def test_send_invitation_mail(mock_send_email):
    """
    Test send_invitation_mail calls send_email with correctly structured content.
    """
    await send_invitation_mail("test@example.com", "http://onboarding-link")
    mock_send_email.assert_called_once()
    args, kwargs = mock_send_email.call_args
    assert args[0] == "test@example.com"
    assert "invited to join" in args[1]
    assert "http://onboarding-link" in args[2]
