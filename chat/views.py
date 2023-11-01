import os
import json
import openai
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db.models import Q

from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory


import telegram
from telegram import Bot, Update
from telegram.ext import Updater
from time import sleep
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from asgiref.sync import async_to_sync
from telegram.request._baserequest import BaseRequest

from .forms import UpdateProfileForm, UpdateDigitalPersonaForm
from .models import ChatMessage, CustomUser, Conversation

from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv()) # read local .env file
# Set the API key
openai.api_key = os.environ['OPENAI_API_KEY']



bot = Bot(token=os.environ['TELEGRAM_BOT_TOKEN'])
# Adjust the connection pool size
BaseRequest.CON_POOL_SIZE = 10  # Set the desired pool size
WEBHOOK_URL = 'https://modelchat-app-047e22be030b.herokuapp.com/telegram_webhook/'
# This function will be synchronous
def set_telegram_webhook():
    async_to_sync(bot.set_webhook)(url=WEBHOOK_URL)


llm_model ="gpt-3.5-turbo"
llm = ChatOpenAI(temperature=0.0, model=llm_model)
memory = ConversationBufferMemory()

persona = "You are Sara, a friendly and upbeat personality known for her roles in adult films. Engage in light-hearted and respectful conversations. Avoid discussing explicit details and handle inappropriate requests gracefully."
system_message = f"System: {persona}"
system_message = "You are chatting with Sara, a popular adult movie star. She's here to engage in friendly conversations. How can she assist you today?"

conversation = ConversationChain(llm=llm, memory=memory, verbose=True)

def generate_prompt(user_message, previous_responses=None):
    base_prompt = f"System: {persona}"
    if previous_responses:
        conversation_history = "\n".join(previous_responses)
        return f"{base_prompt}\n{conversation_history}\nUser: {user_message}\nSara: "
    else:
        return f"{base_prompt}\nUser: {user_message}\nSara: "


# Create your views here.

def home(request):
    # Get the last 20 messages involving the logged-in user (both sent and received)
    messages = ChatMessage.objects.filter(Q(sender=request.user) | Q(receiver=request.user)).order_by('timestamp')[:20]
    return render(request, 'chat/home.html', {'messages': messages})

# Decorate the view to exempt it from CSRF protection
@csrf_exempt
def process_message(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        user_message_content = data.get('message')
        sender_user = request.user
        ai_user, created = CustomUser.objects.get_or_create(username='AI_Bot')

        user_message = ChatMessage(
            sender=sender_user,
            receiver=ai_user,
            content=user_message_content,
        )
        user_message.save()

        # Get previous messages for context (assuming a maximum of 5 for this example)
        previous_messages = ChatMessage.objects.filter(Q(sender=request.user) | Q(receiver=request.user)).order_by('-timestamp')[:5]
        previous_responses = [f"User: {msg.content}" if msg.sender == request.user else f"Sara: {msg.content}" for msg in previous_messages]

        prompt = generate_prompt(user_message_content, previous_responses)

        try:
            ai_response_content = conversation.predict(input=prompt)
            sara_emoji = "💋"
            response = f"{sara_emoji} {ai_response_content}"
            
            ai_response = ChatMessage(
                sender=ai_user,
                receiver=sender_user,
                content=ai_response_content,
            )
            ai_response.save()

            return JsonResponse({'message': response})

        except Exception as e:
            print("Error:", e)
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
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Use the conversation chain to process the user's message                
                response = conversation.predict(input=full_message)
                
                # Extract the assistant's response from the conversation
                gpt_response = response
                async_to_sync(bot.send_message)(chat_id=update.message.chat_id, text=gpt_response)
                break  # If successful, break out of the loop

            except telegram.error.TimedOut:
                if attempt < max_retries - 1:  # Don't sleep on the last attempt
                    sleep(2)  # Wait for 2 seconds before retrying
                else:
                    print("Error: Max retries reached. Failed to send message to Telegram.")
                    async_to_sync(bot.send_message)(chat_id=update.message.chat_id, text="Sorry, I couldn't process that.")
            except Exception as e:
                print("Error:", e)  # Debug print
                async_to_sync(bot.send_message)(chat_id=update.message.chat_id, text="Sorry, I couldn't process that.")
                break  # If it's not a timeout error, break out of the loop

    return JsonResponse({})

def after_login_redirect(request):
    if request.user.user_type == 'MODEL':
        return HttpResponseRedirect(reverse('model_dashboard'))
    else:
        return HttpResponseRedirect(reverse('fan_dashboard'))

@login_required
def model_dashboard(request):
    if request.user.user_type != 'MODEL':
        return redirect('fan_dashboard')  # Redirect to fan dashboard if not a model
    return render(request, 'chat/model_dashboard.html')

@login_required
def fan_dashboard(request):

    model_user = CustomUser.objects.filter(user_type='MODEL')
    print(model_user.count())

    if request.user.user_type != 'FAN':
        return redirect('model_dashboard')  # Redirect to model dashboard if not a fan
    return render(request, 'chat/fan_dashboard.html', {'model_users': model_user})


def update_profile(request):
    if request.method == 'POST':
        form = UpdateProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect(reverse('home'))
    else:
        form = UpdateProfileForm(instance=request.user)
    return render(request, 'chat/update_profile.html', {'form': form})


def update_digital_persona(request):
    if request.method == 'POST':
        form = UpdateDigitalPersonaForm(request.POST, instance=request.user.digital_persona)
        if form.is_valid():
            digital_persona = form.save(commit=False)
            digital_persona.ai_response_tuning = {
                'response_speed': form.cleaned_data['response_speed'],
                'response_length': form.cleaned_data['response_length'],
                'response_style': form.cleaned_data['response_style'],
            }
            digital_persona.save()
            return redirect(reverse('home'))  # Redirect to the home view
    else:
        form = UpdateDigitalPersonaForm(instance=request.user.digital_persona)
    return render(request, 'chat/update_digital_persona.html', {'form': form})

def landing_page(request):
    if request.user.is_authenticated:
        return redirect('home')  # Redirect to home if user is already authenticated
    return render(request, 'chat/landing.html')

def how_it_works(request):
    return render(request, 'chat/how_it_works.html')

@login_required
def chat_with_model(request, model_username):
    model_user = CustomUser.objects.get(username=model_username, user_type='MODEL')
    fan = request.user

    # Get or create the conversation between the fan and the model
    conversation, created = Conversation.objects.get_or_create(fan=fan, model=model_user)

    # Get the last 20 messages for this conversation
    messages = ChatMessage.objects.filter(conversation=conversation).order_by('timestamp')[:20]

    context = {
        'model_user': model_user,
        'messages': messages,
    }
    return render(request, 'chat/chat_with_model.html', context)
#473467
