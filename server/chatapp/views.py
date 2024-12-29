from django.shortcuts import render, HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
import json
from bson.objectid import ObjectId
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import hashlib
from datetime import datetime
import jwt
import re
from datetime import timedelta
from pymongo import MongoClient
from gridfs import GridFS
from dotenv import load_dotenv
from groq import Groq
from httpx import Client
http_client = Client()
# Load .env file
load_dotenv()

mongo_uri = os.environ.get("MONGO_URI")
client = MongoClient(mongo_uri)
db = client['ChatApp']          # Database name
user_collection = db['users'] 
chat_bots_collection = db['chat_bots']
user_bots_collection = db['user_bots']
user_chats_collection = db['user_chats']
fs = GridFS(db)

# Create your views here.

def index(request):
    # return HttpResponse("Hello There!")
    context ={
        "variable":"Hello world"
    }
    return HttpResponse("<h1>Hello!! Server is working.<h1>")









api_key = os.environ.get("GROQ_API_KEY")
# print("api_key: ",api_key)
if not api_key:
    print("GROQ_API_KEY is missing")
# try:


def groq_res(prompt):
    try:
        client = Groq(
            api_key=os.environ.get("GROQ_API_KEY"),
            http_client=http_client
        )
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "user", "content": prompt},
            ],
            model="llama-3.1-70b-versatile",
            response_format={"type": "json_object"},
        )
        res = chat_completion.choices[0].message.content.strip()
        return res
    except Exception as e:
        error_message = str(e)  # Convert the error to a string
        print(f"Error occurred: {error_message}")
        # Ensure the returned error message is serializable
        return json.dumps({"error": error_message})



@api_view(['POST'])
def groq_api(request):
    # Extract the prompt from the request body
    prompt = request.data.get('prompt')

    if not prompt:
        return Response({"error": "Prompt is required"}, status=400)

    chat_prompt = f'''
You are a personal bot reply to the user queries:
{prompt}


Return a single response in json format
{{
    response:response
}}
'''

    # Call the groq_res function
    result = groq_res(chat_prompt)
    result = json.loads(result)
    print(result)
    result = list(result.values())[0]
    return Response({"response": result})





# Utility functions
def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def is_valid_password(password):
    return re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', password)

def validate_name(name):
    return name.isalpha() and len(name) > 2

def generate_token(user_id):
    secret_key = "your_secret_key"  # Replace with your secret key
    return jwt.encode({"user_id": user_id, "exp": datetime.now() + timedelta(hours=2)}, secret_key, algorithm="HS256")


@csrf_exempt
def signup(request):
    if request.method == "POST":
        try:
            # data = request.POST  # For form data
            data = json.loads(request.body)
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')
            confirm_password = data.get('confirmPassword')
            print(username,email,password,confirm_password)
            # Allowed fields
            allowed_fields = {'username', 'email', 'password', 'confirmPassword'}
            received_fields = set(data.keys())

            # Check for unexpected fields
            if not received_fields.issubset(allowed_fields):
                return JsonResponse({"error": "Invalid fields detected"}, status=400)

            # Validate email and password
            if not is_valid_email(email):
                return JsonResponse({"message": "Invalid email format"}, status=400)
            if not is_valid_password(password):
                return JsonResponse(
                    {"message": "Password must be at least 8 characters long, include an uppercase letter, lowercase letter, number, and special character"},
                    status=400
                )
            if password != confirm_password:
                return JsonResponse({"message": "Passwords do not match"}, status=400)
            if not validate_name(username):
                return JsonResponse({"message": "Invalid name format"}, status=400)

            # Check if email already exists
            if user_collection.find_one({"email": email}):
                return JsonResponse({"message": "Email already registered"}, status=400)

            # Hash the password
            hashed_password = hashlib.sha256(password.encode()).hexdigest()

            # Create the new user record
            new_user = {
                "username": username,
                "email": email,
                "password": hashed_password,
                "created_at": datetime.now(),
                "profile_photo_url": "https://wallpapercrafter.com/desktop1/636078-Bleach-Ichigo-Kurosaki-Zangetsu-Bleach-1080P.jpg"
            }
            result = user_collection.insert_one(new_user)
            print(result)
            if result.inserted_id:
                # Generate token after successful signup
                access_token, refresh_token = generate_tokens(str(result.inserted_id))
                return JsonResponse({"message": "Signup successful", "user_id": str(result.inserted_id),"token": access_token,"refresh_token": refresh_token, "email": email,"username": username}, status=201)
            else:
                return JsonResponse({"message": "Signup failed"}, status=500)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"message": "Invalid request method"}, status=405)




