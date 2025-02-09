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
import shutil
import numpy as np
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import google.generativeai as genai
import os
import json
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS


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
            model="llama-3.3-70b-versatile",
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
            data = request.POST  # For form data
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')
            confirm_password = data.get('confirmPassword')

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

            if result.inserted_id:
                # Generate token after successful signup
                token = generate_token(str(result.inserted_id))
                return JsonResponse({"message": "Signup successful", "user_id": str(result.inserted_id), "token": token, "email": email}, status=201)
            else:
                return JsonResponse({"message": "Signup failed"}, status=500)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"message": "Invalid request method"}, status=405)




# Utility function to generate token
def generate_token(user_id):
    secret_key = "your_secret_key"  # Replace with your secret key
    return jwt.encode({"user_id": user_id, "exp": datetime.now() + timedelta(hours=2)}, secret_key, algorithm="HS256")


@csrf_exempt
def signin(request):
    if request.method == "POST":
        try:
            data = request.POST  # For form data
            email = data.get('email')
            password = data.get('password')

            # Allowed fields
            allowed_fields = {'email', 'password'}
            received_fields = set(data.keys())

            # Check for unexpected fields
            if not received_fields.issubset(allowed_fields):
                return JsonResponse({"error": "Invalid fields detected"}, status=400)

            # Find user by email only
            user = user_collection.find_one({"email": email})

            if user:
                print("user exists")
                hashed_input_password = hashlib.sha256(password.encode()).hexdigest()
                token = generate_token(str(user['_id']))

                # Compare the hashed input password with the stored hashed password
                if hashed_input_password == user['password']:
                    return JsonResponse(
                        {
                            "message": "Logged in successfully.",
                            "token": token,
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



@csrf_exempt
def add_bot(request):
    if request.method == "POST":
        try:
            data = request.POST  # For form data
            bot_name = data.get('bot_name')
            description = data.get('description')
            prompt = data.get('prompt')
            start_message = data.get('start_message')
            # image_url = data.get('image_url')

            # Handling the uploaded image file
            image_file = request.FILES.get('image_file')
            file_id = ""
            image_url = ""
            if image_file:
                # Save the image in GridFS
                print("haaa hai")
                file_id = fs.put(image_file, filename=image_file.name)
            if (file_id != ""):
                image_url = f"https://fun-chat-red.vercel.app/get_image?file_id={str(file_id)}"

            # Check for required fields
            if not description or not prompt or not bot_name:
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

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
# Initialize Google AI Embeddings
embedding_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

# FAISS Directory
FAISS_DIR = "faiss_indexes"
os.makedirs(FAISS_DIR, exist_ok=True)



def get_pdf_text(pdf_docs):
    """Extract text from uploaded PDFs"""
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def get_text_chunks(text):
    """Split large text into smaller chunks for FAISS indexing."""
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    return text_splitter.split_text(text)

def save_faiss_index(vector_store, bot_id):
    """Save FAISS index locally for retrieval."""
    faiss_path = os.path.join(FAISS_DIR, f"{bot_id}.faiss")
    vector_store.save_local(faiss_path)

# from gridfs import GridFS

# Assuming `fs` is initialized as GridFS(db)
import os

def save_faiss_to_mongo(vector_store):
    """Save FAISS index to MongoDB and return the file ID."""
    # Ensure the temporary directory exists
    faiss_temp_dir = '/tmp/faiss_temp/'
    os.makedirs(faiss_temp_dir, exist_ok=True)  # Create the temp directory if it doesn't exist
    
    faiss_temp_file = os.path.join(faiss_temp_dir, 'faiss_index.bin')  # Ensure it's a file, not a directory
    
    # Save FAISS index locally first
    vector_store.save_local(faiss_temp_file)  # Save the FAISS index to the file

    with open(faiss_temp_file, 'rb') as faiss_file:
        # Save the FAISS index to MongoDB GridFS
        file_id = fs.put(faiss_file, filename="faiss_index")
    
    return file_id

import os
import zipfile

def compress_directory(dir_path, zip_path):
    """Compresses the directory at dir_path into a zip file at zip_path."""
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(dir_path):
            for file in files:
                file_path = os.path.join(root, file)
                # Use a relative path inside the zip archive
                arcname = os.path.relpath(file_path, start=dir_path)
                zipf.write(file_path, arcname)


def save_faiss_index(vector_store, bot_id):
    """
    Save the FAISS index locally (as a directory) and also compress it into a ZIP file
    to upload to MongoDB via GridFS. The GridFS file ID is stored in the bot document.
    """
    # Define the local directory where FAISS index is saved
    faiss_dir = os.path.join(FAISS_DIR, f"{bot_id}.faiss")
    # Save the FAISS index locally (this creates a directory with multiple files)
    vector_store.save_local(faiss_dir)
    
    # Compress the FAISS directory into a ZIP file
    zip_path = os.path.join(FAISS_DIR, f"{bot_id}.faiss.zip")
    compress_directory(faiss_dir, zip_path)
    
    # Upload the ZIP file to MongoDB using GridFS

    with open(zip_path, 'rb') as f:
        file_data = f.read()
    file_id = fs.put(file_data, filename=f"{bot_id}.faiss.zip")
    
    # Update the bot document with the FAISS GridFS file ID
    chat_bots_collection.update_one(
        {"_id": ObjectId(bot_id)},
        {"$set": {"faiss_file_id": str(file_id)}}
    )


@csrf_exempt
def add_user_bot(request):
    if request.method == "POST":
        try:
            data = request.POST  # For form data
            email = data.get('email')
            bot_name = data.get('bot_name')
            description = data.get('description')
            
            start_message = data.get('start_message')
            # image_url = data.get('image_url')

            # Handling the uploaded image file
            image_file = request.FILES.get('image_file')
            file_id = ""
            image_url = ""
            if image_file:
                # Save the image in GridFS
                print("haaa hai")
                file_id = fs.put(image_file, filename=image_file.name)
            if (file_id != ""):
                image_url = f"http://127.0.0.1:8000/get_image?file_id={str(file_id)}"

            # Check for required fields
            if not description or not bot_name:
                return JsonResponse({"error": "Missing required fields"}, status=400)

            # Get PDF files (if any)
            pdf_docs = request.FILES.getlist('pdf_files')
            print("pdf_docs hai ye:",pdf_docs)
            text_chunks =''
            if (pdf_docs):
                print("pdf_mila kya")
                try:
                # Extract text from PDFs
                    pdf_text = get_pdf_text(pdf_docs) if pdf_docs else ""
                    combined_text = pdf_text  # Merge all data

                    # Chunk text
                    text_chunks = get_text_chunks(combined_text)
                    
                    # Generate embeddings and save to FAISS
                    vector_store = FAISS.from_texts(text_chunks, embedding=embedding_model)
                    # Save FAISS index to MongoDB and get the file ID
                    # faiss_file_id = save_faiss_to_mongo(vector_store)
                except Exception as e:
                    print(e)
            # Check for required fields
            if not description or not image_url:
                return JsonResponse({"error": "Missing required fields"}, status=400)
            
            prompt = f'''
You are {bot_name} and respond based on description
{description}
            '''
            # Create bot document
            new_bot = {
                "bot_name": bot_name,
                "description": description,
                "prompt": prompt,
                "image_url": image_url,
                "start_message": start_message,
                "created_at": datetime.now(),
                'email':email
            }

            # Insert into MongoDB
            result = chat_bots_collection.insert_one(new_bot)


            
            if result.inserted_id:
                if (pdf_docs):
                    # Save FAISS index
                    save_faiss_index(vector_store, result.inserted_id)
                
                

                return JsonResponse({"message": "Bot added successfully", "bot_id": str(result.inserted_id)}, status=201)
            else:
                return JsonResponse({"message": "Failed to add bot"}, status=500)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"message": "Invalid request method"}, status=405)

