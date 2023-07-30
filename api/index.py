import slack
import os
from dotenv import load_dotenv
from flask import Flask, request, Response
from slackeventsapi import SlackEventAdapter
import requests

app = Flask(__name__)
load_dotenv()

client = slack.WebClient(
    token=os.environ["SLACK_BOT_TOKEN"]
)

slack_event_adapter = SlackEventAdapter(
    os.environ["SLACK_SIGNING_SECRET"],
    '/slack/events',
    app
)

valid_channels = [
    os.environ['BOT_TESTING_CHANNEL'],
    os.environ['CAT_FACT_CHANNEL']
]

BOT_ID = client.api_call("auth.test")["user_id"]

@app.route('/health')
def health():
    return {"health": os.environ["ENV_TEST"]}

@app.route('/slack/events', methods=['POST'])
def handle_challenge():
    print(request)
    return {"challenge": request.json()['challenge']}

@app.route('/catfact', methods=['POST'])
def get_cat_fact():
    response = requests.get('https://catfact.ninja/fact')
    data = request.form
    channel_id = data.get('channel_id')

    if channel_id not in valid_channels:
        return

    if response.status_code != 200:
        client.chat_postMessage(
            channel=channel_id, text="Failed to get catfact!")
        return Response, 500
    


    client.chat_postMessage(
        channel=channel_id, 
        text=response.json()["fact"]
    )
    return Response(), 200

# @slack_event_adapter.on('app_mention')
# def app_mention(payload):
#     event = payload.get('event', {})
#     channel_id = event.get('channel')
#     user_id = event.get('user_id')
#     if channel_id not in valid_channels:
#         return
    
#     text = event.get('text')

#     if BOT_ID != user_id: 
#         client.chat_postMessage(channel=channel_id, text=text)

if __name__ == "__main__":
    app.run(debug=True)