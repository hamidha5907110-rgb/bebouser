#!/usr/bin/env python3
"""
BEBO ULTIMATE – DYNAMIC USERBOT
Merges BEBO's core with BEBO's advanced raid/spam engine, flow mode,
security locks, and cloud hosting dummy server.
All rights reserved.
"""

import os
import sys
import subprocess

# ==================== AUTO-MODULE DOWNLOADER ====================
def ensure_dependencies():
    required_packages = ["telethon", "requests", "gtts"]
    for pkg in required_packages:
        try:
            __import__(pkg)
        except ImportError:
            print(f"[*] Missing module '{pkg}'. Auto-downloading...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

ensure_dependencies()
# ================================================================

import ssl
ssl._create_default_https_context = ssl._create_unverified_context

import asyncio
import logging
import random
import time
import threading
import json
from collections import defaultdict, deque
from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set

from telethon import TelegramClient, events, utils, functions
from telethon.sessions import StringSession
from telethon.errors import ChatAdminRequiredError, UserNotParticipantError, FloodWaitError
from telethon.tl.functions.channels import EditAdminRequest, EditBannedRequest, EditTitleRequest
from telethon.tl.functions.messages import DeleteMessagesRequest, CreateChatRequest, EditChatTitleRequest
from telethon.tl.types import (
    Channel, Chat, ChatAdminRights, ChatBannedRights,
    InputPeerUser, Message, MessageMediaDocument, MessageMediaPhoto, User
)

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

# ------------------------- CONFIGURATION (Dynamic) -------------------------
API_ID = int(os.getenv("API_ID", "38843772"))
API_HASH = os.getenv("API_HASH", "875fbb273801c8025d05e98173fca536")
PHONE_NUMBER = os.getenv("PHONE_NUMBER", "+917722026588")
OWNER_ID = int(os.getenv("OWNER_ID", "2119464081"))
SESSION_NAME = os.getenv("SESSION_NAME", "bebo_userbot")

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("bebo.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# ------------------------- CLOUD DUMMY SERVER -------------------------
class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"BEBO Ultimate is running 24/7!")

def start_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), DummyHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    logger.info(f"Cloud dummy server started on port {port}")

# ------------------------- GLOBAL STATE & TEXTS -------------------------
BOT_STATE_FILE = "bot_state.txt"
FLOW_STATE_FILE = "flow_state.txt"
TEXTS_FILE = "saved_texts.txt"

bot_on = True
flow_mode = False
saved_texts: List[str] = []
spray_delay = 0.5
auto_reply_on = False
warnings: Dict[int, int] = {}
active_tasks: Dict[str, asyncio.Task] = {}

def load_bot_state():
    global bot_on, flow_mode, saved_texts
    try:
        if Path(BOT_STATE_FILE).exists():
            with open(BOT_STATE_FILE, "r") as f: bot_on = f.read().strip().lower() == "on"
        if Path(FLOW_STATE_FILE).exists():
            with open(FLOW_STATE_FILE, "r") as f: flow_mode = f.read().strip().lower() == "on"
        if Path(TEXTS_FILE).exists():
            with open(TEXTS_FILE, "r", encoding="utf-8") as f: saved_texts = [line.strip() for line in f if line.strip()]
    except Exception as e:
        logger.error(f"Error loading files: {e}")

def save_bot_state():
    with open(BOT_STATE_FILE, "w") as f: f.write("on" if bot_on else "off")
def save_flow_state():
    with open(FLOW_STATE_FILE, "w") as f: f.write("on" if flow_mode else "off")
def save_saved_texts():
    with open(TEXTS_FILE, "w", encoding="utf-8") as f: f.write("\n".join(saved_texts))

load_bot_state()

# ------------------------- TEXT LISTS (Merged) -------------------------
# Original BEBO texts
RAID_TEXTS = [
    "🔥 BEBO IS HERE TO DOMINATE! BOW DOWN! 🔥",
    "💀 YOUR CHAT BELONGS TO BEBO NOW! 💀",
    "⚡ FEEL THE POWER OF BEBO'S ULTIMATE BOT! ⚡",
    "🗑️ THIS CHAT IS TRASH, BEBO IS CLEANING IT UP! 🗑️",
    "💥 BEBO ULTIMATE STRIKES AGAIN! 💥",
    "👑 BEBO IS THE KING HERE! RESPECT THE NAME! 👑",
    "🌪️ A TSUNAMI OF SPAM BY BEBO! 🌪️",
    "🩸 NO MERCY FROM BEBO ULTIMATE! 🩸",
    "🚫 ALL YOUR EFFORTS ARE USELESS AGAINST BEBO! 🚫",
    "💣 PREPARE FOR TOTAL DESTRUCTION! BEBO IS IN CONTROL! 💣"
]

GAALI_LIST = [
    "Abbe teri maa ki chut ko kutte se katva dunga randi k pille 😡😠😤",
    "teri behn ki chut mai set top box ghusa dunga mai madarchod 😳",
    "chutmarik teri tatti jesi shakl pe pad dunga bhen k lode chutiye madarchod kitna chutiya aadmi hai Tu😡",
    "jaya bachan bana kai chod dunga teri behn ko😋",
    "maa k lode tere jese randi k baccho ka abortion krva dena chiye 😤",
    "bhosdk teri maa k bhosde mai MDH CHANA MASALA daal k tere baap ko vo spicy bhosda khila dunga 🤢",
    "Tere dalle baap ka lund uth'ta hai nhi tbhi teri maa 150 k bhav se deti hai 😍",
    "madarchod k baache sudhar ja 😡😠😤",
    "teri ma Randi tera baap hizda kaali gaand kay Khade baal jhaatu Randi kay chodu",
    "TERA BAAP JOHNY SINS CIRCUS KAY BHOSDE JOKER KI CHIDAAS 14 LUND KI DHAAR TERI MUMMY KI CHUT MAI 200 INCH KA LUND",
    "maa k lode tere jese randi k baccho ko bachpan mai maar dena chiye",
    "madarchod chutmarke teri tatti jesi shakl pe pad dunga bhen k lode chutiye",
    "Bhenchod baap se panga matt le Warna maa chodh di Jayegi 🤬",
    "chut kay baal nipple ki dhaar teri gaand mai Road roller de dunga 🖕",
    "teri Gaand Mein Kutte Ka Lund 🖕",
    "Teri Jhaatein Kaat Kar Tere Mooh Par Laga Kar Unki French Beard Bana Doonga!",
    "GAND KII DHAAR BHOSDIKE FATEE HUE CONDOM KI NAAJAIS PAIDAISH",
    "chutiye behenchod lauda madarchod gaandu bhosadikey",
    "Gote Kitne Bhi Badey Ho, Lund Ke Niche Hi Rehtein Hai",
    "डालते ही झड़ गए सब, टिका न कोई भी फूल गले में मेरे हार के !\nदर्द उनको हुआ तो निकाल लिया मैंने, काँटा जो चुभा पैरों में सरकार के !",
    "हम उस बेवफा से क्या दिल लगा बैठे,\nखली फाट अपनी सुकून की माँ चुदा बैठे।"
]

# BEBO texts
reply_texts = [
    "𝐊ʏᴀ 𝐑ᴇ 𝐑ᴀɴᴅɪᴋᴇ 𝐂ᴏᴏʟ 𝐁ᴀɴᴇɢᴀ 𝐓ᴜ 𝐂ʜᴀʟ 𝐀ʙ 𝐂ʜᴜᴅ 𝐀ᴘɴᴇ 𝐁ᴀᴀᴘ 𝗕𝗲𝗯𝗼 𝐒ᴇ - 🦢💘",
    "𝐊ɪ 𝐌ᴀᴀ 𝐌ᴀʀʀ 𝐆ᴀʏɪ 𝐘ᴀᴀʀ - 𝐉ᴀɪ 𝗕𝗲𝗯𝗼 ! 🌙",
    "acha beta 😂🔥👊🏻 ? coi na me toh HATER codunga 😹💔🔥😆👊🏻💥",
    "chudke bhaga kaise 😂💥🤣🤘🏻",
    "ne toh 𝗕𝗲𝗯𝗼 ka lun muh me lelia 😂🙏🏻😂🙏🏻",
    "try maa सूर्य☀ nikalte hi pel du 😹🔥💔",
    "mkl lun te vaj 😂✊🏻💦",
    "𝗧ᴍᴋ𝗕 pe 𝗕𝗲𝗯𝗼 ka hamla 😂⚔🔥💥",
    "𝐂ʟʟ 𝐇ᴀʀᴍᴢᴀᴅ𝐈 𝐊ᴇ लड़के 💛🤍🩵",
    "oi 𝐓ᴇʀɪ 𝐌‌ᴀᴀ गुलाम ₰🖤",
    "chl rndyce chud ke dikha 😂💥🤣🔥",
    "𝐊ɪ 𝐌ᴀᴀ 𝐌ᴀʀʀ 𝐆ᴀʏɪ naacho 💃🏻💃🏻🕺🏻🎶😂😆💞🔥 !",
    "tera baap bass 𝗕𝗲𝗯𝗼 hai 😂🎀",
    "try maa hagte hue paad mari -#😹🔥🥀",
    "𝐓ᴇʀɪ 𝐌ᴜᴍᴍʏ 𝐂ʜᴏᴅ 𝐃ɪ 𝗕𝗲𝗯𝗼 𝐍ᴇ 𝐁ᴡᴀʜᴀʜᴀʜᴀ ⚜",
]

rr_texts = GAALI_LIST  # reuse

fun_texts = [
    "तेरे मां के दूदू के बीच मेरा lund fas gaya oops 🤪（ ͜.🍆 ͜.）",
    "𝐓ᴇʀʏ 𝐁ʜᴇ𝐍 𝐊ᴇ ( ͜. ㅅ ͜. )🥛 ʏᴜᴍᴍʏ ",
    "𓂃☁︎ 𓂃𝐒ɪᴅᴇ 𝐇ᴀᴛ 𝐆ᴜʟᴀᴍ 𝐓ᴇʀʏ 𝐌ᴀᴀ 𝐊ᴏ 𝐂ʜᴏᴅɴᴇ  मेरी रेलगाड़ी आ रही .-'🚂-'.ᯓᡣ𐭩______ 𓂃☁︎ 𓂃",
    "⋆⭒˚.⋆🔭 𝐒ʜᴜᴛ 𝐔ᴘ 𝐑ᴀɴᴅɪᴋᴇ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ɪ 𝐂ʜᴜᴅᴀɪ 𝐄ɴᴊᴏʏ 𝐊ʀ 𝐑ᴀʜᴀ 𝐓ᴇʟᴇ𝐒ᴄᴏᴘᴇ 𝐒ᴇ⋆⭒˚.⋆🔭",
]

flag_texts = [
    " ོ༘₊⁺🇮🇳 ₊⁺⋆.˚ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ 𝗕𝗲𝗯𝗼 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐈ɴᴅɪᴀ 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇮🇳 ₊⁺⋆.˚",
    " ོ༘₊⁺🇯🇵 ₊⁺⋆.˚ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ 𝗕𝗲𝗯𝗼 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐉ᴀᴘᴀɴ 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇯🇵 ₊⁺⋆.˚",
    " ₊⁺🇺🇸 ₊⁺⋆.˚ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ 𝗕𝗲𝗯𝗼 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐔𝐒𝐀 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇺🇸 ₊⁺⋆.˚",
    " ོ༘₊⁺🇬🇧 ₊⁺⋆.˚ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ 𝗕𝗲𝗯𝗼 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐔𝐊 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇬🇧 ₊⁺⋆.˚",
    " ོ༘₊⁺🇰🇷 ₊⁺⋆.˚𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ 𝗕𝗲𝗯𝗼 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐊ᴏʀᴇᴀ 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇰🇷 ₊⁺⋆.˚",
    " ོ༘₊⁺🇩🇪 ₊⁺⋆.˚ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ 𝗕𝗲𝗯𝗼 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐆ᴇʀᴍᴀɴʏ 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇩🇪 ₊⁺⋆.˚",
]

heart_replies = [
    "𓂃˖˳·˖ ִֶָ ⋆❤️͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚❤️ ݁˖⭑.ᐟ",
    "𓂃˖˳·˖ ִֶָ ⋆🧡͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚🧡 ݁˖⭑.ᐟ",
    "𓂃˖˳·˖ ִֶָ ⋆💛͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚💛 ݁˖⭑.ᐟ",
    "𓂃˖˳·˖ ִֶָ ⋆💚͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚💚 ݁˖⭑.ᐟ",
    "𓂃˖˳·˖ ִֶָ ⋆💙͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚💙 ݁˖⭑.ᐟ",
]

