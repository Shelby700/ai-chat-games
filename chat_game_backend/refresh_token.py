import requests
import json

# Change these as needed
API_URL = "http://127.0.0.1:8000/auth/login"
USERNAME = "testuser3"
PASSWORD = "123456"

def refresh_token():
    try:
        res = requests.post(
            API_URL,
            headers={"Content-Type": "application/json"},
            data=json.dumps({"username": USERNAME, "password": PASSWORD})
        )
        if res.status_code == 200:
            token = res.json()["token"]
            with open("token.txt", "w") as f:
                f.write(token)
            print(f"✅ Token refreshed and saved to token.txt")
        else:
            print(f"❌ Failed to refresh token: {res.status_code} {res.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    refresh_token()