# Utility function to generate token
# def generate_token(user_id):
#     secret_key = "your_secret_key"  # Replace with your secret key
#     return jwt.encode({"user_id": user_id, "exp": datetime.now() + timedelta(hours=2)}, secret_key, algorithm="HS256")

def generate_tokens(user_id):
    # Generate Access Token (short-lived)
    print("funct working")
    access_token = jwt.encode(
        {
            "user_id": user_id,
            "exp": datetime.now() + timedelta(minutes=15)  # 15 minutes expiry
        },
        "SECRET_KEY",
        algorithm="HS256"
    )
    print(access_token)
    # Generate Refresh Token (long-lived)
    refresh_token = jwt.encode(
        {
            "user_id": user_id,
            "exp": datetime.now() + timedelta(days=7)  # 7 days expiry
        },
        "SECRET_KEY",
        algorithm="HS256"
    )

    return access_token, refresh_token

def refresh_token(request):
    try:
        # data = request.POST
        data = json.loads(request.body)
        refresh_token = data.get('refresh_token')

        # Decode refresh token
        decoded = jwt.decode(refresh_token, "SECRET_KEY", algorithms=["HS256"])
        user_id = decoded['user_id']

        # Generate new access token
        access_token = jwt.encode(
            {"user_id": user_id, "exp": datetime.now() + timedelta(minutes=15)},
            "SECRET_KEY",
            algorithm="HS256"
        )

        return JsonResponse({"token": access_token}, status=200)

    except jwt.ExpiredSignatureError:
        return JsonResponse({"message": "Refresh token expired"}, status=401)
    except jwt.InvalidTokenError:
        return JsonResponse({"message": "Invalid token"}, status=401)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def signin(request):
    if request.method == "POST":
        try:
            # data = request.POST  # For form data
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')
            print(email,password)
            # Allowed fields
            allowed_fields = {'email', 'password'}
            received_fields = set(data.keys())

            # Check for unexpected fields
            if not received_fields.issubset(allowed_fields):
                return JsonResponse({"error": "Invalid fields detected"}, status=400)
            print("chala??")
            # Find user by email only
            user = user_collection.find_one({"email": email})
            print(user)
            print("chala??")
            if user:
                print("user exists")
                hashed_input_password = hashlib.sha256(password.encode()).hexdigest()
                print("dfs")
                access_token, refresh_token = generate_tokens(str(user['_id']))
                print(access_token, refresh_token)
                # Compare the hashed input password with the stored hashed password
                if hashed_input_password == user['password']:
                    return JsonResponse(
                        {
                            "message": "Logged in successfully.",
                            "token": access_token,
                            "refresh_token": refresh_token,
                            "username": user['username'],
                            "user_id": str(user['_id']),
                            "email": email
                        },
                        status=200
                    )
                else:
                    return JsonResponse({"message": "Invalid login credentials"}, status=400)
            else:
                return JsonResponse({"message": "Invalid login credentials"}, status=400)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"message": "Invalid request method"}, status=405)

from django.shortcuts import redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from oauthlib import oauth2
import requests
import json
import os
from urllib.parse import urlencode
from pymongo import MongoClient
from oauthlib.oauth2 import WebApplicationClient

# Environment setup
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Google OAuth credentials
CLIENT_ID2 = os.environ.get("CLIENT_ID2")
CLIENT_SECRET2 = os.environ.get("CLIENT_SECRET2")

# MongoDB setup
# client = MongoClient(settings.MONGO_URI)
# db = client['socialiq_db']
# collection2 = db['user_data']

# OAuth request data
DATA = {
    'response_type': "code",
    'redirect_uri': "https://chat-persona-ai-ov46.vercel.app/callback_google_trial",
    'scope': 'https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile',
    'client_id': CLIENT_ID2,
    'prompt': 'consent'
}

# URLs for Google OAuth
URL_DICT = {
    'google_oauth': 'https://accounts.google.com/o/oauth2/v2/auth',
    'token_gen': 'https://oauth2.googleapis.com/token',
    'get_user_info': 'https://www.googleapis.com/oauth2/v3/userinfo'
}

# OAuth Client
CLIENT = oauth2.WebApplicationClient(CLIENT_ID2)
REQ_URI = CLIENT.prepare_request_uri(
    uri=URL_DICT['google_oauth'],
    redirect_uri=DATA['redirect_uri'],
    scope=DATA['scope'],
    prompt=DATA['prompt']
)

