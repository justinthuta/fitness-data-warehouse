import os
import requests
import json
from dotenv import load_dotenv

load_dotenv('config/.env')

CLIENT_ID = os.getenv('STRAVA_CLIENT_ID')
CLIENT_SECRET = os.getenv('STRAVA_CLIENT_SECRET')

def exchange_code_for_token(auth_code):
    """Exchange the temporary authorization code for access + refresh tokens"""
    response = requests.post(
        url='https://www.strava.com/oauth/token',
        data={
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'code': auth_code,
            'grant_type': 'authorization_code'
        }
    )
    
    if response.status_code == 200:
        token_data = response.json()
        
        # Save tokens to a local file (gitignored) for reuse
        with open('config/strava_tokens.json', 'w') as f:
            json.dump(token_data, f, indent=2)
        
        print("Token exchange successful!")
        print(f"Access token expires at: {token_data['expires_at']}")
        return token_data
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

if __name__ == "__main__":
    code = input("Paste your authorization code here: ")
    exchange_code_for_token(code)
