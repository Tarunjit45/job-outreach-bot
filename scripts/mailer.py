"""
Sends the outreach email with resume attached, via the SMTP server
configured in config.yaml (defaults to Yahoo).
Requires env var EMAIL_APP_PASSWORD.
"""
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication


def send_outreach_email(to_email: str, company: str, config: dict) -> None:
    sender = config["sender_email"]
    password = os.environ["EMAIL_APP_PASSWORD"]
    smtp_host = config.get("smtp_host", "smtp.mail.yahoo.com")
    smtp_port = int(config.get("smtp_port", 465))

    subject = config["email_subject"]
    body = config["email_body"]

    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    resume_path = config["resume_path"]
    if os.path.exists(resume_path):
        with open(resume_path, "rb") as f:
            part = MIMEApplication(f.read(), Name=os.path.basename(resume_path))
        part["Content-Disposition"] = f'attachment; filename="{os.path.basename(resume_path)}"'
        msg.attach(part)
    else:
        print(f"  [warn] resume not found at {resume_path} — sending without attachment")

    with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
        server.login(sender, password)
        server.sendmail(sender, to_email, msg.as_string())
