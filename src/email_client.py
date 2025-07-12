import imaplib
import smtplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from .config import IMAP_SERVER, SMTP_SERVER, SMTP_PORT, EMAIL_ADDRESS, EMAIL_PASSWORD

def connect_to_inbox():
    """Connects to the email inbox via IMAP."""
    try:
        print(f"Connecting to inbox at {IMAP_SERVER}...")
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        mail.select("inbox")
        print("Successfully connected to inbox.")
        return mail
    except Exception as e:
        print(f"Error connecting to inbox: {e}")
        return None

def fetch_unread_emails(mail: imaplib.IMAP4_SSL):
    """Fetching emails with a customer support queries"""
    search_criteria = 'SUBJECT "Test Customer Support Email"'
    print(f"Fetching emails with subject: '{search_criteria}'...'")

    try:
        status, messages = mail.search(None, search_criteria)

        if status != "OK" or not messages[0]:
            return []
        
        email_ids = messages[0].split()
        emails = []
        for email_id in email_ids:
            # After seeing email we will flag it as seen
            mail.store(email_id, '+FLAGS', '\\Seen')

            status, msg_data = mail.fetch(email_id, "(RFC822)")
            if status == "OK":
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        emails.append(msg)
        print(f"Fetched {len(emails)} new email(s) matching the criteria.")
        return emails
    
    except Exception as e:
        print(f"Error fetching emails: {e}")
        return []

def send_email(to_address: str, subject: str, body: str):
    """Sends an email using SMTP."""
    print(f"Sending  response email to {to_address}...")
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = to_address
        msg['Subject'] = "Re: " + subject
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        print("Response email sent successfully.")
    except Exception as e:
        print(f"Error sending email: {e}")

def get_email_body(msg: email.message.Message) -> str:
    """Extracts the plain text body from an email message."""
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            ctype = part.get_content_type()
            cdispo = str(part.get('Content-Disposition'))
            if ctype == 'text/plain' and 'attachment' not in cdispo:
                body = part.get_payload(decode=True).decode(errors='ignore')
                break
    else:
        body = msg.get_payload(decode=True).decode(errors='ignore')
    return body