attack_list = [
    "⚔️ Teri aukat nahi mujhse ladhne ki randike 😂🔥",
    "💥 Chal bhaag yahan se chutiye warna maar khayega 🤣⚔️",
    "🗡️ Tera baap aaya hai sunta nahi kya 👑😈",
    "⚡ Mere saamne aake dikhao himmat hai toh 😎💪",
    "🔥 Attack mode on — teri khair nahi aaj 😡⚔️",
    "💀 Tujhe itna marunga ke teri maa bhi nahi pehchanegi 😂🔥",
    "⚔️ Randike chal 1v1 kar le dikhata hoon kaun baap hai 👊😤",
    "💥 Beta ye territory meri hai nikal yahan se 🏴‍☠️⚡",
    "🗡️ Aukaat hai toh saamne aa nahi toh chup baith 😈💀",
    "⚡ Tu keyboard warrior hai asli mard nahi 😂👊",
    "🔥 Teri maa ne bhi bola tera baap chahiye 😹💔",
    "💥 Chal hat yahan se chota baccha 🤣👋",
    "⚔️ Mujhe gaali de ke dekh kya hoga teri life mein 😈⚡",
    "💀 Bhai seedha bol de surrender karega ya maar khayega 😎🔥",
    "🗡️ Attack karta hoon toh block nahi hoga tera 😡⚔️",
    "⚡ Yeh game mein nahi real life mein bhi kaatenge tujhe 💪😤",
    "🔥 Tera confidence dekh ke hansi aati hai yaar 😂💥",
    "💥 Andha hai ya dikhta nahi kaun boss hai yahan 👑⚔️",
    "⚔️ Teri har gaali pe 10 gaaliyan waapis aayengi 😈🔥",
    "💀 Beta peeth nahi dikhana mujhe — coward 🏃‍♂️😂",
]

roast_list = [
    "🔥 Teri zindagi ek bakwas webseries ki tarah hai — 1 season mein flop 😂📺",
    "🤣 Bhai teri personality ek sada hua pyaz jaisi hai — khole toh aansu aaye 🧅💀",
    "😹 Tu itna bura lagta hai ke teri photo dekh ke mosquito bhi bhaag jata hai 🦟😂",
    "🔥 Teri maa ne bhi socha hoga — yaar galti ho gayi 😹👶",
    "🤣 Tujhe dekh ke pata chalta hai — darr darr ke jeena kya hota hai 😂💀",
    "😹 Beta tu Google Maps pe search kare toh bhi worthless aayega 🗺️😈",
    "🔥 Teri iq level negative hai — calculator mein error aata hai 🧮😂",
    "🤣 Tu chhata hua papad hai — touch karte hi toot gaya 😹🔥",
    "😹 Bhai teri aukat itni hai ke mirror bhi muh fer leta hai 🪞😂",
    "🔥 Teri personality dekh ke AI bhi depressed ho gaya hoga 🤖😹",
]

all_texts = reply_texts + rr_texts + fun_texts + flag_texts + heart_replies + attack_list + roast_list

# ------------------------- ADVANCED STATE (BEBO COMPATIBLE) -------------------------
# Use the same file names as bebokaauser.py for compatibility
SAFE_USERS_FILE = "safe_users.json"
AUTO_DELETE_FILE = "auto_delete.json"
DELETE_USERS_FILE = "delete_users.json"
ADV_STATE_FILE = "bebo_state.json"   # changed from adv_state.json to match first script

COUNTRY_EMOJIS = ["🇮🇳", "🇺🇸", "🇬🇧", "🇨🇦", "🇦🇺", "🇩🇪", "🇫🇷", "🇯🇵", "🇰🇷", "🇨🇳", "🇷🇺", "🇧🇷", "🇮🇹", "🇪🇸", "🇵🇰", "🇧🇩", "🇳🇵", "🇱🇰", "🇦🇪", "🇸🇦"]
RANDOM_EMOJIS = ["🔥", "⚡", "✨", "🌟", "⭐", "💫", "🌙", "☀️", "❤️", "🧡", "💛", "💚", "💙", "💜", "😀", "😃", "😄", "😁", "👍", "👎"]

BOOST_MODE = False
CRITICAL_MODE = False
NORMAL = dict(SPAM=5, WINDOW=6)
BOOST = dict(SPAM=3, WINDOW=3)
CRIT = dict(SPAM=2, WINDOW=2)
CFG = NORMAL.copy()
MUTE_TABLE = (300, 900, 1800, 3600, 21600)

class BotState:
    """Unified state manager – compatible with BEBO."""
    def __init__(self):
        self.safe_users: Set[int] = set()
        self.safe_usernames: Dict[str, int] = {}
        self.auto_delete_chats: Dict[int, bool] = {}
        self.delete_target_users: Dict[int, Set[int]] = {}
        self.delete_target_usernames: Dict[int, Set[str]] = {}
        self.delete_delay = 0.05

        self.autoswipe_active: Dict[int, str] = {}
        self.adv_spam_active: Dict[int, str] = {}
        self.namechange_active: Dict[int, bool] = {}
        self.reply_raid_active: Dict[int, Dict[int, Dict]] = {}
        self.blitz_active: Dict[int, bool] = {}

        self.locked_titles: Dict[int, str] = {}
        self.swipe_targets: Dict[int, Dict[int, str]] = {}
        self.msg_log = defaultdict(lambda: deque())
        self.offenses = defaultdict(int)

        self.locked_groups: Set[int] = set()
        self.locked_chat: Set[int] = set()
        self.locked_name_change: Set[int] = set()
        self.emergency_active: Dict[int, bool] = {}

        self.metrics = {"start": time.monotonic(), "msg": 0, "mutes": 0, "swipes": 0}
        self.namechange_delays: Dict[int, float] = {}   # for dynamic delay

        self.load_data()

    def load_data(self):
        try:
            if os.path.exists(SAFE_USERS_FILE):
                with open(SAFE_USERS_FILE, "r") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        self.safe_users = set(data.get("user_ids", []))
                        self.safe_usernames = data.get("usernames", {})
                    else:
                        self.safe_users = set(data)
        except: pass
        try:
            if os.path.exists(AUTO_DELETE_FILE):
                with open(AUTO_DELETE_FILE, "r") as f:
                    self.auto_delete_chats = {int(k): v for k, v in json.load(f).items()}
        except: pass
        try:
            if os.path.exists(DELETE_USERS_FILE):
                with open(DELETE_USERS_FILE, "r") as f:
                    data = json.load(f)
                    self.delete_target_users = {int(k): set(v.get("user_ids", [])) for k, v in data.items()}
                    self.delete_target_usernames = {int(k): set(v.get("usernames", [])) for k, v in data.items()}
        except: pass
        try:
            if os.path.exists(ADV_STATE_FILE):
                with open(ADV_STATE_FILE, "r") as f:
                    data = json.load(f)
                    self.locked_titles = {int(k): v for k, v in data.get("titles", {}).items()}
                    self.swipe_targets = {int(k): v for k, v in data.get("swipes", {}).items()}
        except: pass

    def save_safe_users(self):
        try:
            with open(SAFE_USERS_FILE, "w") as f:
                json.dump({"user_ids": list(self.safe_users), "usernames": self.safe_usernames}, f)
        except: pass
    def save_auto_delete(self):
        try:
            with open(AUTO_DELETE_FILE, "w") as f:
                json.dump(self.auto_delete_chats, f)
        except: pass
    def save_delete_targets(self):
        try:
            data = {}
            for chat_id in self.delete_target_users:
                data[str(chat_id)] = {
                    "user_ids": list(self.delete_target_users.get(chat_id, set())),
                    "usernames": list(self.delete_target_usernames.get(chat_id, set()))
                }
            with open(DELETE_USERS_FILE, "w") as f:
                json.dump(data, f)
        except: pass
    def save_state(self):
        try:
            with open(ADV_STATE_FILE, "w") as f:
                json.dump({"titles": self.locked_titles, "swipes": self.swipe_targets}, f)
        except: pass

    def add_safe_user(self, user_id: int, username: str = None):
        self.safe_users.add(user_id)
        if username:
            self.safe_usernames[username.lower()] = user_id
        self.save_safe_users()

    def is_user_safe(self, user_id: int, username: str = None) -> bool:
        if user_id in self.safe_users or user_id == OWNER_ID:
            return True
        if username and username.lower() in self.safe_usernames:
            return True
        return False

    def add_delete_target(self, chat_id: int, user_id: int, username: str = None):
        self.delete_target_users.setdefault(chat_id, set()).add(user_id)
        if username:
            self.delete_target_usernames.setdefault(chat_id, set()).add(username.lower())
        self.save_delete_targets()

    def should_delete_user(self, chat_id: int, user_id: int, username: str = None) -> bool:
        if chat_id not in self.delete_target_users:
            return False
        if user_id in self.delete_target_users[chat_id]:
            return True
        if username and chat_id in self.delete_target_usernames:
            if username.lower() in self.delete_target_usernames[chat_id]:
                return True
        return False

state = BotState()

# ------------------------- TELEGRAM CLIENT -------------------------
SESSION_ENV = os.environ.get("SESSION_STRING")
if SESSION_ENV:
    client = TelegramClient(StringSession(SESSION_ENV), API_ID, API_HASH)
else:
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

# ------------------------- AUTH & DECORATORS -------------------------
async def is_authorized(event) -> bool:
    """Checks if user is OWNER or SAFE. Respects global .off toggle."""
    if event.raw_text and event.raw_text.startswith(("/on", ".on")):
        return True
    if not bot_on:
        return False
    if event.out:
        return True
    sender_id = event.sender_id
    if not sender_id:
        return False

    username = None
    try:
        sender = await event.get_sender()
        if hasattr(sender, 'username'):
            username = sender.username
    except: pass

    if state.is_user_safe(sender_id, username):
        return True

    try:
        await event.reply("bebo ko baap bana ke aa randyke!! 🖕💩")
    except: pass
    return False

def command(cmd):
    def decorator(func):
        @client.on(events.NewMessage(pattern=f"^[/.]{cmd}(?:\\b|$)"))
        async def handler(event):
            if not await is_authorized(event):
                return
            try:
                await func(event)
            except Exception as e:
                logger.error(f"Error in /{cmd}: {e}", exc_info=True)
                await event.reply(f"❌ Error: {e}")
        return handler
    return decorator

def flow_command(cmd):
    def decorator(func):
        @client.on(events.NewMessage(pattern=f"^[/.]{cmd}(?:\\b|$)"))
        async def handler(event):
            if not await is_authorized(event):
                return
            if not flow_mode:
                await event.reply("❌ Flow bot is OFF. Use `/switch` to enable.")
                return
            try:
                await func(event)
            except Exception as e:
                logger.error(f"Error in /{cmd}: {e}", exc_info=True)
                await event.reply(f"❌ Error: {e}")
        return handler
    return decorator

async def get_target(event):
    """Extract target user from command arguments."""
    args = event.raw_text.split(maxsplit=1)
    if len(args) < 2:
        await event.reply("⚠️ Please specify a target username or ID.")
        return None
    target_str = args[1].strip()
    if target_str.startswith("@"):
        target_str = target_str[1:]
    try:
        if target_str.isdigit():
            return await client.get_entity(int(target_str))
        else:
            return await client.get_entity(target_str)
    except Exception as e:
        await event.reply(f"❌ Could not find user: {e}")
        return None

async def get_target_from_str(event, target_str):
    if target_str.startswith("@"):
        target_str = target_str[1:]
    try:
        if target_str.isdigit():
            return await client.get_entity(int(target_str))
        else:
            return await client.get_entity(target_str)
    except Exception as e:
        await event.reply(f"❌ Could not find user: {e}")
        return None

# ------------------------- BACKGROUND PROTECTION MODULES -------------------------
async def smart_mute(chat_id, user_id):
    if user_id == OWNER_ID:
        return
    state.offenses[(chat_id, user_id)] += 1
    state.metrics["mutes"] += 1
    duration = MUTE_TABLE[min(state.offenses[(chat_id, user_id)] - 1, 4)]
    try:
        await client(EditBannedRequest(
            chat_id,
            user_id,
            ChatBannedRights(send_messages=True, until_date=int(time.time()) + duration)
        ))
    except: pass

@client.on(events.NewMessage(incoming=True))
async def auto_delete_handler(event):
    if not bot_on:
        return
    chat_id = event.chat_id
    if not state.auto_delete_chats.get(chat_id, False):
        return
    if hasattr(event, 'action') and event.action is not None:
        try:
            await asyncio.sleep(state.delete_delay)
            await event.delete()
        except: pass
        return
    if not event.sender_id:
        return
    user_id = event.sender_id
    username = None
    try:
        sender = await event.get_sender()
        if hasattr(sender, 'username'):
            username = sender.username
    except: pass

    if chat_id in state.delete_target_users and state.delete_target_users[chat_id]:
        if state.should_delete_user(chat_id, user_id, username):
            try:
                await asyncio.sleep(state.delete_delay)
                await event.delete()
            except: pass
        return
    if not state.is_user_safe(user_id, username):
        try:
            await asyncio.sleep(state.delete_delay)
            await event.delete()
        except: pass