# Step 1: Google Login (Redirect to Google OAuth)
def google_login(request):
    client = WebApplicationClient(CLIENT_ID2)
    req_uri = client.prepare_request_uri(
        URL_DICT['google_oauth'],
        redirect_uri=DATA['redirect_uri'],
        scope=DATA['scope'],
        prompt=DATA['prompt']
    )
    return redirect(req_uri)

@csrf_exempt
def callback_google_trial(request):
    if request.method == 'OPTIONS':
        return JsonResponse({}, status=200)

    print("callback trial")

    # Get authorization code
    code = request.GET.get('code')
    print("code", code)

    # Redirect URL
    # redirect_url = request.build_absolute_uri()
    redirect_url = request.build_absolute_uri().replace("http://", "https://")
    print("redirect_url", redirect_url)

    # Prepare token request
    token_url, headers, body = CLIENT.prepare_token_request(
        URL_DICT['token_gen'],
        authorization_response=request.build_absolute_uri(),
        redirect_url=DATA['redirect_uri'],
        code=code
    )

    # Generate token
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(CLIENT_ID2, CLIENT_SECRET2)
    )

    CLIENT.parse_request_body_response(json.dumps(token_response.json()))

    # Get user info
    uri, headers, body = CLIENT.add_token(URL_DICT['get_user_info'])
    response_user_info = requests.get(uri, headers=headers, data=body)
    info = response_user_info.json()
    print(f"User Info: {info}")

    # User data
    new_user = {
        'sub': info['sub'],
        'name': info['name'],
        'email': info['email'],
        'picture': info['picture']
    }

    # Check existing user
    existing_user = user_collection.find_one({'email': new_user['email']})

    if existing_user:
        print("User with this email already exists.")
        user_id = str(existing_user['_id'])
    else:
        result = user_collection.insert_one(new_user)
        user_id = str(result.inserted_id)
        print("User data inserted successfully!")

    # Email verification
    if info.get("email_verified"):
        access_token, refresh_token = generate_tokens(user_id)
        # print(token)

        params = {
            "message": "Email verified",
            "name": info['name'],
            "email": info['email'],
            "picture": info['picture'],
            "token": access_token,
            "refresh_token": refresh_token
        }

        # Encode parameters
        encoded_params = urlencode(params)
        print("encoded_params: ", encoded_params)

        # Redirect URL
        redirect_url = f"http://localhost:5173/AuthRedirectPage?{encoded_params}"
        return redirect(redirect_url)
    else:
        return JsonResponse({"message": "Email not verified"}, status=200)


@csrf_exempt
def add_bot(request):
    if request.method == "POST":
        try:
            data = request.POST  # For form data
            bot_name = data.get('bot_name')
            description = data.get('description')
            prompt = data.get('prompt')
            start_message = data.get('start_message')
            image_url = data.get('image_url')

            # Check for required fields
            if not description or not image_url:
                return JsonResponse({"error": "Missing required fields"}, status=400)

            # Create bot document
            new_bot = {
                "bot_name": bot_name,
                "description": description,
                "prompt": prompt,
                "image_url": image_url,
                "start_message": start_message,
                "created_at": datetime.now() 
            }

            # Insert into MongoDB
            result = chat_bots_collection.insert_one(new_bot)

            if result.inserted_id:
                return JsonResponse({"message": "Bot added successfully", "bot_id": str(result.inserted_id)}, status=201)
            else:
                return JsonResponse({"message": "Failed to add bot"}, status=500)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"message": "Invalid request method"}, status=405)


# Get all bots from the database
def get_all_bots(request):
    try:
        bots = list(chat_bots_collection.find())  # Fetch all bots from the collection
        for bot in bots:
            bot['_id'] = str(bot['_id'])  # Convert MongoDB ObjectId to string

        return JsonResponse({"bots": bots}, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# Get a specific bot based on its ID
def get_bot_by_id(request):
    bot_id = request.GET.get('bot_id')  # Get bot_id from query parameter

    if not bot_id:
        return JsonResponse({"error": "Bot ID is required"}, status=400)
    try:
        # Convert the bot_id to ObjectId format for MongoDB query
        bot = chat_bots_collection.find_one({"_id": ObjectId(bot_id)})

        if bot:
            bot['_id'] = str(bot['_id'])  # Convert MongoDB ObjectId to string
            return JsonResponse({"bot": bot}, status=200)
        else:
            return JsonResponse({"message": "Bot not found"}, status=404)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)




