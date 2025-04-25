from ast import Return  # not needed actually, can be removed
import os
import time
import json
import random
from datetime import datetime, timedelta
import time
import google.auth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# --- CONFIG --- #
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
CLIENT_SECRET = "client_secret.json"
TOKEN_FILE = "token.json"
VIDEO_ID = "tW_E61KzPuE"
BANNED_WORDS = [] 
GREETED_USERS = set()
TIMED_OUT_USERS = {}
RETURNING_USERS = {}
LIVE_CHAT_ID = None
API_CALL_COUNT = 0
START_TIME = datetime.now()
LAST_CHAT_TIME = datetime.now()
LAST_SENT_TIME = datetime.min # Initialize to the smallest possible datetime value

GREETING_COOLDOWN = timedelta(minutes=15)
TIMEOUT_COOLDOWN = timedelta(minutes=10)

IGNORED_BOTS = ["streamlabs", "nightbot", "rukiya"]

GREETINGS = [
    "Arre kya entry maari bhai! 🔥", "Dekho dekho, asli legend aa gaya 😂",
    "Chat ki roshni aa chuki hai 🌟", "Swagat nahi karoge hamara? 😎",
    "Kya haal hai mere streamer ke star? 🌛",
    "Bhai tu aaya, chat mein jaan aa gayi! 😍",
    "Tum aaye ho toh andhera chhata 🌚",
    "Lagta hai YouTube bhi surprise ho gaya tumhe dekh ke 😲",
    "Itni der kyu laga di bhai, chappal leke baitha tha main 👟",
    "Aap aaye toh laga ki chat mein life hai 😂",
    "Kya bakchodi karne aaye ho aaj? 😏",
    "Lo bhai, celebrity entry le chuka hai 👑"
]

FAREWELLS = [
    "Thanks for joining, milte hain break ke baad 🎬",
    "Chalte chalte, mere yeh do lafz yaad rakhna... 😢",
    "Fir aana bhai, bina bataye na jaana 😎",
    "Tata bye bye! Stream miss mat karna! 👋",
    "Jaa rahe ho? Accha suno... tumhari yaad aayegi! 😭"
]

CHAT_DEAD_ROASTS = [
    "Bhai kuch bol do, chat ka funeral ho gaya kya? 🪦",
    "Streamer OP, par chat RIP 💀",
    "Chat mein sannata hai bhai… kya IPL chal raha hai kya? 🏏",
    "Lagta hai sab ne mute pe laga diya stream 😴",
    "Ek din chat bhi legend ban jaayegi… yaadein reh jaayengi 😔",
    "Chat mein sab so rahe hain kya? Koi toh bol do bhai! 😴",
    "Chat ki jaan hai, par aaj jaan nahi hai 😵"
]