@client.on(events.NewMessage(incoming=True))
async def message_guard(event):
    if not bot_on:
        return
    if event.text and event.text.startswith('.'):
        return
    state.metrics["msg"] += 1
    uid, cid = event.sender_id, event.chat_id
    if uid == OWNER_ID:
        return
    if CRITICAL_MODE:
        await smart_mute(cid, uid)
        return

    now = time.monotonic()
    log = state.msg_log[(cid, uid)]
    log.append(now)
    while log and now - log[0] > CFG["WINDOW"]:
        log.popleft()
    if len(log) >= CFG["SPAM"]:
        await smart_mute(cid, uid)
        return
    if cid in state.swipe_targets and uid in state.swipe_targets[cid]:
        state.metrics["swipes"] += 1
        asyncio.create_task(event.reply(state.swipe_targets[cid][uid]))

@client.on(events.NewMessage(incoming=True))
async def chat_lock_handler(event):
    if not bot_on:
        return
    if event.chat_id in state.locked_chat and event.sender_id != OWNER_ID:
        try:
            await event.delete()
        except: pass

@client.on(events.ChatAction)
async def title_guard(event):
    if not bot_on:
        return
    if event.chat_id in state.locked_titles and event.user_id != OWNER_ID:
        try:
            await client(EditChatTitleRequest(event.chat_id, state.locked_titles[event.chat_id]))
            await smart_mute(event.chat_id, event.user_id)
        except: pass

@client.on(events.ChatAction)
async def namechange_lock_handler(event):
    if not bot_on:
        return
    if event.chat_id in state.locked_name_change and event.user_id != OWNER_ID:
        if event.chat_id in state.locked_titles:
            try:
                await client(EditChatTitleRequest(event.chat_id, state.locked_titles[event.chat_id]))
            except: pass

@client.on(events.NewMessage(incoming=True))
async def adv_multireply_handler(event):
    if not bot_on:
        return
    chat_id = event.chat_id
    if chat_id not in state.autoswipe_active:
        return
    swipe_data = state.autoswipe_active[chat_id]
    if isinstance(swipe_data, str) and swipe_data.startswith("MULTI:"):
        parts = swipe_data.split(":", 2)
        if len(parts) == 3:
            try:
                times = int(parts[1])
                reply_text = parts[2]
                for _ in range(times):
                    try:
                        await event.reply(reply_text)
                        await asyncio.sleep(0.05)
                    except: continue
            except: pass
    elif isinstance(swipe_data, str) and not swipe_data.startswith("MULTI:") and not swipe_data.startswith("RAID:"):
        try:
            await event.reply(swipe_data)
        except: pass

@client.on(events.NewMessage(incoming=True))
async def reply_raid_handler(event):
    if not bot_on or event.out:
        return
    chat_id = event.chat_id
    if chat_id not in state.reply_raid_active:
        return
    sender_id = event.sender_id
    if not sender_id:
        return
    target_data = state.reply_raid_active[chat_id].get(sender_id)
    if not target_data:
        return

    texts = target_data['texts']
    index = target_data['index']
    if index >= len(texts):
        index = 0
    reply_text = texts[index]
    target_data['index'] = (index + 1) % len(texts)
    try:
        await event.reply(reply_text)
    except: pass

# ------------------------- BASE COMMANDS -------------------------
@command("on")
async def cmd_on(event):
    global bot_on
    if not bot_on:
        bot_on = True
        save_bot_state()
        await event.reply("✅ BEBO is now **ON**.")
    else:
        await event.reply("ℹ️ Already ON.")

@command("off")
async def cmd_off(event):
    global bot_on
    if bot_on:
        bot_on = False
        save_bot_state()
        await event.reply("🔴 BEBO is now **OFF**.")
    else:
        await event.reply("ℹ️ Already OFF.")

@command("ping")
async def cmd_ping(event):
    start = time.perf_counter()
    msg = await event.reply("🏓 Pinging...")
    end = time.perf_counter()
    await msg.edit(f"🏓 Pong! 🌀 Latency: `{(end - start) * 1000:.2f} ms`")

@command("echo")
async def cmd_echo(event):
    args = event.raw_text.split(maxsplit=1)
    if len(args) > 1:
        await event.reply(args[1])
    else:
        await event.reply("ℹ️ Usage: `/echo <text>`")

