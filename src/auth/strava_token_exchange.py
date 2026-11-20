import os
import requests
import json
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv

load_dotenv('config/.env')

CLIENT_ID = os.getenv('STRAVA_CLIENT_ID')
CLIENT_SECRET = os.getenv('STRAVA_CLIENT_SECRET')
TOKEN_FILE = 'config/strava_tokens.json'


def extract_code(user_input):
    """Accept either the bare code or the full redirect URL from the browser address bar"""
    user_input = user_input.strip()
    if user_input.startswith('http'):
        codes = parse_qs(urlparse(user_input).query).get('code')
        return codes[0] if codes else None
    return user_input


def exchange_code_for_token(auth_code):
    """Exchange the temporary authorization code for access + refresh tokens"""
    if not CLIENT_ID or not CLIENT_SECRET:
        print("Missing STRAVA_CLIENT_ID or STRAVA_CLIENT_SECRET in config/.env")
        return None

    response = requests.post(
        url='https://www.strava.com/oauth/token',
        data={
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'code': auth_code,
            'grant_type': 'authorization_code'
        },
        timeout=30
    )

    if response.status_code == 200:
        token_data = response.json()

        # Save tokens to a local file (gitignored) for reuse
        os.makedirs(os.path.dirname(TOKEN_FILE), exist_ok=True)
        with open(TOKEN_FILE, 'w') as f:
            json.dump(token_data, f, indent=2)

        print("Token exchange successful!")
        print(f"Access token expires at: {token_data['expires_at']}")
        return token_data
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None


if __name__ == "__main__":
    raw = input("Paste the code (or the full redirect URL) here: ")
    code = extract_code(raw)
    if not code:
        print("Could not find a code. Copy the 'code=' part from the browser address bar.")
    else:
        exchange_code_for_token(code)
