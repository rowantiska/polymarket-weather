import requests

def webhook(message):
    payload = { "text": message }
    response = requests.post("https://hooks.slack.com/services/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", json=payload)
    if response.status_code == 200:
        return
    else:
        print(f"Error: {response.status_code}")