@command("stats")
async def cmd_stats(event):
    uptime_seconds = time.time() - client.start_time
    days, remainder = divmod(uptime_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    stats = f"""📊 **BEBO Stats**
• Uptime: `{int(days)}d {int(hours)}h {int(minutes)}m {int(seconds)}s`
• State: `{'ON' if bot_on else 'OFF'}`
• Flow Mode: `{'ON' if flow_mode else 'OFF'}`
• Owner: `{OWNER_ID}`
• API ID: `{API_ID}`"""
    await event.reply(stats)

@command("info")
async def cmd_info(event):
    chat = await event.get_chat()
    sender = await event.get_sender()
    await event.reply(f"""ℹ️ **Chat Info**
• Chat ID: `{event.chat_id}`
• Chat Title: `{getattr(chat, 'title', 'N/A')}`

👤 **Sender Info**
• ID: `{sender.id}`
• Name: `{utils.get_display_name(sender)}`
• Is Owner: `{sender.id == OWNER_ID}`""")

@command("restart")
async def cmd_restart(event):
    await event.reply("🔄 Restarting BEBO...")
    save_bot_state()
    save_flow_state()
    save_saved_texts()
    os.execv(sys.executable, [sys.executable] + sys.argv)

@command("switch")
async def cmd_switch(event):
    global flow_mode
    flow_mode = not flow_mode
    save_flow_state()
    await event.reply(f"🔄 Flow bot mode is now **{'ON' if flow_mode else 'OFF'}**.\nUse `.flowmenu` for available flow commands.")

# ------------------------- RAID ENGINE COMMANDS (BEBO style) -------------------------
async def start_raid(event, text_list, raid_type):
    user = await get_target(event)
    if not user:
        return
    chat = event.chat
    if raid_type in active_tasks:
        return await event.reply(f"⚠️ A {raid_type} raid is already running. Stop it with `.s{raid_type}` first.")
    active_tasks[raid_type] = asyncio.create_task(raid_loop(event, chat, user, text_list, raid_type))
    await event.reply(f"✅ {raid_type.capitalize()} raid started on {utils.get_display_name(user)}!")

async def raid_loop(event, chat, user, text_list, raid_type):
    try:
        while raid_type in active_tasks:
            text = random.choice(text_list)
            try:
                if user.username:
                    await client.send_message(chat, f"{text} @{user.username}")
                else:
                    await client.send_message(chat, f"{text} {user.first_name}")
            except Exception as e:
                logger.error(f"Raid send error: {e}")
            await asyncio.sleep(0.3)
    except asyncio.CancelledError:
        pass
    finally:
        active_tasks.pop(raid_type, None)

async def stop_raid(event, raid_type):
    if raid_type in active_tasks:
        active_tasks[raid_type].cancel()
        await event.reply(f"✅ {raid_type.capitalize()} raid stopped.")
    else:
        await event.reply(f"ℹ️ No active {raid_type} raid.")

@command("reply")
async def cmd_reply(event):
    await start_raid(event, reply_texts, "reply")
@command("sreply")
async def cmd_sreply(event):
    await stop_raid(event, "reply")

@command("rr")
async def cmd_rr(event):
    await start_raid(event, rr_texts, "rr")
@command("srr")
async def cmd_srr(event):
    await stop_raid(event, "rr")

@command("flag")
async def cmd_flag(event):
    await start_raid(event, flag_texts, "flag")
@command("sflag")
async def cmd_sflag(event):
    await stop_raid(event, "flag")

@command("hrr")
async def cmd_hrr(event):
    await start_raid(event, heart_replies, "hrr")
@command("shrr")
async def cmd_shrr(event):
    await stop_raid(event, "hrr")

@command("replygod")
async def cmd_replygod(event):
    await start_raid(event, attack_list + roast_list, "replygod")
@command("sgod")
async def cmd_sgod(event):
    await stop_raid(event, "replygod")

async def limited_raid_loop(event, chat, user, text, count):
    try:
        for _ in range(count):
            try:
                if user.username:
                    await client.send_message(chat, f"{text} @{user.username}")
                else:
                    await client.send_message(chat, f"{text} {user.first_name}")
            except Exception as e:
                logger.error(f"Limited raid error: {e}")
            await asyncio.sleep(0.2)
    except asyncio.CancelledError:
        pass
    finally:
        active_tasks.pop("limited", None)
        await event.reply("✅ Limited raid finished/stopped.")

@command("replybebo")
async def cmd_replybebo(event):
    args = event.raw_text.split(maxsplit=3)
    if len(args) < 4:
        return await event.reply("⚠️ Usage: `.replybebo @user <text> <count>`")
    try:
        count = int(args[3])
    except ValueError:
        return await event.reply("⚠️ Count must be a number.")
    user = await get_target_from_str(event, args[1])
    if not user:
        return
    if "limited" in active_tasks:
        active_tasks["limited"].cancel()
    active_tasks["limited"] = asyncio.create_task(limited_raid_loop(event, event.chat, user, args[2], count))
    await event.reply(f"✅ Limited raid started on {utils.get_display_name(user)} for {count} messages.")

@command("sstop")
async def cmd_sstop(event):
    if "limited" in active_tasks:
        active_tasks["limited"].cancel()
        await event.reply("✅ Limited raid stopped.")
    else:
        await event.reply("ℹ️ No limited raid running.")

# ------------------------- ORIGINAL BEBO RAID (.raid) -------------------------
@command("raid")
async def cmd_raid(event):
    args = event.text.strip().split()
    if len(args) < 2:
        return await event.reply("**Usage:** `.raid <count>`\nExample: `.raid 50`")
    try:
        count = int(args[1])
    except:
        return await event.respond("❌ **Count must be a valid number!**")

    chat_id = event.chat_id
    # use a separate task name to avoid conflict
    if "bebo_raid" in active_tasks:
        return await event.reply("⚠️ A BEBO raid is already running. Use `.stopraid` first.")
    active_tasks["bebo_raid"] = asyncio.create_task(bebo_raid_loop(event, chat_id, count))
    msg = await event.respond("🚀 **PREPARING TO RAID...**")
    await asyncio.sleep(0.3)
    await msg.edit("⚠️ **TARGET ACQUIRED & LOCKED...**")
    await asyncio.sleep(0.3)
    await msg.edit(f"🔥 **BEBO RAID INITIATED: {count} TOXIC MESSAGES!**")

async def bebo_raid_loop(event, chat_id, count):
    try:
        for _ in range(count):
            if "bebo_raid" not in active_tasks:
                break
            try:
                text = random.choice(RAID_TEXTS)
                await client.send_message(chat_id, text)
                await asyncio.sleep(0.1)
            except Exception as e:
                logger.error(f"BEBO raid error: {e}")
        if "bebo_raid" in active_tasks:
            await client.send_message(chat_id, "✅ **BEBO RAID SUCCESSFULLY COMPLETED!**")
    except asyncio.CancelledError:
        pass
    finally:
        active_tasks.pop("bebo_raid", None)

@command("stopraid")
async def cmd_stopraid(event):
    if "bebo_raid" in active_tasks:
        active_tasks["bebo_raid"].cancel()
        await event.reply("🛑 **BEBO RAID FORCE STOPPED!**")
    else:
        await event.reply("ℹ️ No active BEBO raid.")

# ------------------------- SPRAY COMMANDS (BEBO) -------------------------
async def spray_loop(event, chat, text, count, delay):
    try:
        for _ in range(count):
            try:
                await client.send_message(chat, text)
            except Exception as e:
                logger.error(f"Spray send error: {e}")
            await asyncio.sleep(delay)
    except asyncio.CancelledError:
        pass
    finally:
        active_tasks.pop("spray", None)

async def random_spray_loop(event, chat, text_list, count, delay):
    try:
        for _ in range(count):
            try:
                await client.send_message(chat, random.choice(text_list))
            except Exception as e:
                logger.error(f"Random spray send error: {e}")
            await asyncio.sleep(delay)
    except asyncio.CancelledError:
        pass
    finally:
        active_tasks.pop("spray", None)

async def multispray_loop(event, chat, lines, delay):
    try:
        while "spray" in active_tasks:
            for line in lines:
                if "spray" not in active_tasks:
                    break
                try:
                    await client.send_message(chat, line)
                except Exception as e:
                    logger.error(f"Multi spray error: {e}")
                await asyncio.sleep(delay)
    except asyncio.CancelledError:
        pass
    finally:
        active_tasks.pop("spray", None)

@command("spray")
async def cmd_spray(event):
    args = event.raw_text.split(maxsplit=1)
    if len(args) < 2:
        return await event.reply("⚠️ Usage: `.spray <text>`")
    if "spray" in active_tasks:
        return await event.reply("⚠️ A spray is already running. Use `.stopspray` first.")
    active_tasks["spray"] = asyncio.create_task(spray_loop(event, event.chat, args[1], 10, spray_delay))
    await event.reply(f"✅ Spray started for 10 messages with delay {spray_delay}s.")

@command("dspray")
async def cmd_dspray(event):
    args = event.raw_text.split(maxsplit=1)
    if len(args) < 2:
        return await event.reply("⚠️ Usage: `.dspray <text>`")
    try:
        async for msg in client.iter_messages(event.chat, limit=10):
            await msg.delete()
            await asyncio.sleep(0.1)
    except Exception as e:
        logger.warning(f"Could not delete messages: {e}")
    if "spray" in active_tasks:
        active_tasks["spray"].cancel()
    active_tasks["spray"] = asyncio.create_task(spray_loop(event, event.chat, args[1], 10, spray_delay))
    await event.reply(f"✅ Deleted 10 messages and started spray.")

@command("tspray")
async def cmd_tspray(event):
    args = event.raw_text.split(maxsplit=3)
    if len(args) < 4:
        return await event.reply("⚠️ Usage: `.tspray <count> <delay_sec> <text>`")
    try:
        count = int(args[1])
        delay = float(args[2])
        text = args[3]
    except ValueError:
        return await event.reply("⚠️ Count and delay must be numbers.")
    if "spray" in active_tasks:
        active_tasks["spray"].cancel()
    active_tasks["spray"] = asyncio.create_task(spray_loop(event, event.chat, text, count, delay))
    await event.reply(f"✅ Timed spray started: {count} messages with delay {delay}s.")

@command("rspray")
async def cmd_rspray(event):
    if "spray" in active_tasks:
        active_tasks["spray"].cancel()
    text_list = saved_texts if saved_texts else all_texts
    if not text_list:
        return await event.reply("⚠️ No texts available. Add some with `.addtext`.")
    active_tasks["spray"] = asyncio.create_task(random_spray_loop(event, event.chat, text_list, 20, spray_delay))
    await event.reply(f"✅ Random spray started (20 messages from {len(text_list)} texts).")

@command("multispray")
async def cmd_multispray(event):
    args = event.raw_text.split(maxsplit=1)
    if len(args) < 2:
        return await event.reply("⚠️ Usage: `.multispray <t1|t2|...>`")
    lines = [line.strip() for line in args[1].split("|") if line.strip()]
    if not lines:
        return await event.reply("⚠️ No valid lines.")
    if "spray" in active_tasks:
        active_tasks["spray"].cancel()
    active_tasks["spray"] = asyncio.create_task(multispray_loop(event, event.chat, lines, spray_delay))
    await event.reply(f"✅ Multi-spray started with {len(lines)} lines.")

@command("countspray")
async def cmd_countspray(event):
    args = event.raw_text.split(maxsplit=2)
    if len(args) < 3:
        return await event.reply("⚠️ Usage: `.countspray <count> <text>`")
    try:
        count = int(args[1])
        text = args[2]
    except ValueError:
        return await event.reply("⚠️ Count must be a number.")
    if "spray" in active_tasks:
        active_tasks["spray"].cancel()
    active_tasks["spray"] = asyncio.create_task(spray_loop(event, event.chat, text, count, spray_delay))
    await event.reply(f"✅ Count spray started: {count} messages.")

@command("spraydelay")
async def cmd_spraydelay(event):
    global spray_delay
    args = event.raw_text.split(maxsplit=1)
    if len(args) < 2:
        return await event.reply(f"ℹ️ Current spray delay: {spray_delay}s")
    try:
        new_delay = float(args[1])
        if new_delay < 0.1:
            return await event.reply("⚠️ Delay too small, min 0.1s")
        spray_delay = new_delay
        await event.reply(f"✅ Spray delay set to {spray_delay}s")
    except ValueError:
        await event.reply("⚠️ Invalid delay. Use a number.")

@command("stopspray")
async def cmd_stopspray(event):
    if "spray" in active_tasks:
        active_tasks["spray"].cancel()
        await event.reply("✅ Spray stopped.")
    else:
        await event.reply("ℹ️ No active spray.")

# ------------------------- ADVANCED SPAM (BEBO style) -------------------------
@command("advspam")
async def advspam_cmd(event):
    args = event.text.strip().split(None, 2)
    if len(args) < 2:
        return await event.respond("**Usage:** `.advspam <mode> <text>`\n**Modes:** fast, medium, slow, burst, random, tsunami, nightmare")
    mode = args[1].lower()
    if len(args) < 3:
        return await event.respond("❌ **Provide message!**")
    text = args[2]
    chat_id = event.chat_id
    valid_modes = ['fast', 'medium', 'slow', 'burst', 'random', 'tsunami', 'nightmare']
    if mode not in valid_modes:
        return await event.respond(f"❌ **Invalid mode!**")
    state.adv_spam_active[chat_id] = f"{mode}:{text}"
    msg = await event.respond("🚀 **PREPARING SPAM ENGINE...**")
    await asyncio.sleep(0.3)
    await msg.edit(f"📢 **SPAM ON:** {mode.upper()}")

    async def spam_task():
        while chat_id in state.adv_spam_active:
            try:
                spam_data = state.adv_spam_active[chat_id]
                if ':' not in spam_data:
                    break
                current_mode, spam_text = spam_data.split(':', 1)

                if current_mode == 'fast':
                    await client.send_message(chat_id, spam_text)
                    await asyncio.sleep(0.1)
                elif current_mode == 'medium':
                    await client.send_message(chat_id, spam_text)
                    await asyncio.sleep(0.5)
                elif current_mode == 'slow':
                    await client.send_message(chat_id, spam_text)
                    await asyncio.sleep(2)
                elif current_mode == 'burst':
                    for _ in range(10):
                        await client.send_message(chat_id, spam_text)
                        await asyncio.sleep(0.01)
                    await asyncio.sleep(5)
                elif current_mode == 'random':
                    await client.send_message(chat_id, spam_text)
                    await asyncio.sleep(random.uniform(0.1, 3.0))
                elif current_mode == 'tsunami':
                    for _ in range(50):
                        await client.send_message(chat_id, spam_text)
                        await asyncio.sleep(0.01)
                    await asyncio.sleep(10)
                elif current_mode == 'nightmare':
                    for _ in range(5):
                        await client.send_message(chat_id, spam_text)
                        await asyncio.sleep(0.01)
                    await asyncio.sleep(1)
            except Exception:
                continue
        if chat_id in state.adv_spam_active:
            del state.adv_spam_active[chat_id]

    asyncio.create_task(spam_task())

@command("stopadvspam")
async def stopadvspam_cmd(event):
    chat_id = event.chat_id
    if chat_id in state.adv_spam_active:
        del state.adv_spam_active[chat_id]
        await event.respond("✅ **ADV SPAM OFF**")

# Alias .spam to .advspam
@command("spam")
async def spam_alias(event):
    # Redirect to advspam
    await advspam_cmd(event)

# ------------------------- TEXT MANAGER -------------------------
@command("addtext")
async def cmd_addtext(event):
    args = event.raw_text.split(maxsplit=1)
    if len(args) < 2:
        return await event.reply("⚠️ Usage: `.addtext <text>`")
    saved_texts.append(args[1])
    save_saved_texts()
    await event.reply(f"✅ Text added. Total: {len(saved_texts)}")

@command("listtexts")
async def cmd_listtexts(event):
    if not saved_texts:
        return await event.reply("ℹ️ No saved texts.")
    text_list = "\n".join([f"{i+1}. {t[:50]}..." if len(t)>50 else f"{i+1}. {t}" for i,t in enumerate(saved_texts)])
    await event.reply(f"📝 **Saved Texts ({len(saved_texts)})**\n{text_list}")

@command("edittext")
async def cmd_edittext(event):
    args = event.raw_text.split(maxsplit=2)
    if len(args) < 3:
        return await event.reply("⚠️ Usage: `.edittext <index> <new_text>`")
    try:
        idx = int(args[1]) - 1
        if idx < 0 or idx >= len(saved_texts):
            return await event.reply("⚠️ Invalid index.")
        saved_texts[idx] = args[2]
        save_saved_texts()
        await event.reply(f"✅ Text {idx+1} updated.")
    except ValueError:
        await event.reply("⚠️ Index must be a number.")

@command("deltext")
async def cmd_deltext(event):
    args = event.raw_text.split(maxsplit=1)
    if len(args) < 2:
        return await event.reply("⚠️ Usage: `.deltext <index>`")
    try:
        idx = int(args[1]) - 1
        if idx < 0 or idx >= len(saved_texts):
            return await event.reply("⚠️ Invalid index.")
        removed = saved_texts.pop(idx)
        save_saved_texts()
        await event.reply(f"✅ Removed text: `{removed[:30]}...`")
    except ValueError:
        await event.reply("⚠️ Index must be a number.")

@command("cleartext")
async def cmd_cleartext(event):
    global saved_texts
    saved_texts.clear()
    save_saved_texts()
    await event.reply("✅ All saved texts cleared.")

# ------------------------- FAST GC ENGINE -------------------------
fast_gc_trigger = None
fast_gc_template = None

@command("fastgc")
async def cmd_fastgc(event):
    global fast_gc_trigger, fast_gc_template
    args = event.raw_text.split(maxsplit=3)
    if len(args) < 4 or args[1].lower() != "set":
        return await event.reply("⚠️ Usage: `.fastgc set <emoji> <template>`")
    fast_gc_trigger = args[2]
    fast_gc_template = args[3]
    await event.reply(f"✅ Fast GC set: trigger '{fast_gc_trigger}' → template '{fast_gc_template}'")

@command("fastgc stop")
async def cmd_fastgc_stop(event):
    global fast_gc_trigger, fast_gc_template
    fast_gc_trigger = None
    fast_gc_template = None
    await event.reply("✅ Fast GC stopped.")

@client.on(events.NewMessage())
async def fast_gc_handler(event):
    if fast_gc_trigger is None or fast_gc_template is None:
        return
    if event.sender_id == OWNER_ID:
        return
    if event.raw_text and fast_gc_trigger in event.raw_text:
        user = await event.get_sender()
        name = utils.get_display_name(user)
        reply = fast_gc_template.replace("{user}", name).replace("{username}", user.username if user.username else name)
        await event.reply(reply)

# ------------------------- ADMIN COMMANDS -------------------------
async def get_user_from_arg(event):
    args = event.raw_text.split(maxsplit=1)
    if len(args) < 2:
        await event.reply("⚠️ Please specify a user (username or ID).")
        return None
    target = args[1].strip()
    try:
        if target.startswith("@"):
            target = target[1:]
        if target.isdigit():
            user = await client.get_entity(int(target))
        else:
            user = await client.get_entity(target)
        return user
    except Exception as e:
        await event.reply(f"❌ Could not find user: {e}")
        return None

@command("mute")
async def cmd_mute(event):
    if not event.is_group:
        return await event.reply("⚠️ This command only works in groups.")
    user = await get_user_from_arg(event)
    if not user:
        return
    try:
        rights = ChatBannedRights(
            until_date=None,
            send_messages=True, send_media=True, send_stickers=True,
            send_gifs=True, send_games=True, send_inline=True, send_polls=True,
            change_info=False, invite_users=False, pin_messages=False
        )
        await client.edit_permissions(event.chat_id, user, rights)
        await event.reply(f"🔇 Muted {utils.get_display_name(user)}.")
    except Exception as e:
        await event.reply(f"❌ Failed to mute: {e}")

@command("unmute")
async def cmd_unmute(event):
    if not event.is_group:
        return await event.reply("⚠️ This command only works in groups.")
    user = await get_user_from_arg(event)
    if not user:
        return
    try:
        rights = ChatBannedRights(
            until_date=None,
            send_messages=False, send_media=False, send_stickers=False,
            send_gifs=False, send_games=False, send_inline=False, send_polls=False
        )
        await client.edit_permissions(event.chat_id, user, rights)
        await event.reply(f"🔊 Unmuted {utils.get_display_name(user)}.")
    except Exception as e:
        await event.reply(f"❌ Failed to unmute: {e}")

@command("demote")
async def cmd_demote(event):
    if not event.is_group:
        return await event.reply("⚠️ This command only works in groups.")
    user = await get_user_from_arg(event)
    if not user:
        return
    try:
        rights = ChatAdminRights(
            post_messages=False, add_admins=False, invite_users=False,
            change_info=False, ban_users=False, pin_messages=False,
            manage_call=False, anonymous=False, manage_chat=False,
            delete_messages=False, restrict_users=False
        )
        await client.edit_admin(event.chat_id, user, rights)
        await event.reply(f"⬇️ Demoted {utils.get_display_name(user)}.")
    except Exception as e:
        await event.reply(f"❌ Failed to demote: {e}")

@command("promote")
async def cmd_promote(event):
    if not event.is_group:
        return await event.reply("⚠️ This command only works in groups.")
    user = await get_user_from_arg(event)
    if not user:
        return
    try:
        rights = ChatAdminRights(
            post_messages=True, add_admins=False, invite_users=True,
            change_info=True, ban_users=True, pin_messages=True,
            manage_call=True, anonymous=False, manage_chat=True,
            delete_messages=True, restrict_users=True
        )
        await client.edit_admin(event.chat_id, user, rights)
        await event.reply(f"⬆️ Promoted {utils.get_display_name(user)}.")
    except Exception as e:
        await event.reply(f"❌ Failed to promote: {e}")

@command("kick")
async def cmd_kick(event):
    if not event.is_group:
        return await event.reply("⚠️ This command only works in groups.")
    user = await get_user_from_arg(event)
    if not user:
        return
    try:
        await client.kick_participant(event.chat_id, user)
        await event.reply(f"👢 Kicked {utils.get_display_name(user)}.")
    except Exception as e:
        await event.reply(f"❌ Failed to kick: {e}")

@command("ban")
async def cmd_ban(event):
    if not event.is_group:
        return await event.reply("⚠️ This command only works in groups.")
    user = await get_user_from_arg(event)
    if not user:
        return
    try:
        rights = ChatBannedRights(
            until_date=None,
            view_messages=True, send_messages=True, send_media=True,
            send_stickers=True, send_gifs=True, send_games=True,
            send_inline=True, send_polls=True, change_info=True,
            invite_users=True, pin_messages=True
        )
        await client.edit_permissions(event.chat_id, user, rights)
        await event.reply(f"🚫 Banned {utils.get_display_name(user)}.")
    except Exception as e:
        await event.reply(f"❌ Failed to ban: {e}")

# ------------------------- MENU COMMANDS -------------------------
@command("menu")
async def cmd_menu(event):
    menu = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
      💖  BEBO ULTIMATE  💖
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  📌 .menu      → This menu
  📌 .flowmenu  → Flow Bot menu
  📌 .advmenu   → Advanced Security & Tools Menu
  📌 .about     → About BEBO
  📌 .banner    → Show ASCII art

【 🛠️ 𝗕𝗔𝗦𝗜𝗖 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 】
  /on, /off, /ping, /echo, /stats, /info, /restart, /switch

【 ⚔️ 𝗥𝗔𝗜𝗗 𝗘𝗡𝗚𝗜𝗡𝗘 】
  💬 Reply  → .reply @user   | .sreply
  🤣 RR     → .rr @user      | .srr
  🚩 Flag   → .flag @user    | .sflag
  💗 Heart  → .hrr @user     | .shrr
  😈 God    → .replygod @user| .sgod
  📌 Limited → .replybebo @user <text> <count> | .sstop
  ⚡ Super  → .superraid @user | .stopsuper
  🔥 BEBO Raid → .raid <count> | .stopraid

【 💣 𝗦𝗣𝗔𝗠 𝗦𝗬𝗦𝗧𝗘𝗠 】
  ✦ .spam <mode> <text> (fast, medium, slow, burst, random, tsunami, nightmare)
  ✦ .spray <text>          → 10x spray
  ✦ .dspray <text>         → delete & spray
  ✦ .tspray <count> <delay> <text>
  ✦ .rspray                → random text spam
  ✦ .multispray <text1|text2|...>
  ✦ .countspray <n> <text>
  ✦ .spraydelay <seconds>
  ✦ .stopspray / .stopadvspam

【 📝 𝗧𝗘𝗫𝗧 𝗠𝗔𝗡𝗔𝗚𝗘𝗥 】
  .addtext, .listtexts, .edittext, .deltext, .cleartext

【 🚀 𝗙𝗔𝗦𝗧 𝗚𝗖 】
  .fastgc set <emoji> <template>   | .fastgc stop

【 👑 𝗔𝗗𝗠𝗜𝗡 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 】
  .mute, .unmute, .promote, .demote, .kick, .ban
  .pin (reply), .unpin, .slowmode <sec>, .setgrouptitle <title>
  .setgrouppic (reply to photo), .adminlist, .banlist
  .purge <n>  (delete n messages)

【 ✨ 𝗨𝗧𝗜𝗟𝗜𝗧𝗬 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 】
  .id @user      → get user/chat ID
  .tagall [text] → mention everyone
  .warn @user    → warn a user
  .kickme        → bot leaves the group
  .join <link>   → join group via link
  .setpfp (reply) → change bot's profile pic
  .setname <name> → change bot's name
  .setbio <bio>   → change bot's bio
  .autoreply on/off → toggle auto‑reply

【 🎭 𝗙𝗨𝗡 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 】
  .motivate, .truth, .dare, .shayari, .joke, .quote

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
       💖  BEBO — 𝗔𝗹𝗹 𝗥𝗶𝗴𝗵𝘁𝘀 𝗥𝗲𝘀𝗲𝗿𝘃𝗲𝗱
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """
    await event.reply(menu)

@command("advmenu")
async def cmd_advmenu(event):
    menu = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   🛡️  BEBO ADVANCED SECURITY & TOOLS  🛡️
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【 🗑️ 𝗠𝗨𝗧𝗘 𝗖𝗢𝗡𝗧𝗥𝗢𝗟𝗦 】
  • .sabchup / .speakall
  • .chup / .bol (reply to user)
  • .safe @user

【 💣 𝗔𝗗𝗩𝗔𝗡𝗖𝗘𝗗 𝗦𝗣𝗔𝗠 & 𝗥𝗔𝗜𝗗 】
  • .advspam <mode> <text> (fast, medium, slow, burst, random, tsunami, nightmare)
  • .stopadvspam
  • .replyraid @user | .stopreplyraid
  • .autoswipe <text> | .stopautoswipe
  • .advmultireply <n> <text> | .stopadvmultireply

【 🔄 𝗡𝗔𝗠𝗘 𝗖𝗢𝗡𝗧𝗥𝗢𝗟𝗦 】
  • .namechange [mode] [ms] (normal, time, emoji, owns, enters, dad)
  • .namedelay <ms> | .stopnamechange
  • .blitz [mode] | .stopblitz

【 🔐 𝗦𝗘𝗖𝗨𝗥𝗜𝗧𝗬 𝗟𝗢𝗖𝗞𝗦 】
  • .lockname | .lockgroup | .unlockgroup
  • .lockchat | .unlockchat | .locknamechange | .unlocknamechange

【 🛡️ 𝗣𝗥𝗢𝗧𝗘𝗖𝗧𝗜𝗢𝗡 & 𝗘𝗠𝗘𝗥𝗚𝗘𝗡𝗖𝗬 】
  • .boost on/off | .assist on/off | .perf
  • .terminate | .killname | .dominate | .stopdominate
  • .emergency | .stopemergency

【 📦 𝗨𝗧𝗜𝗟𝗜𝗧𝗜𝗘𝗦 】
  • .makegc <name> | .lockswipe @user <text>
  • .hindivoice <text> (if module available)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """
    await event.reply(menu)

@command("flowmenu")
async def cmd_flowmenu(event):
    menu = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
      💖  BEBO FLOW BOT  💖
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  🌊 This is the high‑speed flow engine.
  Use `.swipe` to start a swipe flood.

【 🌊 𝗙𝗟𝗢𝗪 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 】
  ✦ .swipe <text>           → swipe with custom text
  ✦ .swipe                  → swipe using default texts
  ✦ .stopswipe              → stop swipe flood

【 🚀 𝗙𝗟𝗢𝗪 𝗦𝗣𝗘𝗘𝗗 】
  ✦ .flowdelay <seconds>    → set delay between messages
  ✦ .flowcount <n>          → set number of messages per swipe

【 💡 𝗧𝗜𝗣 】
  Swipe uses the powerful text library from BEBO.
  You can also add your own texts with `.addtext`.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
       💖  BEBO — 𝗙𝗹𝗼𝘄 𝘄𝗶𝘁𝗵 𝗣𝗼𝘄𝗲𝗿
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """
    await event.reply(menu)

@command("help")
async def cmd_help(event):
    await cmd_menu(event)

# ------------------------- FLOW BOT COMMANDS -------------------------
flow_delay = 0.2
flow_count = 30

@flow_command("swipe")
async def cmd_swipe(event):
    args = event.raw_text.split(maxsplit=1)
    if len(args) > 1:
        text = args[1]
        await event.reply(f"🌊 Swiping with custom text: {text[:30]}...")
    else:
        if saved_texts:
            text = random.choice(saved_texts)
        else:
            text = random.choice(all_texts)
        await event.reply(f"🌊 Swiping with random text.")
    chat = event.chat
    
    if "swipe" in active_tasks:
        active_tasks["swipe"].cancel()
        
    active_tasks["swipe"] = asyncio.create_task(swipe_loop(event, chat, text))
    await event.reply(f"✅ Swipe started! {flow_count} messages with delay {flow_delay}s. Use .stopswipe to stop.")

@flow_command("stopswipe")
async def cmd_stopswipe(event):
    if "swipe" in active_tasks:
        active_tasks["swipe"].cancel()
        await event.reply("✅ Swipe stopped.")
    else:
        await event.reply("ℹ️ No active swipe.")

@flow_command("flowdelay")
async def cmd_flowdelay(event):
    global flow_delay
    args = event.raw_text.split(maxsplit=1)
    if len(args) < 2:
        return await event.reply(f"ℹ️ Current flow delay: {flow_delay}s")
    try:
        new_delay = float(args[1])
        if new_delay < 0.05:
            return await event.reply("⚠️ Delay too small, min 0.05s")
        flow_delay = new_delay
        await event.reply(f"✅ Flow delay set to {flow_delay}s")
    except ValueError:
        await event.reply("⚠️ Invalid delay.")

@flow_command("flowcount")
async def cmd_flowcount(event):
    global flow_count
    args = event.raw_text.split(maxsplit=1)
    if len(args) < 2:
        return await event.reply(f"ℹ️ Current flow count: {flow_count}")
    try:
        new_count = int(args[1])
        if new_count < 1:
            return await event.reply("⚠️ Count must be >= 1")
        flow_count = new_count
        await event.reply(f"✅ Flow count set to {flow_count}")
    except ValueError:
        await event.reply("⚠️ Invalid count.")

async def swipe_loop(event, chat, text):
    try:
        for _ in range(flow_count):
            if not flow_mode or "swipe" not in active_tasks:
                break
            try:
                await client.send_message(chat, text)
            except Exception as e:
                logger.error(f"Swipe send error: {e}")
            await asyncio.sleep(flow_delay)
    except asyncio.CancelledError:
        pass
    finally:
        active_tasks.pop("swipe", None)

# ------------------------- ANIMATION & BEAUTIFICATION -------------------------
@command("start")
async def cmd_start(event):
    msg = await event.reply("⏳ **Starting BEBO...**")
    for i in range(1, 11):
        bar = "█" * i + "░" * (10 - i)
        await msg.edit(f"⏳ **Loading BEBO**  [{bar}] {i*10}%")
        await asyncio.sleep(0.3)
    await asyncio.sleep(0.3)
    await cmd_menu(event)
    await msg.delete()

@command("welcome")
async def cmd_welcome(event):
    welcome_msg = f"""
╔══════════════════════════════════════════╗
║                                          ║
║   ✨  𝐖𝐄𝐋𝐂𝐎𝐌𝐄  𝐓𝐎  𝐁𝐄𝐁𝐎  ✨     ║
║                                          ║
║   💖  The most powerful userbot          ║
║   ⚡  Fast, reliable, and stylish        ║
║                                          ║
║   🛠️  Use `.menu` to explore            ║
║   🌊  Use `.flowmenu` for Flow mode      ║
║                                          ║
║   🎀  Made with ❤️ for the community    ║
║                                          ║
╚══════════════════════════════════════════╝

{BANNER}
    """
    await event.reply(welcome_msg)

@command("about")
async def cmd_about(event):
    about = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
      💖  𝐀𝐁𝐎𝐔𝐓  𝐁𝐄𝐁𝐎  💖
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  🔹 **Version** : 4.0 (Ultimate Dynamic Edition)
  🔹 **Author**  : BEBO Team
  🔹 **License** : All Rights Reserved
  🔹 **Language** : Python (Telethon)

  🌟 **Features** :
  • Merged BEBO engines
  • Advanced Security & Defense protocols
  • Ultra‑fast raid & spam (Tsunami, Blitz)
  • Intelligent Auto-Delete & Smart Mute
  • Flow mode with swipe flood
  • 500+ built‑in texts
  • Cloud dummy server

  💡 **Credits** : Powered by Telethon
  🛡️ **BEBO** — Built with ❤️.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """
    await event.reply(about)

BANNER = r"""
  ╔═╗╦ ╦╔═╗╔═╗╔═╗
  ║ ╦║ ║║ ╦║╣ ╚═╗
  ╚═╝╚═╝╚═╝╚═╝╚═╝
  ╔═╗╔╗╔╔═╗╦ ╦╔═╗
  ╠═╣║║║║ ╦║ ║║╣
  ╩ ╩╝╚╝╚═╝╚═╝╚═╝
         💖 𝐁𝐄𝐁𝐎 💖
"""
@command("banner")
async def cmd_banner(event):
    await event.reply(f"`{BANNER}`")

# ------------------------- UTILITIES (BEBO style) -------------------------
@command("sabchup")
async def sabchup_cmd(event):
    chat_id = event.chat_id
    msg = await event.respond("🔒 **LOCKING ALL MESSAGES...**")
    await asyncio.sleep(0.3)
    state.auto_delete_chats[chat_id] = True
    state.save_auto_delete()
    await msg.edit("🤐 **SABCHUP MODE ON** (0.05s delay)")

@command("speakall")
async def speakall_cmd(event):
    chat_id = event.chat_id
    msg = await event.respond("🔓 **UNLOCKING MESSAGES...**")
    await asyncio.sleep(0.3)
    if chat_id in state.auto_delete_chats:
        del state.auto_delete_chats[chat_id]
        state.save_auto_delete()
        if chat_id in state.delete_target_users:
            del state.delete_target_users[chat_id]
        if chat_id in state.delete_target_usernames:
            del state.delete_target_usernames[chat_id]
        state.save_delete_targets()
    await msg.edit("🗣️ **SPEAKALL - Auto-delete OFF**")

@command("chup")
async def deluser_cmd(event):
    chat_id = event.chat_id
    if event.is_reply:
        reply_msg = await event.get_reply_message()
        user_id = reply_msg.sender_id
        try:
            sender = await reply_msg.get_sender()
            username = sender.username
        except:
            username = None
        state.add_delete_target(chat_id, user_id, username)
        if not state.auto_delete_chats.get(chat_id, False):
            state.auto_delete_chats[chat_id] = True
            state.save_auto_delete()
        msg = await event.respond("🎯 **TARGET ACQUIRED...**")
        await asyncio.sleep(0.3)
        await msg.edit(f"🤐 **CHUP!** (User muted forever)")
    else:
        await event.respond("Reply to a message with `.chup`")

@command("bol")
async def bol_cmd(event):
    chat_id = event.chat_id
    if event.is_reply:
        reply_msg = await event.get_reply_message()
        user_id = reply_msg.sender_id
        try:
            sender = await reply_msg.get_sender()
            username = sender.username
        except:
            username = None
        if chat_id in state.delete_target_users:
            state.delete_target_users[chat_id].discard(user_id)
        if chat_id in state.delete_target_usernames and username:
            state.delete_target_usernames[chat_id].discard(username.lower())
        state.save_delete_targets()
        msg = await event.respond("🔄 **RELEASING TARGET...**")
        await asyncio.sleep(0.3)
        await msg.edit(f"🗣️ **BOL!** (User unmuted)")
    else:
        await event.respond("Reply to a message with `.bol`")

@command("safe")
async def safe_cmd(event):
    args = event.text.strip().split()[1:]
    if not args and not event.is_reply:
        if not state.safe_users:
            return await event.respond("🛡️ **Safe list empty**\nUse: `.safe @user`")
        else:
            return await event.respond(f"🛡️ **Safe users:** {len(state.safe_users)}")
    if event.is_reply:
        reply_msg = await event.get_reply_message()
        user_id = reply_msg.sender_id
        try:
            sender = await reply_msg.get_sender()
            username = sender.username
        except:
            username = None
        state.add_safe_user(user_id, username)
        return await event.respond(f"✅ **Protected user**")
    for arg in args:
        username = arg.lstrip('@')
        try:
            user = await client.get_entity(username)
            state.add_safe_user(user.id, username)
        except:
            pass
    await event.respond(f"✅ **Protected {len(args)} users**")

@client.on(events.NewMessage(pattern=r'^\.boost (on|off)$'))
async def boost_cmd(event):
    if not await is_authorized(event):
        return
    global BOOST_MODE, CFG
    BOOST_MODE = event.pattern_match.group(1) == "on"
    CFG = BOOST.copy() if BOOST_MODE else NORMAL.copy()
    await event.respond(f"⚡ **BOOST MODE:** {'ON' if BOOST_MODE else 'OFF'}")
    await event.delete()

@client.on(events.NewMessage(pattern=r'^\.assist (on|off)$'))
async def assist_cmd(event):
    if not await is_authorized(event):
        return
    global CRITICAL_MODE, CFG
    CRITICAL_MODE = event.pattern_match.group(1) == "on"
    CFG = CRIT.copy() if CRITICAL_MODE else NORMAL.copy()
    await event.respond(f"🛡️ **CRITICAL MODE:** {'ON' if CRITICAL_MODE else 'OFF'}")
    await event.delete()

@command("perf")
async def perf_cmd(event):
    up = int(time.monotonic() - state.metrics["start"])
    rate = state.metrics["msg"] / max(1, up)
    await event.respond(
        f"⟦ LIVE PERFORMANCE ⟧\n"
        f"Uptime: {up}s\n"
        f"Msg/s: {rate:.2f}\n"
        f"Mutes: {state.metrics['mutes']}\n"
        f"Boost: {BOOST_MODE}\n"
        f"Critical: {CRITICAL_MODE}"
    )
    await event.delete()

@command("autoswipe")
async def autoswipe_cmd(event):
    args = event.text.strip().split(None, 1)
    if len(args) < 2:
        return await event.respond("**Usage:** `.autoswipe <text>`")
    chat_id = event.chat_id
    state.autoswipe_active[chat_id] = args[1]
    await event.respond(f"🔄 **AUTO-SWIPE ON:** {args[1]}")

@command("stopautoswipe")
async def stopautoswipe_cmd(event):
    chat_id = event.chat_id
    if chat_id in state.autoswipe_active:
        del state.autoswipe_active[chat_id]
        await event.respond("✅ **AUTO-SWIPE OFF**")

@command("advmultireply")
async def advmultireply_cmd(event):
    args = event.text.strip().split(None, 2)
    if len(args) < 2:
        return await event.respond("**Usage:** `.advmultireply <times> <text>`")
    try:
        times = int(args[1])
        if times < 1 or times > 50:
            return await event.respond("⚠️ **Times must be between 1-50**")
    except:
        return await event.respond("❌ **Invalid number!**")
    if len(args) < 3:
        return await event.respond("❌ **Please provide a message!**")
    chat_id = event.chat_id
    state.autoswipe_active[chat_id] = f"MULTI:{times}:{args[2]}"
    msg = await event.respond("🔁 **INITIALIZING MULTI-REPLY...**")
    await asyncio.sleep(0.3)
    await msg.edit(f"🔁 **MULTI-REPLY ON**\n📢 Sending {times}x: {args[2]}")

@command("stopadvmultireply")
async def stopadvmultireply_cmd(event):
    chat_id = event.chat_id
    if chat_id in state.autoswipe_active:
        swipe_data = state.autoswipe_active[chat_id]
        if isinstance(swipe_data, str) and swipe_data.startswith("MULTI:"):
            del state.autoswipe_active[chat_id]
            return await event.respond("✅ **MULTI-REPLY OFF**")
    await event.respond("❌ **Multi-reply is not active**")

# Reply raid (from BEBO)
@command("replyraid")
async def reply_raid_cmd(event):
    chat_id = event.chat_id
    target_user_id = None
    target_username = None
    parts = event.text.strip().split()
    if len(parts) > 1:
        username = parts[1].lstrip('@')
        try:
            entity = await client.get_entity(username)
            target_user_id = entity.id
            target_username = username
        except:
            pass

    if not target_user_id and event.is_reply:
        reply_msg = await event.get_reply_message()
        if reply_msg:
            target_user_id = reply_msg.sender_id
            try:
                sender = await reply_msg.get_sender()
                if hasattr(sender, 'username'):
                    target_username = sender.username
            except:
                pass
    if not target_user_id:
        return await event.respond("❌ **Please reply to a user or mention @username**")

    if chat_id not in state.reply_raid_active:
        state.reply_raid_active[chat_id] = {}
    texts = GAALI_LIST.copy()
    state.reply_raid_active[chat_id][target_user_id] = {'texts': texts, 'index': 0}
    msg = await event.respond("🔥 **INITIALIZING REPLY RAID...**")
    await asyncio.sleep(0.3)
    await msg.edit("⚡ **TARGET LOCKED**")
    await asyncio.sleep(0.3)
    await msg.edit(f"💀 **REPLY RAID ON**\n🎯 Target: {target_username or target_user_id}\n📦 Total insults: {len(texts)}")

@command("stopreplyraid")
async def stop_reply_raid_cmd(event):
    chat_id = event.chat_id
    if chat_id in state.reply_raid_active:
        state.reply_raid_active[chat_id].clear()
        del state.reply_raid_active[chat_id]
        msg = await event.respond("🛑 **STOPPING REPLY RAID...**")
        await asyncio.sleep(0.3)
        await msg.edit("✅ **REPLY RAID OFF**")
    else:
        await event.respond("❌ **No active reply raid**")

# Alias for .rr and .srr already defined, but .replyraid and .stopreplyraid now added.

# Name change (from BEBO)
@command("namechange")
async def namechange_cmd(event):
    args = event.text.strip().split()
    delay = 0.1
    mode = "normal"
    if len(args) > 1:
        if args[1].lower() in ['time', 'emoji', 'owns', 'enters', 'dad']:
            mode = args[1].lower()
            if len(args) > 2:
                try:
                    delay = float(args[2]) / 1000
                except:
                    delay = 0.1
        else:
            try:
                delay = float(args[1]) / 1000
            except:
                delay = 0.1

    chat_id = event.chat_id
    try:
        chat = await event.get_chat()
        if not hasattr(chat, 'title'):
            return await event.respond("❌ **Groups only!**")
    except:
        return await event.respond("❌ **Cannot access chat**")

    state.namechange_active[chat_id] = True
    mode_text = {'normal': 'Normal', 'time': '⏰ Time', 'emoji': '😎 Emoji',
                 'owns': '👑 OWNS', 'enters': '🚪 ENTERS', 'dad': '👨 YOUR DAD'}.get(mode, 'Normal')
    msg = await event.respond("🔄 **PREPARING NAME CHANGE MODULE...**")
    await asyncio.sleep(0.3)
    await msg.edit(f"🔄 **NAME CHANGE ON**\n📝 Mode: {mode_text}\n⏱️ {delay*1000:.0f}ms")

    async def namechange_task():
        original_title = chat.title
        counter = 0
        current_delay = delay
        is_channel = hasattr(chat, 'megagroup') or hasattr(chat, 'broadcast')
        while chat_id in state.namechange_active and state.namechange_active[chat_id]:
            try:
                if chat_id in state.namechange_delays:
                    current_delay = state.namechange_delays[chat_id]
                if mode == 'time':
                    new_name = f"⏰ {datetime.now().strftime('%H:%M:%S')} {random.choice(RANDOM_EMOJIS)} {original_title}"
                elif mode == 'emoji':
                    new_name = f"{''.join([random.choice(RANDOM_EMOJIS) for _ in range(5)])} {original_title} {''.join([random.choice(COUNTRY_EMOJIS) for _ in range(3)])}"
                elif mode == 'owns':
                    new_name = f"👑 BEBO OWNS {random.choice(RANDOM_EMOJIS)} {original_title} {random.choice(COUNTRY_EMOJIS)}"
                elif mode == 'enters':
                    new_name = f"🚪 BEBO ENTERS {random.choice(RANDOM_EMOJIS)} {original_title} 🔥"
                elif mode == 'dad':
                    new_name = f"👨 BEBO YOUR DAD {random.choice(RANDOM_EMOJIS)} {original_title} 💀"
                else:
                    new_name = f"{random.choice(RANDOM_EMOJIS)} {original_title} {random.choice(COUNTRY_EMOJIS)} #{counter}"

                if is_channel:
                    await client(EditTitleRequest(channel=chat_id, title=new_name))
                else:
                    await client(EditChatTitleRequest(chat_id=chat_id, title=new_name))
                counter += 1
                await asyncio.sleep(current_delay)
            except Exception:
                continue
        if chat_id in state.namechange_active:
            del state.namechange_active[chat_id]

    asyncio.create_task(namechange_task())

@command("namedelay")
async def namedelay_cmd(event):
    args = event.text.strip().split()
    chat_id = event.chat_id
    if chat_id not in state.namechange_active:
        return await event.respond("❌ **Not active!**")
    if len(args) < 2:
        return await event.respond("⚙️ **Usage:** `.namedelay <ms>`")
    try:
        state.namechange_delays[chat_id] = float(args[1]) / 1000
        await event.respond(f"⚙️ **Delay changed to: {args[1]}ms**")
    except:
        await event.respond("❌ **Invalid delay amount!**")

@command("stopnamechange")
async def stopnamechange_cmd(event):
    chat_id = event.chat_id
    if chat_id in state.namechange_active:
        del state.namechange_active[chat_id]
        await event.respond("✅ **NAME CHANGE STOPPED**")

@command("blitz")
async def blitz_cmd(event):
    chat_id = event.chat_id
    try:
        chat = await event.get_chat()
        if not hasattr(chat, 'title'):
            return
    except:
        return
    
    original_title = chat.title
    is_channel = hasattr(chat, 'megagroup') or hasattr(chat, 'broadcast')
    state.blitz_active[chat_id] = True
    
    msg = await event.respond("⚡ **WARMING UP BLITZ...**")
    await asyncio.sleep(0.3)
    status_msg = await msg.edit(f"⚡ **BEBO BLITZ MODE**\n🎯 100K changes\n💀 3s flood waits")

    async def blitz_task():
        counter = 0
        start_time = time.time()
        flood_waits = 0
        while counter < 100000 and state.blitz_active.get(chat_id):
            try:
                new_name = f"{random.choice(RANDOM_EMOJIS)} {original_title} {random.choice(COUNTRY_EMOJIS)} #{counter}"
                if is_channel:
                    await client(EditTitleRequest(channel=chat_id, title=new_name))
                else:
                    await client(EditChatTitleRequest(chat_id=chat_id, title=new_name))
                counter += 1
                if counter % 1000 == 0:
                    elapsed = time.time() - start_time
                    try:
                        await status_msg.edit(f"⚡ **BEBO BLITZ**\n📊 {counter:,}/100K\n⚡ {counter / max(1, elapsed):.1f}/s\n💀 Floods: {flood_waits}")
                    except:
                        pass
            except Exception as e:
                if 'flood' in str(e).lower():
                    flood_waits += 1
                    await asyncio.sleep(3)
                continue
        if chat_id in state.blitz_active:
            del state.blitz_active[chat_id]
        try:
            await status_msg.edit(f"✅ **BEBO BLITZ COMPLETE OR STOPPED!**\n📊 {counter:,}\n⏱️ {time.time() - start_time:.1f}s\n🔥 DONE!")
        except:
            pass

    asyncio.create_task(blitz_task())

@command("stopblitz")
async def stopblitz_cmd(event):
    chat_id = event.chat_id
    if chat_id in state.blitz_active:
        del state.blitz_active[chat_id]
        await event.respond("✅ **BLITZ STOPPED**")

# Locks
@command("lockname")
async def lockname_cmd(event):
    chat = await event.get_chat()
    state.locked_titles[event.chat_id] = chat.title
    state.save_state()
    await event.respond(f"🔒 **NAME LOCKED BY BEBO:** {chat.title}")

@command("lockgroup")
async def lockgroup_cmd(event):
    state.locked_groups.add(event.chat_id)
    await event.respond("🔐 **GROUP LOCKED BY BEBO**")

@command("unlockgroup")
async def unlockgroup_cmd(event):
    if event.chat_id in state.locked_groups:
        state.locked_groups.remove(event.chat_id)
    await event.respond("🔓 **UNLOCKED BY BEBO**")

@command("lockchat")
async def lockchat_cmd(event):
    state.locked_chat.add(event.chat_id)
    await event.respond("💬 **CHAT LOCKED BY BEBO**")

@command("unlockchat")
async def unlockchat_cmd(event):
    if event.chat_id in state.locked_chat:
        state.locked_chat.remove(event.chat_id)
    await event.respond("💬 **CHAT UNLOCKED BY BEBO**")

@command("locknamechange")
async def locknamechange_cmd(event):
    chat_id = event.chat_id
    chat = await event.get_chat()
    state.locked_name_change.add(chat_id)
    state.locked_titles[chat_id] = chat.title
    state.save_state()
    await event.respond(f"🔒 **NAME CHANGE LOCKED BY BEBO**")

@command("unlocknamechange")
async def unlocknamechange_cmd(event):
    if event.chat_id in state.locked_name_change:
        state.locked_name_change.remove(event.chat_id)
    await event.respond("🔓 **NAME CHANGE UNLOCKED BY BEBO**")

# Terminate, killname, dominate, emergency
@command("terminate")
async def terminate_cmd(event):
    await event.delete()
    chat_id = event.chat_id
    stop_commands = ['.stopadvspam', '.stopspray', '.stopraid', '.stop', '.stopall', '.stopdel',
                     '.stopswipe', '.cancel', '.end', '.halt', '.off', '.disable', '.stopflood', '.stopnamechange']
    status_msg = await event.respond("🛑 **BEBO TERMINATING PROCESSES...**")
    sent = 0
    for cmd in stop_commands:
        try:
            msg = await client.send_message(chat_id, cmd)
            await asyncio.sleep(0.1)
            await msg.delete()
            sent += 1
        except:
            pass
    await status_msg.edit(f"✅ **BEBO SENT {sent} COMMANDS**")
    await asyncio.sleep(2)
    await status_msg.delete()

@command("killname")
async def killname_cmd(event):
    args = event.text.strip().split(None, 1)
    chat_id = event.chat_id
    if len(args) > 1:
        original_name = args[1]
    else:
        try:
            chat = await event.get_chat()
            original_name = chat.title.split()[0]
        except:
            original_name = "Group"
    status_msg = await event.respond("💀 **BEBO IS KILLING NAME CHANGERS...**")
    for cmd in ['.stopnamechange', '.stopname', '.stopnm', '.stop']:
        try:
            msg = await client.send_message(chat_id, cmd)
            await asyncio.sleep(0.05)
            await msg.delete()
        except:
            pass
    try:
        chat = await event.get_chat()
        is_channel = hasattr(chat, 'megagroup') or hasattr(chat, 'broadcast')
        for _ in range(5):
            try:
                if is_channel:
                    await client(EditTitleRequest(channel=chat_id, title=original_name))
                else:
                    await client(EditChatTitleRequest(chat_id=chat_id, title=original_name))
                await asyncio.sleep(0.2)
            except:
                pass
        await status_msg.edit(f"✅ **BEBO TERMINATED THE PROCESS!**\n📝 {original_name}")
    except:
        await status_msg.edit("⚠️ **Sent commands**")
    await asyncio.sleep(2)
    await status_msg.delete()

@command("dominate")
async def dominate_cmd(event):
    chat_id = event.chat_id
    if chat_id in state.adv_spam_active and 'DOMINATE' in str(state.adv_spam_active.get(chat_id, '')):
        return await event.respond("⚠️ **Already active!**")
    all_stop_commands = ['.stop', '.stopall', '.end', '.stopadvspam', '.stopspray', '.stopraid',
                         '.stopnamechange', '.stopdel', '.stopswipe', '.stoppromote', '.stopkick', '.stopban']
    state.adv_spam_active[chat_id] = 'DOMINATE_MODE_ACTIVE'
    msg = await event.respond("🔌 **POWERING UP DOMINATION...**")
    await asyncio.sleep(0.3)
    await msg.edit("👑 **BEBO DOMINATION ON**\n💀 Blocking all enemy bots!")
    async def dominate_task():
        while chat_id in state.adv_spam_active and state.adv_spam_active[chat_id] == 'DOMINATE_MODE_ACTIVE':
            try:
                msg = await client.send_message(chat_id, random.choice(all_stop_commands))
                await asyncio.sleep(0.01)
                try:
                    await msg.delete()
                except:
                    pass
            except:
                continue
    asyncio.create_task(dominate_task())

@command("stopdominate")
async def stopdominate_cmd(event):
    chat_id = event.chat_id
    if chat_id in state.adv_spam_active and 'DOMINATE' in str(state.adv_spam_active.get(chat_id, '')):
        del state.adv_spam_active[chat_id]
        await event.respond("✅ **BEBO DOMINATION STOPPED**")

@command("emergency")
async def emergency_cmd(event):
    chat_id = event.chat_id
    if chat_id in state.emergency_active and state.emergency_active[chat_id]:
        return await event.respond("⚠️ **Already active!**")
    state.emergency_active[chat_id] = True
    msg = await event.respond("⚠️ **WARNING: ENGAGING OVERDRIVE...**")
    await asyncio.sleep(0.3)
    await msg.edit("🚨 **BEBO EMERGENCY MODE** 🚨\n\n💀 **MAXIMUM OVERDRIVE!**\n⚡ 1000 changes/sec\n💥 1000 msgs/sec\n🔁 100x replies\n\n⚠️ **OVERWHELMING SPEED!**")

    async def emergency_namechange():
        try:
            chat = await event.get_chat()
            if not hasattr(chat, 'title'):
                return
            original_title = chat.title
            is_channel = hasattr(chat, 'megagroup') or hasattr(chat, 'broadcast')
            counter = 0
            while chat_id in state.emergency_active and state.emergency_active[chat_id]:
                try:
                    new_name = f"{random.choice(RANDOM_EMOJIS)}💀BEBO EMERGENCY💀 {original_title} #{counter}"
                    if is_channel:
                        await client(EditTitleRequest(channel=chat_id, title=new_name))
                    else:
                        await client(EditChatTitleRequest(chat_id=chat_id, title=new_name))
                    counter += 1
                    await asyncio.sleep(0.001)
                except:
                    await asyncio.sleep(0.001)
        except:
            pass

    async def emergency_spam():
        while chat_id in state.emergency_active and state.emergency_active[chat_id]:
            try:
                await client.send_message(chat_id, "🚨 BEBO EMERGENCY 🚨")
                await asyncio.sleep(0.001)
            except:
                await asyncio.sleep(0.001)

    state.autoswipe_active[chat_id] = "MULTI:100:🚨 BEBO EMERGENCY 🚨"
    asyncio.create_task(emergency_namechange())
    asyncio.create_task(emergency_spam())

@command("stopemergency")
async def stopemergency_cmd(event):
    chat_id = event.chat_id
    if chat_id in state.emergency_active and state.emergency_active[chat_id]:
        state.emergency_active[chat_id] = False
        if chat_id in state.autoswipe_active:
            del state.autoswipe_active[chat_id]
        await event.respond("✅ **BEBO EMERGENCY STOPPED**")

@command("makegc")
async def makegc_cmd(event):
    args = event.text.strip().split(maxsplit=1)
    if len(args) < 2:
        return await event.respond("Usage: `.makegc <name>`")
    title = args[1]
    try:
        msg = await event.respond(f"🛠️ **CREATING CHAT...**")
        await asyncio.sleep(0.3)
        await client(CreateChatRequest(users=[OWNER_ID], title=title))
        await msg.edit(f"✅ **BEBO Created Chat:** {title}")
    except Exception as e:
        await event.respond(f"❌ {str(e)[:50]}")

@command("lockswipe")
async def lockswipe_cmd(event):
    # pattern: .lockswipe @username text
    parts = event.text.strip().split(maxsplit=2)
    if len(parts) < 3:
        return await event.respond("Usage: `.lockswipe @username <text>`")
    username = parts[1].lstrip('@')
    text = parts[2]
    try:
        ent = await client.get_entity(username)
        state.swipe_targets.setdefault(event.chat_id, {})[ent.id] = text
        state.save_state()
        await event.respond(f"🔒 **LOCKED SWIPE BY BEBO:** @{username}")
    except:
        await event.respond("❌ **Failed**")

if GTTS_AVAILABLE:
    @command("hindivoice")
    async def hindivoice_cmd(event):
        args = event.text.strip().split(maxsplit=1)
        if len(args) < 2:
            return await event.respond("Usage: `.hindivoice <text>`")
        text = args[1]
        file_name = f"hindi_{int(time.time())}.ogg"
        try:
            gTTS(text=text, lang="hi").save(file_name)
            await client.send_file(event.chat_id, file_name, voice_note=True)
            os.remove(file_name)
        except Exception as e:
            await event.respond(f"❌ {str(e)[:50]}")
        await event.delete()

# ------------------------- ADDITIONAL UTILITIES (from BEBO) -------------------------
@command("id")
async def cmd_id(event):
    args = event.raw_text.split(maxsplit=1)
    if len(args) > 1:
        target = args[1].strip()
        try:
            if target.startswith("@"):
                target = target[1:]
            if target.isdigit():
                entity = await client.get_entity(int(target))
            else:
                entity = await client.get_entity(target)
            await event.reply(f"🆔 **ID** of `{utils.get_display_name(entity)}` : `{entity.id}`")
        except Exception as e:
            await event.reply(f"❌ Could not fetch ID: {e}")
    else:
        chat = await event.get_chat()
        sender = await event.get_sender()
        reply = f"📌 **Current Chat ID** : `{event.chat_id}`\n👤 **Your ID** : `{sender.id}`\n📛 **Chat Title** : `{getattr(chat, 'title', 'N/A')}`"
        await event.reply(reply)

@command("tagall")
async def cmd_tagall(event):
    if not event.is_group:
        return await event.reply("⚠️ This command only works in groups.")
    args = event.raw_text.split(maxsplit=1)
    custom_text = args[1] if len(args) > 1 else "Attention!"
    try:
        participants = await client.get_participants(event.chat)
        mentions = [f"@{user.username}" if user.username else f"[{user.first_name}](tg://user?id={user.id})" for user in participants if not (user.bot or user.deleted)]
        if not mentions:
            return await event.reply("No active members found.")
        batch_size = 50
        for i in range(0, len(mentions), batch_size):
            batch = mentions[i:i+batch_size]
            await client.send_message(event.chat, f"{custom_text}\n" + " ".join(batch))
            await asyncio.sleep(1)
        await event.reply(f"✅ Tagged {len(mentions)} members.")
    except Exception as e:
        await event.reply(f"❌ Failed to tag all: {e}")

@command("purge")
async def cmd_purge(event):
    args = event.raw_text.split(maxsplit=1)
    if len(args) < 2:
        return await event.reply("⚠️ Usage: `.purge <count>`")
    try:
        count = int(args[1])
        if count < 1 or count > 500:
            return await event.reply("⚠️ Count must be between 1 and 500.")
        deleted = 0
        async for msg in client.iter_messages(event.chat, limit=count+1):
            if msg.id == event.id:
                continue
            await msg.delete()
            deleted += 1
            await asyncio.sleep(0.2)
        await event.reply(f"✅ Purged {deleted} messages.")
    except ValueError:
        await event.reply("⚠️ Count must be a number.")

@command("warn")
async def cmd_warn(event):
    user = await get_user_from_arg(event)
    if not user:
        return
    if user.id in warnings:
        warnings[user.id] += 1
    else:
        warnings[user.id] = 1
    count = warnings[user.id]
    msg = f"⚠️ **{utils.get_display_name(user)}** has been warned ({count}/3)."
    if count >= 3:
        msg += "\n🔨 Auto‑kick activated! Kicking user..."
        await event.reply(msg)
        try:
            await client.kick_participant(event.chat, user)
        except Exception as e:
            await event.reply(f"❌ Could not kick: {e}")
        del warnings[user.id]
    else:
        await event.reply(msg)

@command("kickme")
async def cmd_kickme(event):
    await event.reply("👋 Leaving this group...")
    await client.leave_chat(event.chat)

@command("join")
async def cmd_join(event):
    args = event.raw_text.split(maxsplit=1)
    if len(args) < 2:
        return await event.reply("⚠️ Usage: `.join <invite_link>`")
    try:
        await client.join_channel(args[1].strip())
        await event.reply(f"✅ Joined: {args[1].strip()}")
    except Exception as e:
        await event.reply(f"❌ Failed to join: {e}")

@command("setpfp")
async def cmd_setpfp(event):
    if event.reply_to_msg_id:
        msg = await event.get_reply_message()
        if msg.photo:
            try:
                await client.download_profile_photo(msg.photo, "temp_pfp.jpg")
                await client.set_profile_photo("temp_pfp.jpg")
                os.remove("temp_pfp.jpg")
                await event.reply("✅ Profile picture updated.")
            except Exception as e:
                await event.reply(f"❌ Failed: {e}")
        else:
            await event.reply("⚠️ Reply to a photo message.")
    else:
        await event.reply("⚠️ Reply to a photo with `.setpfp`.")

@command("setname")
async def cmd_setname(event):
    args = event.raw_text.split(maxsplit=1)
    if len(args) < 2:
        return await event.reply("⚠️ Usage: `.setname <name>`")
    try:
        await client.edit_profile(first_name=args[1])
        await event.reply(f"✅ Name changed to: **{args[1]}**")
    except Exception as e:
        await event.reply(f"❌ Failed: {e}")

@command("setbio")
async def cmd_setbio(event):
    args = event.raw_text.split(maxsplit=1)
    if len(args) < 2:
        return await event.reply("⚠️ Usage: `.setbio <bio>`")
    try:
        await client.edit_profile(about=args[1])
        await event.reply(f"✅ Bio updated.")
    except Exception as e:
        await event.reply(f"❌ Failed: {e}")

@command("pin")
async def cmd_pin(event):
    if event.reply_to_msg_id:
        try:
            msg = await event.get_reply_message()
            await client.pin_message(event.chat, msg.id)
            await event.reply("📌 Pinned that message.")
        except Exception as e:
            await event.reply(f"❌ Failed to pin: {e}")
    else:
        await event.reply("⚠️ Reply to a message to pin.")

@command("unpin")
async def cmd_unpin(event):
    try:
        await client.unpin_message(event.chat)
        await event.reply("📌 Unpinned.")
    except Exception as e:
        await event.reply(f"❌ Failed to unpin: {e}")

@command("adminlist")
async def cmd_adminlist(event):
    if not event.is_group:
        return await event.reply("⚠️ This command only works in groups.")
    try:
        admins = [f"• {utils.get_display_name(p)}" async for p in client.iter_participants(event.chat, filter="admin")]
        if admins:
            await event.reply(f"👑 **Admins** :\n" + "\n".join(admins))
        else:
            await event.reply("No admins found.")
    except Exception as e:
        await event.reply(f"❌ Failed: {e}")

@command("banlist")
async def cmd_banlist(event):
    if not event.is_group:
        return await event.reply("⚠️ This command only works in groups.")
    try:
        banned = [f"• {utils.get_display_name(p)}" async for p in client.iter_participants(event.chat, filter="banned")]
        if banned:
            await event.reply(f"🚫 **Banned Users** :\n" + "\n".join(banned))
        else:
            await event.reply("No banned users.")
    except Exception as e:
        await event.reply(f"❌ Failed: {e}")

@command("slowmode")
async def cmd_slowmode(event):
    args = event.raw_text.split(maxsplit=1)
    if len(args) < 2:
        return await event.reply("⚠️ Usage: `.slowmode <seconds>` (0 to disable)")
    try:
        seconds = int(args[1])
        await client.edit_admin(event.chat, ChatAdminRights(slowmode=seconds))
        await event.reply(f"✅ Slow mode set to {seconds} seconds.")
    except Exception as e:
        await event.reply(f"❌ Failed: {e}")

@command("setgrouptitle")
async def cmd_setgrouptitle(event):
    if not event.is_group:
        return await event.reply("⚠️ This command only works in groups.")
    args = event.raw_text.split(maxsplit=1)
    if len(args) < 2:
        return await event.reply("⚠️ Usage: `.setgrouptitle <title>`")
    try:
        await client.edit_group_title(event.chat, args[1])
        await event.reply(f"✅ Group title changed to: **{args[1]}**")
    except Exception as e:
        await event.reply(f"❌ Failed: {e}")

@command("setgrouppic")
async def cmd_setgrouppic(event):
    if not event.is_group:
        return await event.reply("⚠️ This command only works in groups.")
    if event.reply_to_msg_id:
        msg = await event.get_reply_message()
        if msg.photo:
            try:
                await client.download_media(msg.photo, "temp_grouppic.jpg")
                await client.edit_group_photo(event.chat, "temp_grouppic.jpg")
                os.remove("temp_grouppic.jpg")
                await event.reply("✅ Group photo updated.")
            except Exception as e:
                await event.reply(f"❌ Failed: {e}")
        else:
            await event.reply("⚠️ Reply to a photo.")
    else:
        await event.reply("⚠️ Reply to a photo with `.setgrouppic`.")

@command("autoreply")
async def cmd_autoreply(event):
    global auto_reply_on
    args = event.raw_text.split(maxsplit=1)
    if len(args) < 2:
        return await event.reply(f"ℹ️ Auto‑reply is currently **{'ON' if auto_reply_on else 'OFF'}**.")
    if args[1].lower() == "on":
        auto_reply_on = True
        await event.reply("✅ Auto‑reply enabled.")
    elif args[1].lower() == "off":
        auto_reply_on = False
        await event.reply("✅ Auto‑reply disabled.")
    else:
        await event.reply("⚠️ Usage: `.autoreply on/off`")

@client.on(events.NewMessage)
async def auto_reply_handler(event):
    if not auto_reply_on:
        return
    if event.sender_id == OWNER_ID:
        return
    if event.is_group or event.is_private:
        reply = random.choice(saved_texts) if saved_texts else random.choice(all_texts)
        try:
            await event.reply(reply)
        except Exception as e:
            logger.warning(f"Auto‑reply failed: {e}")

@command("superraid")
async def cmd_superraid(event):
    user = await get_target(event)
    if not user:
        return
    chat = event.chat
    raid_types = ["reply", "rr", "flag", "hrr", "replygod"]
    text_lists = {"reply": reply_texts, "rr": rr_texts, "flag": flag_texts, "hrr": heart_replies, "replygod": attack_list + roast_list}
    for rtype in raid_types:
        if rtype in active_tasks:
            active_tasks[rtype].cancel()
    tasks = []
    for rtype in raid_types:
        task = asyncio.create_task(raid_loop(event, chat, user, text_lists[rtype], rtype))
        active_tasks[rtype] = task
        tasks.append(task)
    await event.reply(f"💥 Super raid started on {utils.get_display_name(user)} using all 5 raid types!")

@command("stopsuper")
async def cmd_stopsuper(event):
    stopped = False
    for rtype in ["reply", "rr", "flag", "hrr", "replygod"]:
        if rtype in active_tasks:
            active_tasks[rtype].cancel()
            stopped = True
    if stopped:
        await event.reply("✅ **Super raid stopped.**")
    else:
        await event.reply("ℹ️ No active super raid.")

# ------------------------- FUN COMMANDS -------------------------
motivation_quotes = [
    "Believe you can and you're halfway there. – Theodore Roosevelt",
    "The only way to do great work is to love what you do. – Steve Jobs",
    "Success is not final, failure is not fatal: it is the courage to continue that counts. – Winston Churchill",
    "The future belongs to those who believe in the beauty of their dreams. – Eleanor Roosevelt",
    "It does not matter how slowly you go as long as you do not stop. – Confucius",
    "You are never too old to set another goal or to dream a new dream. – C.S. Lewis",
    "Act as if what you do makes a difference. It does. – William James",
    "Keep your face always toward the sunshine—and shadows will fall behind you. – Walt Whitman",
]
@command("motivate")
async def cmd_motivate(event):
    await event.reply(f"💪 **Motivation** : {random.choice(motivation_quotes)}")

truths = [
    "What is the biggest lie you've ever told?",
    "Have you ever cheated on a test?",
    "What is the most embarrassing thing you've done in public?",
    "Who is your secret crush?",
    "Have you ever lied to your best friend?",
    "What is the most money you've ever found and kept?",
    "Have you ever stolen something?",
    "What is the worst date you've ever been on?",
]
@command("truth")
async def cmd_truth(event):
    await event.reply(f"🔮 **Truth** : {random.choice(truths)}")

dares = [
    "Do 20 push-ups right now.",
    "Sing the national anthem loudly.",
    "Send a random emoji to your last chat.",
    "Speak in a British accent for the next 5 minutes.",
    "Swap your profile picture with a meme for an hour.",
    "Write a poem about the person who sent this command.",
    "Do a handstand for 10 seconds.",
    "Send a voice message saying 'I love BEBO'.",
]
@command("dare")
async def cmd_dare(event):
    await event.reply(f"⚡ **Dare** : {random.choice(dares)}")

shayaris = [
    "तुम्हें देखा तो ये ख़याल आया,\nज़िन्दगी धूप, तुम घना साया।",
    "मोहब्बत की राहें मुश्किल हैं,\nफिर भी हमने ये राह चुनी है।",
    "तेरी यादों में बीती है रात,\nसुबह हुई तो फिर से तेरी बात।",
    "तेरे बिना दिल है बेकरार,\nमाँग ले मुझसे हर बार प्यार।",
    "हमने चाहा तो बहुत चाहा,\nपर वफ़ा ना मिली कोई भी।",
    "ज़िंदगी एक सफ़र है,\nतू मेरी मंज़िल है।"
]
@command("shayari")
async def cmd_shayari(event):
    await event.reply(f"💕 **Shayari** :\n{random.choice(shayaris)}")

jokes = [
    "Why don't scientists trust atoms? Because they make up everything!",
    "What do you call a bear with no teeth? A gummy bear!",
    "Why did the scarecrow win an award? Because he was outstanding in his field!",
    "What do you call fake spaghetti? An impasta!",
    "Why did the bicycle fall over? Because it was two-tired!",
]
@command("joke")
async def cmd_joke(event):
    await event.reply(f"😂 **Joke** : {random.choice(jokes)}")

quotes = [
    "The only limit to our realization of tomorrow is our doubts of today. – FDR",
    "In the middle of difficulty lies opportunity. – Einstein",
    "Do or do not. There is no try. – Yoda",
    "Be the change you wish to see in the world. – Gandhi",
    "The purpose of life is a life of purpose. – Robert Byrne",
]
@command("quote")
async def cmd_quote(event):
    await event.reply(f"📖 **Quote** : {random.choice(quotes)}")

# Catch unknown commands
@client.on(events.NewMessage(pattern="^[/.]"))
async def unknown_command(event):
    if not await is_authorized(event):
        return

# ------------------------- MAIN -------------------------
async def main():
    await client.start()
    client.start_time = time.time()
    me = await client.get_me()
    logger.info(f"BEBO Ultimate started as {me.first_name} (ID: {me.id})")
    logger.info(f"Owner ID: {OWNER_ID}")

    start_dummy_server()

    if bot_on:
        try:
            await client.send_message(OWNER_ID, f"💖 **BEBO Ultimate** started.\nUse `.menu` for commands.\n{BANNER}")
        except Exception:
            logger.warning("Could not notify owner at startup.")

    await client.run_until_disconnected()

if __name__ == "__main__":
    try:
        client.loop.run_until_complete(main())
    except KeyboardInterrupt:
        logger.info("BEBO stopped by user.")
        save_bot_state()
        save_flow_state()
        save_saved_texts()
