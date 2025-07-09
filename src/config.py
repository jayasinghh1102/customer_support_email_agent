import os

# --- Email Configuration ---
IMAP_SERVER = os.environ.get("IMAP_SERVER")
SMTP_SERVER = os.environ.get("SMTP_SERVER")
SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))

EMAIL_ADDRESS = os.environ.get("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")

# Agent Configuration
CHECK_INTERVAL_SECONDS = int(os.environ.get("CHECK_INTERVAL_SECONDS", 30)) 

# Knowledge Base Configuration
KNOWLEDGE_BASE_DIR = os.environ.get("KNOWLEDGE_BASE_DIR", "knowledge_base")

# Validate config
def validate_config():
    """Checks if essential configuration variables are set."""
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        raise ValueError(
            "EMAIL_ADDRESS and EMAIL_PASSWORD environment variables must be set. "
            "Please export them or set them in a .env file before running the application."
        )
    print("Configuration validated successfully.")