SHAYARIS = [
    "Dil ki baatein kehne ka waqt nahi mila,\nTujhse milne ka mauka toh mila,\nPar ab toh bas yaadon mein reh gaya hai tu,\nKash ek baar keh de, \"mujhe yaad hai tu.\"",
    "Akela tha, akela rahe gaya,\nAb aadat hi ban gaya chhupane ki...",
    "Na main kahani, na koi kirdar,\nBas ek mohra, bas ek intezar.",
    "Dil ki baatein kehne ka waqt nahi mila,\nTujhse milne ka mauka toh mila,\nPar ab toh bas yaadon mein reh gaya hai tu,\nKash ek baar keh de, \"mujhe yaad hai tu.\"",
    "Tumhare bina sab kuch hai,\nPar tumhare bina sab kuch adhoora hai.",
   " Chaha tha usse dil se, par voh kabhi samjhi nahi,\nHar pal uski yaadon mein khud ko bhula diya,\nKash ek baar keh de voh… main bhi chahti hoon tujhe, har ek aas mein.",
   "Khuda ke saaye mein socha kab tak sahenge\nSabar ke daaman ko aur kitna thaamenge?\nDard ne har shabd lafz mein rang bhar diya,\nEk sitara gira, magar kaun tha jo dekhe?\nKhamoshi poochti rahi, jawab kahaan mile?",
    "Mohabbat na hoti to ghazal kaun likhta,\nKeechad mein khile us phool ko kamal kaun kehta.\nPyaar to kudrat ka karishma hai,\nWarna laash ke ghar ko Taj Mahal kaun kehta.",
    "Akela tha, akela rahe gaya,\nAb aadat hi ban gaya chhupane ki...\nDost banane ka junoon gum ho gaya,\nNa baat ho kisi se, dil udaas ho gaya",
    "Na main kahani, na koi kirdar,\nBas ek mohra, bas ek intezar.\nJab zaroorat thi tab kiya yaad,\nAb bhool gaye jaise bekaar.",
     "Dil ki baatein kehne ka waqt nahi mila,\nTujhse milne ka mauka toh mila,\nPar ab toh bas yaadon mein reh gaya hai tu,\nKash ek baar keh de, \"mujhe yaad hai tu.\"",
    "Akela tha, akela rahe gaya,\nAb aadat hi ban gaya chhupane ki...",
    "Na main kahani, na koi kirdar,\nBas ek mohra, bas ek intezar.",
    "Mohabbat na hoti to ghazal kaun likhta,\nKeechad mein khile us phool ko kamal kaun kehta.\nPyaar to kudrat ka karishma hai,\nWarna laash ke ghar ko Taj Mahal kaun kehta.",
    "Akela tha, akela rahe gaya,\nAb aadat hi ban gaya chhupane ki...\nDost banane ka junoon gum ho gaya,\nNa baat ho kisi se, dil udaas ho gaya",
    "Na main kahani, na koi kirdar,\nBas ek mohra, bas ek intezar.\nJab zaroorat thi tab kiya yaad,\nAb bhool gaye jaise bekaar.",
    "Tere jaane ke baad tanha ho gaye,\nJo kabhi hans dete the, aaj roya karte hain.\nWaqt badla, log badle, jazbaat badal gaye,\nMagar ek tu hi hai, jo yaadon mein waisi hi hai.",
    "Keh nahi paate, magar mehsoos hota hai,\nJo dard aankhon se beh gaya, voh kabhi lafzon mein nahi aata.\nHar muskurahat ke peeche chhupa hai ek raaz,\nJise samjha sirf tanhai ne, aur kisi ne nahi.",
    "Intezaar ka bhi ek apna maza hota hai,\nHar pal uski yaadon mein kho jaata hai.\nKya karein, aadat si ho gayi hai us pal ki,\nJab voh kehta tha, \"bas thodi der aur.\"",
    "Kabhi socha nahi tha tu itna khas ban jaayega,\nPal pal mein tera naam, meri saans ban jaayega.\nTu samjhe ya na samjhe meri khamoshi ko,\nMagar har lafz, sirf tera zikr kar jaayega.",
    "Raat ke aakhri pehar mein kuch yaadein bol padti hain,\nChup chaap dil ke kone mein roshni kar jaati hain.\nJise bhool jaane ki koshish mein the hum,\nWoh khwab ban kar roz laut aati hain."

]

def authenticate():
    global API_CALL_COUNT
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET, SCOPES)
            creds = flow.run_local_server(port=8080)
            with open(TOKEN_FILE, "w") as token_file:
                token_file.write(creds.to_json())
    API_CALL_COUNT += 1
    return build("youtube", "v3", credentials=creds)

def get_live_chat_id(youtube):
    global API_CALL_COUNT
    response = youtube.videos().list(part="liveStreamingDetails", id=VIDEO_ID).execute()
    API_CALL_COUNT += 1
    try:
        return response["items"][0]["liveStreamingDetails"]["activeLiveChatId"]
    except (KeyError, IndexError):
        print("❌ Could not find Live Chat ID.")
        return None

