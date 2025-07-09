# test_env.py
from dotenv import load_dotenv
import os

# Load variables from the .env file in the current directory
load_dotenv()

# Print the variables to see if they were loaded
print("Attempting to read .env file...")
print("Email Address found:", os.getenv("EMAIL_ADDRESS"))
print("Email Password found:", os.getenv("EMAIL_PASSWORD"))