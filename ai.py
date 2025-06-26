from google import genai
from google.genai.errors import ServerError
import os
from dotenv import load_dotenv
from bot_payload import *

load_dotenv() # Load Environment Variables
client = genai.Client(api_key=os.getenv("GEMINI")) # Setup AI
MODEL = "gemini-2.0-flash-001"
PRINT_SESSIONS_ALWAYS = True
sessions = {
    "global": [client.chats.create(model=MODEL)],
}

features = {
    "filter": True,
    "rant": False,
    "yap": False,
    "angry": False,
    "bully": False,
    "ultrasilly": False,
    "fake_unfilter": False
}


current_sessions = {
    "global": 0
}

def reset_global_session():
    sessions["global"][0] = client.chats.create(model=MODEL)


def set_session(userid, id):
    print(id)
    print(len(sessions[userid]))
    if userid not in sessions: # If user never chatted or has no sessions
        current_sessions[userid] = -1
    elif len(sessions[userid]) >= id and id > 0 or id == -1:
        current_sessions[userid] = id
    else:
        id = -1000
    return current_sessions[userid]


def create_session(userid):
    if userid not in sessions:
        sessions[userid] = []
    
    sessions[userid].append(client.chats.create(model=MODEL))
    return len(sessions[userid])

def chat(userid, message, username,print_unf=True):
    filtered = features["filter"]
    isNewSession = False
    if userid not in current_sessions: # If user never chatted
        current_sessions[userid] = -1 # Global Chat
        isNewSession = True
    
    sessionid = current_sessions[userid] # Get session ID

    if userid not in sessions and sessionid != -1: # If not exist and not global
        create_session(userid)
        isNewSession = True
        sessionid = 1
    
    chat = None
    if sessionid == -1:
        chat = sessions["global"][0]
    else:
        chat = sessions[userid][sessionid-1] # Get chat object

    print(isNewSession)
    sessInfo=""
    if isNewSession and sessionid == -1:
        sessInfo="-# Switched to Global session!\n"
    elif isNewSession:
        sessInfo=f"-# Created new session ({sessionid})\n"
    elif PRINT_SESSIONS_ALWAYS and sessionid == -1:
        sessInfo=f"-# Session: global\n"
    elif PRINT_SESSIONS_ALWAYS:
        sessInfo=f"-# Session: {sessionid}\n"
    try:
        message = chat.send_message(setup_payload(userid,username,features)+message).text
    except ServerError as e:
        message = "**[AI ERROR]** The Google Gemini Servers might be overloaded. Please try again Later! `Likely: HTTP Error Code 503`"
    except:
        message = "**[GENERAL ERROR]** Something went HORRIBLY wrong! Please report this to Lighty ASAP! ||Thanks >^-^<||"
    unf = message+""
    if print_unf: print("> "+message)
    if filtered:
        for word in filter:
            message = message.replace(word, "_[Filtered]_").replace(word.upper(), "_[Filtered]_").replace(word.capitalize(), "_[Filtered]_")
    else:
        sessInfo=f"-# Not Filtered!\n"
    return {"chat":message, "sid":sessionid, "isNew":isNewSession, "info":sessInfo, "unf":unf} # Return chat