@csrf_exempt
def delete_faiss_file_id(request):
    """
    API endpoint to delete the FAISS file from GridFS and locally (if exists),
    and update the bot's file id field to an empty string.
    """
    if request.method == "POST":
        try:
            data = request.POST
            bot_id = data.get("bot_id")
            if not bot_id:
                return JsonResponse({"error": "Missing bot_id"}, status=400)
            
            # Retrieve the bot document using the provided bot_id
            bot_doc = chat_bots_collection.find_one({"_id": ObjectId(bot_id)})
            if not bot_doc:
                return JsonResponse({"error": "Bot not found"}, status=404)
            
            file_id = bot_doc.get("faiss_file_id", "")
            # Delete from GridFS if file_id exists
            if file_id:
            
                try:
                    fs.delete(ObjectId(file_id))
                except Exception as e:
                    # Log error if necessary (the file may already be deleted)
                    print(f"Error deleting file from GridFS: {e}")
            
            # Remove local FAISS directory if it exists
            faiss_dir = os.path.join(FAISS_DIR, f"{bot_id}.faiss")
            if os.path.exists(faiss_dir):
                try:
                    shutil.rmtree(faiss_dir)
                    print(f"Deleted local FAISS directory: {faiss_dir}")
                except Exception as e:
                    print(f"Error deleting local FAISS directory: {e}")
            
            # Remove the local FAISS ZIP file if it exists
            zip_path = os.path.join(FAISS_DIR, f"{bot_id}.faiss.zip")
            if os.path.exists(zip_path):
                try:
                    os.remove(zip_path)
                    print(f"Deleted local FAISS zip file: {zip_path}")
                except Exception as e:
                    print(f"Error deleting local FAISS zip file: {e}")
            
            # Update the bot document: set the faiss_file_id field to an empty string.
            chat_bots_collection.update_one(
                {"_id": ObjectId(bot_id)},
                {"$set": {"faiss_file_id": ""}}
            )
            
            return JsonResponse({"message": "FAISS file deleted (from GridFS and locally) and bot updated."}, status=200)
        
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


