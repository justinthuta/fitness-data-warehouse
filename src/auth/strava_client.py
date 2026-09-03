import os
import json
import time
import requests
from dotenv import load_dotenv

load_dotenv('config/.env')

CLIENT_ID = os.getenv('STRAVA_CLIENT_ID')
CLIENT_SECRET = os.getenv('STRAVA_CLIENT_SECRET')
TOKEN_FILE = 'config/strava_tokens.json'

def load_tokens():
    """Load saved tokens from local file"""
    with open(TOKEN_FILE, 'r') as f:
        return json.load(f)

def save_tokens(token_data):
    """Save updated tokens back to local file"""
    with open(TOKEN_FILE, 'w') as f:
        json.dump(token_data, f, indent=2)

def get_valid_access_token():
    """
    Returns a valid access token, refreshing it automatically if expired.
    This is the function other parts of the pipeline will call.
    """
    tokens = load_tokens()
    
    # Check if current token is still valid (with 5 min buffer)
    if tokens['expires_at'] > time.time() + 300:
        return tokens['access_token']
    
    # Token expired or about to expire - refresh it
    print("Access token expired, refreshing...")
    response = requests.post(
        url='https://www.strava.com/oauth/token',
        data={
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'grant_type': 'refresh_token',
            'refresh_token': tokens['refresh_token']
        }
    )
    
    if response.status_code == 200:
        new_tokens = response.json()
        save_tokens(new_tokens)
        print("Token refreshed successfully!")
        return new_tokens['access_token']
    else:
        raise Exception(f"Failed to refresh token: {response.text}")

if __name__ == "__main__":
    token = get_valid_access_token()
    print(f"Valid access token obtained (length: {len(token)} chars)")
