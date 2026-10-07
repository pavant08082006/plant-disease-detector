"""
Email Dispatcher Service for Agricultural Reports.
Uses SMTP TLS protocol to send PDF diagnostic test reports directly to farmers.
Host Sender: Lokeshmmankith@gmail.com
"""

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from typing import Tuple, Optional
from dotenv import load_dotenv

from backend.utils.helpers import get_logger

load_dotenv()
logger = get_logger("EmailService")


def get_smtp_config():
    """Retrieves and sanitizes SMTP configuration from environment."""
    host = os.getenv("SMTP_HOST", "smtp.gmail.com").strip()
    port = int(os.getenv("SMTP_PORT", "587"))
    user = os.getenv("SMTP_USER", "Lokeshmmankith@gmail.com").strip()
    raw_pwd = os.getenv("SMTP_PASSWORD", "")
    password = raw_pwd.replace(" ", "").strip()
    return host, port, user, password


def send_report_email(
    recipient_email: str,
    subject: str,
    body_text: str,
    pdf_bytes: bytes,
    filename: str = "Smart_Agri_Partner_Report.pdf",
    farmer_name: str = "Farmer"
) -> Tuple[bool, str]:
    """
    Sends a dedicated PDF disease diagnostic test report to the recipient's email address.
    Returns (success: bool, status_message: str).
    """
    host, port, user, password = get_smtp_config()

    if not user or not password:
        err_msg = "SMTP sender email or password not configured in environment."
        logger.error(err_msg)
        return False, err_msg

    recipient_email = recipient_email.strip()
    if not recipient_email or "@" not in recipient_email:
        return False, "Please provide a valid recipient email address."

    try:
        # Build MIME Message
        msg = MIMEMultipart("mixed")
        msg["From"] = f"Smart Agri-Partner <{user}>"
        msg["To"] = recipient_email
        msg["Reply-To"] = user
        msg["Subject"] = subject

        # HTML Body
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; color: #333333; line-height: 1.6; max-width: 620px; margin: 0 auto; padding: 20px;">
            <div style="background-color: #1b5e20; color: #ffffff; padding: 18px 24px; border-radius: 8px 8px 0 0; text-align: center;">
                <h2 style="margin: 0; font-size: 22px;">🌾 Smart Agri-Partner</h2>
                <p style="margin: 5px 0 0 0; font-size: 14px; opacity: 0.9;">AI-Powered Smart Agriculture Assistant</p>
            </div>
            
            <div style="border: 1px solid #e0e0e0; border-top: none; padding: 24px; border-radius: 0 0 8px 8px; background-color: #fafafa;">
                <p style="font-size: 16px;">Dear <b>{farmer_name}</b>,</p>
                <p>{body_text}</p>
                
                <div style="background-color: #e8f5e9; border-left: 4px solid #2e7d32; padding: 14px 18px; margin: 20px 0; border-radius: 4px;">
                    <p style="margin: 0; font-weight: bold; color: #1b5e20; font-size: 15px;">📄 Diagnostic Test Report Attached ({filename})</p>
                    <p style="margin: 6px 0 0 0; font-size: 13px; color: #424242;">
                        Your verified crop leaf disease diagnostic test report is attached to this email. 
                        It details the diagnosed pathogen, model certainty percentage, observed symptoms, 
                        and recommended non-chemical IPM field management guidelines.
                    </p>
                </div>
                
                <p style="font-size: 12px; color: #757575; border-top: 1px solid #e0e0e0; padding-top: 15px; margin-top: 25px;">
                    🛡️ <b>Agricultural Safety Advisory:</b> Recommendations in this report are for Integrated Pest Management (IPM) 
                    and cultural guidance. Consult your local Krishi Vigyan Kendra (KVK) specialist before applying any chemical products.
                </p>
                <p style="font-size: 12px; color: #9e9e9e; text-align: center; margin-top: 15px;">
                    Sent automatically by Smart Agri-Partner Platform via {user}
                </p>
            </div>
        </body>
        </html>
        """
        msg.attach(MIMEText(html_content, "html"))

        # Attach PDF
        if pdf_bytes:
            part = MIMEApplication(pdf_bytes, _subtype="pdf")
            part.add_header("Content-Disposition", "attachment", filename=filename)
            msg.attach(part)

        # Connect and Send via TLS
        logger.info(f"Connecting to SMTP server {host}:{port}...")
        with smtplib.SMTP(host, port, timeout=25) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(user, password)
            server.sendmail(user, [recipient_email], msg.as_string())

        logger.info(f"Successfully sent report email to {recipient_email}")
        return True, f"Diagnostic report successfully dispatched to {recipient_email}!"

    except smtplib.SMTPAuthenticationError as e:
        err_msg = f"SMTP Authentication failed: Check sender email and app password. ({e})"
        logger.error(err_msg)
        return False, err_msg
    except Exception as e:
        err_msg = f"Failed to send email: {str(e)}"
        logger.error(err_msg)
        return False, err_msg