def send_message(youtube, text):
    global API_CALL_COUNT, LAST_SENT_TIME

    now = datetime.now()
    time_since_last = (now - LAST_SENT_TIME).total_seconds()

    # Cooldown: wait if too soon
    if time_since_last < 3:  # YouTube allows 1 message every ~3 seconds
        wait_time = 3 - time_since_last
        print(f"⏳ Waiting {wait_time:.2f}s to avoid rate limit")
        time.sleep(wait_time)

    try:
        youtube.liveChatMessages().insert(
            part="snippet",
            body={
                "snippet": {
                    "liveChatId": LIVE_CHAT_ID,
                    "type": "textMessageEvent",
                    "textMessageDetails": {"messageText": text}
                }
            }).execute()
        LAST_SENT_TIME = datetime.now()
        API_CALL_COUNT += 1
        print(f"✅ Sent message: {text}")
    except Exception as e:
        print(f"❌ Failed to send message: {e}")

def listen_to_chat(youtube):
    global LIVE_CHAT_ID, API_CALL_COUNT, LAST_CHAT_TIME
    print("📡 Listening to chat...")
    next_page_token = None

    while True:
        chat_response = youtube.liveChatMessages().list(
            liveChatId=LIVE_CHAT_ID,
            part="snippet,authorDetails",
            pageToken=next_page_token).execute()
        API_CALL_COUNT += 1
        current_time = datetime.now()

        for item in chat_response["items"]:
            try:
                author = item["authorDetails"]["displayName"].lower()
                user_id = item["authorDetails"]["channelId"]
                message = item["snippet"]["displayMessage"].lower()
            except Exception as e:
                print(f"[WARN] Skipping message due to error: {e}")
                continue

            LAST_CHAT_TIME = current_time
            print(f"{author}: {message}")

            if any(bot in author for bot in IGNORED_BOTS):
                continue

            if any(word in message for word in BANNED_WORDS):
                if user_id not in TIMED_OUT_USERS or (current_time - TIMED_OUT_USERS[user_id]) > TIMEOUT_COOLDOWN:
                    send_message(youtube, f"@{author} tameez se baat kar bhai! 😡 5 min ka timeout le.")
                    # (Timeout code can go here)
                continue

            if user_id in RETURNING_USERS:
                if (current_time - RETURNING_USERS[user_id]) > GREETING_COOLDOWN:
                    send_message(youtube, f"@{author} Arre welcome back! Lagta hai charger mil gaya 🔌😂")
            elif user_id not in GREETED_USERS:
                greeting = random.choice(GREETINGS)
                send_message(youtube, f"@{author} {greeting}")
                GREETED_USERS.add(user_id)

            RETURNING_USERS[user_id] = current_time

            if "ru stats" in message:
                uptime = datetime.now() - START_TIME
                send_message(youtube, f"Viewers: N/A | Uptime: {str(uptime).split('.')[0]}")
            elif "ru shayari" in message:
                send_message(youtube, random.choice(SHAYARIS))
            elif any(word in message for word in ["bye", "goodnight", "gn"]):
                send_message(youtube, f"@{author} {random.choice(FAREWELLS)}")

        if (current_time - LAST_CHAT_TIME).seconds > 180:
            send_message(youtube, random.choice(CHAT_DEAD_ROASTS))
            LAST_CHAT_TIME = current_time

        next_page_token = chat_response.get("nextPageToken")
        time.sleep(int(chat_response["pollingIntervalMillis"]) / 1000)

def run_bot():
    youtube = authenticate()
    global LIVE_CHAT_ID
    LIVE_CHAT_ID = get_live_chat_id(youtube)
    if LIVE_CHAT_ID:
        send_message(youtube, "🤖 Rukiya is online and watching the chat!")
        listen_to_chat(youtube)
    else:
        print("❌ Can't run without a live chat ID.")

if __name__ == "__main__":
    run_bot()