@csrf_exempt
def chat_generation(request):
    if request.method == "POST":
        data = request.POST  # For form data
        email = data.get('email')
        user_name = data.get('username')
        bot_id = data.get('bot_id')
        bot_name = data.get('bot_name')
        prompt = data.get('prompt')
        start_message = data.get('start_message')
        last_message = data.get('last_message')
        last_message = user_name + ": " + last_message

        user_chats = db['user_chats'].find_one({"email": email, "bot_id": bot_id})

        if user_chats:
            # If user chat exists, retrieve the dialog and add the last message
            chat_history = user_chats.get("chat_history", [])
            # chat_history_len= len(chat_history)

        else:
            new_user_chat = {
                "email": email,
                "bot_id": bot_id,
                "chat_history": [start_message]  # Initialize chat_history with start_message and last_message
            }
            # Insert the new document into the 'user_chats' collection
            user_chats_collection.insert_one(new_user_chat)
            # return "User chat created with start message and last message."
            chat_history = [start_message]

        chat_history_string = '\n'.join(chat_history)
        chat_prompt = f'''
#Your task is to roleplay given character and reply to user {user_name} based on it and chat history roleplaying as the character.

Character:
'{prompt}'

chat history:
'{chat_history_string}'

last message:
{last_message}

You are {bot_name} and reply accordingly 

The response should be based on last message with a single dialog.

'''

        # Call the groq_res function
        bot_chat = groq_res(chat_prompt)
        bot_chat = json.loads(bot_chat)

        bot_chat = list(bot_chat.values())[0]
        bot_response = {"sender":bot_name,"message":bot_chat}
        bot_chat = bot_name+": "+ bot_chat
        chat_history.append(last_message)
        chat_history.append(bot_chat)

        user_chats_collection.update_one(
            {"email": email, "bot_id": bot_id},
            {"$set": {"chat_history": chat_history}}
        )
        # return Response({"response": bot_chat})
        
        return JsonResponse(bot_response, status=200)


def show_chat(request):
    email = request.GET.get('email')
    bot_id = request.GET.get('bot_id')
    # bot_name = request.GET.get('bot_name')

    user_chats = user_chats_collection.find_one({"email": email, "bot_id": bot_id})

    if user_chats:
        
        chat_history = user_chats.get("chat_history", [])
        processed_chats = []
    
        for chat in chat_history:
            if ": " in chat:
                sender, message = chat.split(": ", 1)
                # sender_type = "user" if sender.lower() == "vijay" else "bot"
                processed_chats.append({"sender": sender, "message": message})
            else:
                # If there's no sender, assume it's a bot message
                processed_chats.append({"sender": "bot", "message": chat})
        print(len(chat_history))
        if len(chat_history)==1:
            return JsonResponse({"chats":processed_chats})

        else:

            return JsonResponse({"chats":processed_chats})
        
    else:

        bot = chat_bots_collection.find_one({"_id": ObjectId(bot_id)})
        if not bot:
            return JsonResponse({"message": f"Bot not found"}, status=404)
        
        start_message = bot.get("start_message")
        bot_name = bot.get("bot_name")
        processed_chats = [{"sender": bot_name, "message": start_message}]
        start_message = bot_name + ": " + start_message

        new_user_chat = {
            "email": email,
            "bot_id": bot_id,
            "chat_history": [start_message]  # Initialize chat_history with start_message and last_message
        }
        # Insert the new document into the 'user_chats' collection
        user_chats_collection.insert_one(new_user_chat)

        return JsonResponse({"chats":processed_chats})



@csrf_exempt
def create_user_bots(request):
    if request.method == "POST":
        data = request.POST  # For form data
        bot_name = data.get('bot_name')
        description = data.get('bot_name')
        prompt = data.get('prompt')
        start_message = data.get('start_message')
        # Handling the uploaded image file
        image_file = request.FILES.get('image_file')
        if image_file:
            # Save the image in GridFS
            file_id = fs.put(image_file, filename=image_file.name)

            # Save the bot details in MongoDB
            bot_data = {
                "bot_name": bot_name,
                "description": description,
                "prompt": prompt,
                "start_message": start_message,
                "image_file_id": str(file_id),  # Convert ObjectId to string for readability
                "image_url": f"https://fun-chat-red.vercel.app/get_image?file_id={str(file_id)}"

            }
            user_bots_collection.insert_one(bot_data)

            return JsonResponse({"message": "Bot created successfully", "bot_id": str(bot_data["_id"])})
        else:
            return JsonResponse({"error": "Image file is required"}, status=400)
        

def get_image(request):
    file_id = request.GET.get('file_id')
    if not file_id:
        return JsonResponse({"error": "file_id is required"}, status=400)

    try:
        # Fetch the image from GridFS
        file_data = fs.get(ObjectId(file_id))
        content_type = file_data.content_type or "application/octet-stream"

        # Return the image as an HTTP response
        return HttpResponse(file_data.read(), content_type=content_type)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

