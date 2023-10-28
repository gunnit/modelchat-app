import os
import json
import openai
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory

from telegram import Bot, Update
from telegram.ext import Updater
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from asgiref.sync import async_to_sync

from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv()) # read local .env file


bot = Bot(token=os.environ['TELEGRAM_BOT_TOKEN'])
WEBHOOK_URL = 'https://0c5f-146-241-36-184.ngrok-free.app/telegram_webhook/'
# This function will be synchronous
def set_telegram_webhook():
    async_to_sync(bot.set_webhook)(url=WEBHOOK_URL)


# Set the API key

openai.api_key = os.environ['OPENAI_API_KEY']


llm_model ="gpt-3.5-turbo"
llm = ChatOpenAI(temperature=0.0, model=llm_model)
memory = ConversationBufferMemory()
conversation = ConversationChain(llm=llm, memory=memory, verbose=True)
system_message = "You are Sara, an AI assistant who works in the fashion industry."


# Create your views here.

def home(request): 


    return render(request, 'chat/home.html')

# Decorate the view to exempt it from CSRF protection
@csrf_exempt
def process_message(request):
    if request.method == 'POST':
        # Parse the JSON data from the request body
        data = json.loads(request.body.decode('utf-8'))
        user_message = data.get('message')
        print(user_message)

        # Prepend the system message to set the context
        full_message = system_message + " " + user_message

        try:
            # Use the conversation chain to process the user's message
            response = conversation.predict(input=full_message)
            
            # Extract the assistant's response from the conversation
            print(type(response), response)
            gpt_response = response
            print(gpt_response)

            return JsonResponse({'message': gpt_response})

        except Exception as e:
            print("Error:", e)  # Debug print
            return JsonResponse({'message': 'An error occurred: ' + str(e)})

    return JsonResponse({'message': 'Invalid request'})


@csrf_exempt
def telegram_webhook(request):
    if request.method == "POST":
        json_str = request.body.decode('UTF-8')
        update = Update.de_json(json.loads(json_str), bot)
        message_text = update.message.text
        
        # Prepend the system message to set the context
        full_message = system_message + " " + message_text
        print("Received message from Telegram:", message_text)
        try:
            # Use the conversation chain to process the user's message
            response = conversation.predict(input=full_message)
            
            # Extract the assistant's response from the conversation
            gpt_response = response
            async_to_sync(bot.send_message)(chat_id=update.message.chat_id, text=gpt_response)

        except Exception as e:
            print("Error:", e)  # Debug print
            async_to_sync(bot.send_message)(chat_id=update.message.chat_id, text="Sorry, I couldn't process that.")

    return JsonResponse({})




