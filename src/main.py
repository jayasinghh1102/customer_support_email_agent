import sys
import os
import time
# from .llm_integration import slm_handler

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from dotenv import load_dotenv

CUSTOMER_SUPPORT_EMAIL_AGENT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
dotenv_path = os.path.join(CUSTOMER_SUPPORT_EMAIL_AGENT, '.env')

load_dotenv(dotenv_path=dotenv_path)

from src.config import CHECK_INTERVAL_SECONDS, validate_config
from src.email_client import connect_to_inbox, fetch_unread_emails
from src.agent import create_agent_graph
from src.knowledge_base import get_knowledge_base


def main():
    """
    The main function that initializes and runs the agent.
    """
    print("Starting Customer Support Email Agent...")
    
    try:
        validate_config()
    except ValueError as e:
        print(f"Configuration Error: {e}")
        return

    # Initialize the Knowledge Base
    get_knowledge_base()

    # Create the agent graph
    app = create_agent_graph()

    # Connect to the email inbox
    mail = connect_to_inbox()
    if not mail:
        print("Could not connect to inbox. Exiting.")
        return
    
    # Load local model
    

    # 5. Start the main agent loop
    print("\nAgent is running. Press Ctrl+C to stop.")
    try:
        while True:
            unread_emails = fetch_unread_emails(mail)
            
            if not unread_emails:
                print(f"No new emails. Waiting for {CHECK_INTERVAL_SECONDS} seconds...")
            else:
                for msg in unread_emails:
                    email_subject = msg['Subject']
                    email_from = msg['From']
                    print(f"\n{'*'*50}")
                    print(f"Processing New Email from '{email_from}' with Subject: '{email_subject}'")
                    print(f"{'*'*50}")
                    
                    initial_state = {"email_message": msg, "log": []}
                    final_state = app.invoke(initial_state)
                    
                    print("\n Final State Log ")
                    for log_entry in final_state['log']:
                        print(f"- {log_entry}")
                    print(" End of Processing ")

            time.sleep(CHECK_INTERVAL_SECONDS)

    except KeyboardInterrupt:
        print("\nAgent stopped by user.")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
    finally:
        if mail:
            mail.logout()
            print("Logged out and closed email connection.")
        # slm_handler.unload_slm()
        print("Local model unloaded successfully")

if __name__ == "__main__":
    print("--- Agent execution has started ---")
    main()
