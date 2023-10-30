import json
import os
import openai
from channels.generic.websocket import AsyncWebsocketConsumer
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv()) # read local .env file
# Set the API key
openai.api_key = os.environ['OPENAI_API_KEY']



class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("Attempting to connect...")
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        print(message)

        # Get response from OpenAI's GPT
        response = openai.Completion.create(engine="davinci", prompt=message, max_tokens=150)
        gpt_response = response.choices[0].text.strip()

        await self.send(text_data=json.dumps({
            'message': gpt_response
        }))