def load_faiss_index(bot_id):
    """
    Load the FAISS index for a given bot.
    If the local FAISS directory is missing, attempt to download the ZIP file from MongoDB,
    extract it, and then load the index.
    """
    faiss_dir = os.path.join(FAISS_DIR, f"{bot_id}.faiss")
    
    # If the local FAISS directory doesn't exist, try to download it from GridFS
    if not os.path.exists(faiss_dir):
        bot_doc = chat_bots_collection.find_one({"_id": ObjectId(bot_id)})
        if bot_doc and "faiss_file_id" in bot_doc:
            file_id = bot_doc["faiss_file_id"]
            try:
                grid_out = fs.get(ObjectId(file_id))
                # Save the ZIP file temporarily
                zip_path = os.path.join(FAISS_DIR, f"{bot_id}.faiss.zip")
                with open(zip_path, 'wb') as f:
                    f.write(grid_out.read())
                # Extract the ZIP file into the FAISS directory
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(faiss_dir)
            except Exception as e:
                print(f"Error retrieving FAISS index from GridFS: {e}")
                return None
        else:
            print("No FAISS file ID found in the bot document.")
            return None
    
    # Now load the FAISS index (using dangerous deserialization if you trust the source)
    try:
        return FAISS.load_local(faiss_dir, embedding_model, allow_dangerous_deserialization=True)
    except Exception as e:
        print(f"Error loading FAISS index: {e}")
        return None



# @csrf_exempt
# def chat_generation(request):
#     if request.method == "POST":
#         data = request.POST  # For form data
#         email = data.get('email')
#         user_name = data.get('username')
#         bot_id = data.get('bot_id')
#         bot_name = data.get('bot_name')
#         prompt = data.get('prompt')
#         start_message = data.get('start_message')
#         last_message = data.get('last_message')
#         last_message = user_name + ": " + last_message

#         user_chats = db['user_chats'].find_one({"email": email, "bot_id": bot_id})

#         if user_chats:
#             # If user chat exists, retrieve the dialog and add the last message
#             chat_history = user_chats.get("chat_history", [])
#             # chat_history_len= len(chat_history)

#         else:
#             new_user_chat = {
#                 "email": email,
#                 "bot_id": bot_id,
#                 "chat_history": [start_message]  # Initialize chat_history with start_message and last_message
#             }
#             # Insert the new document into the 'user_chats' collection
#             user_chats_collection.insert_one(new_user_chat)
#             # return "User chat created with start message and last message."
#             chat_history = [start_message]

#         chat_history_string = '\n'.join(chat_history)
#         chat_prompt = f'''
# #Your task is to roleplay given character and reply to user {user_name} based on it and chat history roleplaying as the character.

# Character:
# '{prompt}'

# chat history:
# '{chat_history_string}'

# last message:
# {last_message}

# You are {bot_name} and reply accordingly 

# The response should be in Json format based on last message with a single dialog:
# {{
#     {user_name}: dialog
# }}
# '''

#         # Call the groq_res function
#         bot_chat = groq_res(chat_prompt)
#         bot_chat = json.loads(bot_chat)

#         bot_chat = list(bot_chat.values())[0]
#         bot_response = {"sender":bot_name,"message":bot_chat}
#         bot_chat = bot_name+": "+ bot_chat
#         chat_history.append(last_message)
#         chat_history.append(bot_chat)

#         user_chats_collection.update_one(
#             {"email": email, "bot_id": bot_id},
#             {"$set": {"chat_history": chat_history}}
#         )
#         # return Response({"response": bot_chat})
        
#         return JsonResponse(bot_response, status=200)

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


         # Fetch relevant context from FAISS index
        vector_store = load_faiss_index(bot_id)
        if vector_store:
            # Use FAISS to retrieve relevant context based on the last message
            context_docs = vector_store.similarity_search(last_message, k=3)  # Top 3 similar documents
            context = "\n".join([doc.page_content for doc in context_docs])
        else:
            context = ""  # No FAISS index found, use empty context
        print("context:  ", context)
        chat_history_string = '\n'.join(chat_history)
        chat_prompt = f'''
#Your task is to roleplay given character and reply to user {user_name} based on it and chat history roleplaying as the character.

Character:
'{prompt}'

chat history:
'{chat_history_string}'

Relevant Context:
'{context}'

last message:
{last_message}

You are {bot_name} and reply accordingly 

The response should be in Json format based on last message with a single dialog:
{{
    {user_name}: dialog
}}
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
        content_type = file_data.content_type or "image/jpeg"

        # Return the image as an HTTP response
        return HttpResponse(file_data.read(), content_type=content_type)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
