import json
import openai
from channels.generic.websocket import AsyncWebsocketConsumer

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
        openai.api_key = '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'
        response = openai.Completion.create(engine="davinci", prompt=message, max_tokens=150)
        gpt_response = response.choices[0].text.strip()

        await self.send(text_data=json.dumps({
            'message': gpt_response
        }))
