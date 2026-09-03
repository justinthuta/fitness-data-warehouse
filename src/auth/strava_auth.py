import os
import webbrowser
from dotenv import load_dotenv

load_dotenv('config/.env')

CLIENT_ID = os.getenv('STRAVA_CLIENT_ID')
REDIRECT_URI = 'http://localhost/exchange_token'
SCOPE = 'activity:read_all'

def get_authorization_url():
    """Build the URL that sends the user to Strava's approval page"""
    auth_url = (
        f"https://www.strava.com/oauth/authorize?"
        f"client_id={CLIENT_ID}&"
        f"redirect_uri={REDIRECT_URI}&"
        f"response_type=code&"
        f"approval_prompt=force&"
        f"scope={SCOPE}"
    )
    return auth_url

if __name__ == "__main__":
    url = get_authorization_url()
    print("Opening browser for Strava authorization...")
    print(f"If it doesn't open automatically, visit this URL:\n{url}\n")
    webbrowser.open(url)
