# ════════════════════════════════════════════════════════════════
#   HOSTER BOT CODE (MERGED WITH FULL BEBO ULTIMATE USERBOT ENGINE)
# ════════════════════════════════════════════════════════════════

import asyncio
import logging
import os
import sys
import time
import shutil
import random
import json
import threading
from io import BytesIO
from datetime import datetime
from collections import defaultdict, deque
from pathlib import Path

# --- Gtts Import ---
try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler, ConversationHandler,
    CallbackQueryHandler, ContextTypes, filters
)
from telegram.constants import ParseMode

from telethon import TelegramClient, events, utils
from telethon.sessions import StringSession
from telethon.errors import (
    SessionPasswordNeededError, PhoneCodeExpiredError,
    PhoneCodeInvalidError, FloodWaitError
)
from telethon.tl.functions.channels import EditAdminRequest, EditBannedRequest, EditTitleRequest
from telethon.tl.functions.messages import DeleteMessagesRequest, CreateChatRequest, EditChatTitleRequest
from telethon.tl.types import ChatAdminRights, ChatBannedRights

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

START_TIME = time.time()

# ─── BOT CONFIGURATION ────────────────────────────────────────────────────────
BOT_TOKEN = "8629618999:AAG4CtSRQDZzr_bqPc5cDSiRn54JzwxoOGM"
OWNER_ID = 8115054010
TELEGRAM_API_ID = 38843772
TELEGRAM_API_HASH = "875fbb273801c8025d05e98173fca536"
SUPPORT_USERNAME = "@YourSupport"
MAX_ACCOUNTS_PER_USER = 3
MAX_USERBOTS = 50

# ─── CONVERSATION STATES ──────────────────────────────────────────────────────
ASK_PHONE, ASK_CODE, ASK_2FA = range(3)
pending_logins: dict = {}

# ════════════════════════════════════════════════════════════════════════════════
#   USERBOT ENGINE REGISTRATION (BEBO ULTIMATE COMPLETE LOGIC)
# ════════════════════════════════════════════════════════════════════════════════
def register_userbot_engine(client: TelegramClient, user_id: int):
    # ------------------------- TEXT LISTS -------------------------
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

    rr_texts = GAALI_LIST.copy()

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
    COUNTRY_EMOJIS = ["🇮🇳", "🇺🇸", "🇬🇧", "🇨🇦", "🇦🇺", "🇩🇪", "🇫🇷", "🇯🇵", "🇰🇷", "🇨🇳", "🇷🇺", "🇧🇷", "🇮🇹", "🇪🇸", "🇵🇰", "🇧🇩", "🇳🇵", "🇱🇰", "🇦🇪", "🇸🇦"]
    RANDOM_EMOJIS = ["🔥", "⚡", "✨", "🌟", "⭐", "💫", "🌙", "☀️", "❤️", "🧡", "💛", "💚", "💙", "💜", "😀", "😃", "😄", "😁", "👍", "👎"]

    # ------------------------- STATE CLASSES -------------------------
    class LocalBotState:
        def __init__(self):
            self.bot_on = True
            self.flow_mode = False
            self.saved_texts = []
            self.spray_delay = 0.5
            self.auto_reply_on = False
            self.warnings = {}
            self.active_tasks = {}
            self.safe_users = set()
            self.safe_usernames = {}
            self.auto_delete_chats = {}
            self.delete_target_users = defaultdict(set)
            self.delete_target_usernames = defaultdict(set)
            self.delete_delay = 0.05
            self.autoswipe_active = {}
            self.adv_spam_active = {}
            self.namechange_active = {}
            self.raid_active = {}  
            self.blitz_active = {}
            self.react_active = {} # New property for auto reaction
            self.locked_titles = {}
            self.swipe_targets = defaultdict(dict)
            self.msg_log = defaultdict(lambda: deque())
            self.offenses = defaultdict(int)
            self.locked_groups = set()
            self.locked_chat = set()
            self.locked_name_change = set()
            self.emergency_active = {}
            self.metrics = {"start": time.monotonic(), "msg": 0, "mutes": 0, "swipes": 0}
            self.namechange_delays = {}
            
            self.flow_delay = 0.2
            self.flow_count = 30
            self.fast_gc_trigger = None
            self.fast_gc_template = None
            self.boost_mode = False
            self.critical_mode = False
            
            self.normal_cfg = dict(SPAM=5, WINDOW=6)
            self.boost_cfg = dict(SPAM=3, WINDOW=3)
            self.crit_cfg = dict(SPAM=2, WINDOW=2)
            self.cfg = self.normal_cfg.copy()
            self.mute_table = (300, 900, 1800, 3600, 21600)

        def is_user_safe(self, uid, username=None):
            if uid in self.safe_users or uid == user_id:
                return True
            if username and username.lower() in self.safe_usernames:
                return True
            return False

        def should_delete_user(self, chat_id, uid, username=None):
            if chat_id not in self.delete_target_users:
                return False
            if uid in self.delete_target_users[chat_id]:
                return True
            if username and chat_id in self.delete_target_usernames:
                if username.lower() in self.delete_target_usernames[chat_id]:
                    return True
            return False

    state = LocalBotState()

    # ------------------------- AUTH & DECORATORS -------------------------
    async def is_authorized(event):
        if event.raw_text and event.raw_text.startswith(("/on", ".on")): return True
        if not state.bot_on: return False
        if event.out or event.sender_id == user_id: return True
        
        sender_id = getattr(event, 'sender_id', None)
        if not sender_id: return False

        username = None
        try:
            sender = await event.get_sender()
            if hasattr(sender, 'username'): username = sender.username
        except: pass

        if state.is_user_safe(sender_id, username): return True
        return False

    def command(cmd):
        def decorator(func):
            @client.on(events.NewMessage(pattern=rf"^[/.]{cmd}(?:\b|$)"))
            async def handler(event):
                if not await is_authorized(event): return
                try: await func(event)
                except Exception as e: await event.reply(f"❌ Error: {e}")
            return handler
        return decorator

    def flow_command(cmd):
        def decorator(func):
            @client.on(events.NewMessage(pattern=rf"^[/.]{cmd}(?:\b|$)"))
            async def handler(event):
                if not await is_authorized(event): return
                if not state.flow_mode: return await event.reply("❌ Flow bot is OFF. Use `/switch` to enable.")
                try: await func(event)
                except Exception as e: await event.reply(f"❌ Error: {e}")
            return handler
        return decorator

    async def get_target(event):
        if event.is_reply:
            reply_msg = await event.get_reply_message()
            try:
                return await client.get_entity(reply_msg.sender_id)
            except: pass

        args = event.raw_text.split(maxsplit=1)
        if len(args) < 2:
            await event.reply("⚠️ Please specify a target username or ID, or reply to a message.")
            return None
        target_str = args[1].strip()
        if target_str.startswith("@"): target_str = target_str[1:]
        try:
            if target_str.isdigit(): return await client.get_entity(int(target_str))
            else: return await client.get_entity(target_str)
        except Exception as e:
            await event.reply(f"❌ Could not find user: {e}")
            return None

    async def get_target_from_str(event, target_str):
        if target_str.startswith("@"): target_str = target_str[1:]
        try:
            if target_str.isdigit(): return await client.get_entity(int(target_str))
            else: return await client.get_entity(target_str)
        except Exception as e:
            await event.reply(f"❌ Could not find user: {e}")
            return None

    async def get_user_from_arg(event):
        if event.is_reply:
            reply_msg = await event.get_reply_message()
            try:
                return await client.get_entity(reply_msg.sender_id)
            except: pass

        args = event.raw_text.split(maxsplit=1)
        if len(args) < 2:
            await event.reply("⚠️ Please specify a user (username or ID), or reply to a message.")
            return None
        target = args[1].strip()
        try:
            if target.startswith("@"): target = target[1:]
            if target.isdigit(): return await client.get_entity(int(target))
            else: return await client.get_entity(target)
        except Exception as e:
            await event.reply(f"❌ Could not find user: {e}")
            return None

    # ------------------------- BACKGROUND GUARDS -------------------------
    async def smart_mute(chat_id, target_uid):
        if target_uid == user_id: return
        state.offenses[(chat_id, target_uid)] += 1
        state.metrics["mutes"] += 1
        duration = state.mute_table[min(state.offenses[(chat_id, target_uid)] - 1, 4)]
        try: await client(EditBannedRequest(chat_id, target_uid, ChatBannedRights(send_messages=True, until_date=int(time.time()) + duration)))
        except: pass

    @client.on(events.NewMessage(incoming=True))
    async def auto_delete_handler(event):
        if not state.bot_on: return
        chat_id = event.chat_id
        if not state.auto_delete_chats.get(chat_id, False): return
        
        if hasattr(event, 'action') and event.action is not None:
            try:
                await asyncio.sleep(state.delete_delay)
                await event.delete()
            except: pass
            return
            
        if not event.sender_id: return
        uid = event.sender_id
        username = getattr(getattr(event, 'sender', None), 'username', None)

        if chat_id in state.delete_target_users and state.delete_target_users[chat_id]:
            if state.should_delete_user(chat_id, uid, username):
                try:
                    await asyncio.sleep(state.delete_delay)
                    await event.delete()
                except: pass
            return
            
        if not state.is_user_safe(uid, username):
            try:
                await asyncio.sleep(state.delete_delay)
                await event.delete()
            except: pass

    @client.on(events.NewMessage(incoming=True))
    async def global_react_handler(event):
        if not state.bot_on: return
        if event.chat_id in state.react_active:
            try:
                emoji = random.choice(RANDOM_EMOJIS[:10]) 
                await event.react(emoji)
            except: pass

    @client.on(events.NewMessage(incoming=True))
    async def message_guard(event):
        if not state.bot_on: return
        if event.text and event.text.startswith('.'): return
        state.metrics["msg"] += 1
        uid, cid = event.sender_id, event.chat_id
        if uid == user_id: return
        
        if state.critical_mode:
            await smart_mute(cid, uid)
            return

        now = time.monotonic()
        log = state.msg_log[(cid, uid)]
        log.append(now)
        while log and now - log[0] > state.cfg["WINDOW"]: log.popleft()
        if len(log) >= state.cfg["SPAM"]:
            await smart_mute(cid, uid)
            return
            
        if cid in state.swipe_targets and uid in state.swipe_targets[cid]:
            state.metrics["swipes"] += 1
            asyncio.create_task(event.reply(state.swipe_targets[cid][uid]))

    @client.on(events.NewMessage(incoming=True))
    async def chat_lock_handler(event):
        if not state.bot_on: return
        if event.chat_id in state.locked_chat and event.sender_id != user_id:
            try: await event.delete()
            except: pass

    @client.on(events.ChatAction)
    async def title_guard(event):
        if not state.bot_on: return
        if event.chat_id in state.locked_titles and getattr(event, 'user_id', None) != user_id:
            try:
                await client(EditChatTitleRequest(event.chat_id, state.locked_titles[event.chat_id]))
                if hasattr(event, 'user_id'): await smart_mute(event.chat_id, event.user_id)
            except: pass

    @client.on(events.ChatAction)
    async def namechange_lock_handler(event):
        if not state.bot_on: return
        if event.chat_id in state.locked_name_change and getattr(event, 'user_id', None) != user_id:
            if event.chat_id in state.locked_titles:
                try: await client(EditChatTitleRequest(event.chat_id, state.locked_titles[event.chat_id]))
                except: pass

    @client.on(events.NewMessage(incoming=True))
    async def adv_multireply_handler(event):
        if not state.bot_on: return
        chat_id = event.chat_id
        if chat_id not in state.autoswipe_active: return
        swipe_data = state.autoswipe_active[chat_id]
        if isinstance(swipe_data, str) and swipe_data.startswith("MULTI:"):
            parts = swipe_data.split(":", 2)
            if len(parts) == 3:
                try:
                    times = int(parts[1])
                    for _ in range(times):
                        await event.reply(parts[2])
                        await asyncio.sleep(0.05)
                except: pass
        elif isinstance(swipe_data, str) and not swipe_data.startswith("MULTI:") and not swipe_data.startswith("RAID:"):
            try: await event.reply(swipe_data)
            except: pass

    @client.on(events.NewMessage(incoming=True))
    async def global_raid_handler(event):
        if not state.bot_on or event.out: return
        chat_id = event.chat_id
        uid = event.sender_id
        if not uid: return
        
        if chat_id in state.raid_active and uid in state.raid_active[chat_id]:
            raid_data = state.raid_active[chat_id][uid]
            text = random.choice(raid_data["texts"])
            try: await event.reply(text)
            except: pass

    # ------------------------- BASE COMMANDS -------------------------
    @command("on")
    async def cmd_on(event):
        state.bot_on = True
        await event.reply("✅ BEBO is now **ON**.")

    @command("off")
    async def cmd_off(event):
        state.bot_on = False
        await event.reply("🔴 BEBO is now **OFF**.")

    @command("ping")
    async def cmd_ping(event):
        start = time.perf_counter()
        msg = await event.reply("🏓 Pinging...")
        end = time.perf_counter()
        await msg.edit(f"🏓 Pong! 🌀 Latency: `{(end - start) * 1000:.2f} ms`")

    @command("echo")
    async def cmd_echo(event):
        args = event.raw_text.split(maxsplit=1)
        if len(args) > 1: await event.reply(args[1])
        else: await event.reply("ℹ️ Usage: `/echo <text>`")

    @command("stats")
    async def cmd_stats(event):
        up = int(time.time() - state.metrics["start"])
        d, r = divmod(up, 86400)
        h, r = divmod(r, 3600)
        m, s = divmod(r, 60)
        await event.reply(f"📊 **BEBO Stats**\n• Uptime: `{d}d {h}h {m}m {s}s`\n• State: `{'ON' if state.bot_on else 'OFF'}`\n• Flow Mode: `{'ON' if state.flow_mode else 'OFF'}`\n• API ID: `{TELEGRAM_API_ID}`")

    @command("info")
    async def cmd_info(event):
        chat = await event.get_chat()
        sender = await event.get_sender()
        await event.reply(f"ℹ️ **Chat Info**\n• ID: `{event.chat_id}`\n• Title: `{getattr(chat, 'title', 'N/A')}`\n\n👤 **Sender**\n• ID: `{sender.id}`\n• Name: `{utils.get_display_name(sender)}`")

    @command("restart")
    async def cmd_restart(event):
        await event.reply("🔄 Restart request received. Please use `/restart` in the hoster bot.")

    @command("switch")
    async def cmd_switch(event):
        state.flow_mode = not state.flow_mode
        await event.reply(f"🔄 Flow mode is now **{'ON' if state.flow_mode else 'OFF'}**.\nUse `.flowmenu` for flow commands.")

    @command("react")
    async def cmd_react(event):
        state.react_active[event.chat_id] = True
        msg = await event.respond("🔄 **INITIALIZING REACT ENGINE...**")
        await asyncio.sleep(0.3)
        await msg.edit("✅ **REACT MODE ON**\nReacting to all messages in this chat!")

    @command("sreact")
    async def cmd_sreact(event):
        if event.chat_id in state.react_active:
            del state.react_active[event.chat_id]
            await event.respond("✅ **REACT MODE OFF**")
        else:
            await event.respond("ℹ️ React mode is not active here.")

    # ------------------------- EVENT-DRIVEN RAID COMMANDS -------------------------
    async def start_raid(event, text_list, raid_type):
        user = await get_target(event)
        if not user: return
        chat_id = event.chat_id
        
        if chat_id not in state.raid_active:
            state.raid_active[chat_id] = {}
            
        state.raid_active[chat_id][user.id] = {"texts": text_list, "type": raid_type}
        
        if raid_type == "rr":
            await event.reply(f"rr started on {user.id}")
        else:
            await event.reply(f"✅ {raid_type.capitalize()} raid started on {utils.get_display_name(user)}! (Will swipe their messages)")

    async def stop_raid(event, raid_type):
        chat_id = event.chat_id
        stopped = False
        if chat_id in state.raid_active:
            to_remove = [uid for uid, data in state.raid_active[chat_id].items() if data["type"] == raid_type]
            for uid in to_remove:
                del state.raid_active[chat_id][uid]
                stopped = True
            if not state.raid_active[chat_id]:
                del state.raid_active[chat_id]
                
        if stopped: await event.reply(f"✅ {raid_type.capitalize()} raid stopped.")
        else: await event.reply(f"ℹ️ No active {raid_type} raid in this chat.")

    @command("reply")
    async def cmd_reply(event): await start_raid(event, reply_texts, "reply")
    @command("sreply")
    async def cmd_sreply(event): await stop_raid(event, "reply")

    @command("rr")
    async def cmd_rr(event): await start_raid(event, rr_texts, "rr")
    @command("srr")
    async def cmd_srr(event): await stop_raid(event, "rr")

    @command("flag")
    async def cmd_flag(event): await start_raid(event, flag_texts, "flag")
    @command("sflag")
    async def cmd_sflag(event): await stop_raid(event, "flag")

    @command("hrr")
    async def cmd_hrr(event): await start_raid(event, heart_replies, "hrr")
    @command("shrr")
    async def cmd_shrr(event): await stop_raid(event, "hrr")

    @command("replygod")
    async def cmd_replygod(event): await start_raid(event, attack_list + roast_list, "replygod")
    @command("sgod")
    async def cmd_sgod(event): await stop_raid(event, "replygod")

    @command("replyraid")
    async def reply_raid_cmd(event): await start_raid(event, GAALI_LIST, "replyraid")
    @command("stopreplyraid")
    async def stop_reply_raid_cmd(event): await stop_raid(event, "replyraid")

    @command("superraid")
    async def cmd_superraid(event):
        user = await get_target(event)
        if not user: return
        chat_id = event.chat_id
        all_texts_super = reply_texts + rr_texts + flag_texts + heart_replies + attack_list + roast_list
        state.raid_active.setdefault(chat_id, {})[user.id] = {"texts": all_texts_super, "type": "superraid"}
        await event.reply(f"💥 Super raid started on {utils.get_display_name(user)}!")

    @command("stopsuper")
    async def cmd_stopsuper(event): await stop_raid(event, "superraid")

    async def limited_raid_loop(chat, user, text, count):
        try:
            for _ in range(count):
                try:
                    if getattr(user, 'username', None): await client.send_message(chat, f"{text} @{user.username}")
                    else: await client.send_message(chat, f"{text} {user.first_name}")
                except Exception: pass
                await asyncio.sleep(0.2)
        except asyncio.CancelledError: pass
        finally: state.active_tasks.pop("limited", None)

    @command("replybebo")
    async def cmd_replybebo(event):
        args = event.raw_text.split(maxsplit=3)
        if len(args) < 4: return await event.reply("⚠️ Usage: `.replybebo @user <text> <count>`")
        try: count = int(args[3])
        except ValueError: return await event.reply("⚠️ Count must be a number.")
        user = await get_target_from_str(event, args[1])
        if not user: return
        if "limited" in state.active_tasks: state.active_tasks["limited"].cancel()
        state.active_tasks["limited"] = asyncio.create_task(limited_raid_loop(event.chat, user, args[2], count))
        await event.reply(f"✅ Limited raid started on {utils.get_display_name(user)} for {count} messages.")

    @command("sstop")
    async def cmd_sstop(event):
        if "limited" in state.active_tasks:
            state.active_tasks["limited"].cancel()
            await event.reply("✅ Limited raid stopped.")
        else: await event.reply("ℹ️ No limited raid running.")

    @command("raid")
    async def cmd_raid(event):
        args = event.text.strip().split()
        if len(args) < 2: return await event.reply("**Usage:** `.raid <count>`")
        try: count = int(args[1])
        except: return await event.respond("❌ **Count must be a valid number!**")
        
        chat_id = event.chat_id
        if "bebo_raid" in state.active_tasks: return await event.reply("⚠️ A BEBO raid is already running. Use `.stopraid` first.")
        
        async def bebo_raid_loop():
            try:
                for _ in range(count):
                    if "bebo_raid" not in state.active_tasks: break
                    try: await client.send_message(chat_id, random.choice(RAID_TEXTS))
                    except: pass
                    await asyncio.sleep(0.1)
                if "bebo_raid" in state.active_tasks: await client.send_message(chat_id, "✅ **BEBO RAID SUCCESSFULLY COMPLETED!**")
            except asyncio.CancelledError: pass
            finally: state.active_tasks.pop("bebo_raid", None)

        state.active_tasks["bebo_raid"] = asyncio.create_task(bebo_raid_loop())
        msg = await event.respond("🚀 **PREPARING TO RAID...**")
        await asyncio.sleep(0.3)
        await msg.edit("⚠️ **TARGET ACQUIRED & LOCKED...**")
        await asyncio.sleep(0.3)
        await msg.edit(f"🔥 **BEBO RAID INITIATED: {count} TOXIC MESSAGES!**")

    @command("stopraid")
    async def cmd_stopraid(event):
        if "bebo_raid" in state.active_tasks:
            state.active_tasks["bebo_raid"].cancel()
            await event.reply("🛑 **BEBO RAID FORCE STOPPED!**")
        else: await event.reply("ℹ️ No active BEBO raid.")

    # ------------------------- SPRAY COMMANDS -------------------------
    async def spray_task(chat, text, count, delay):
        try:
            for _ in range(count):
                try: await client.send_message(chat, text)
                except: pass
                await asyncio.sleep(delay)
        except asyncio.CancelledError: pass
        finally: state.active_tasks.pop("spray", None)

    async def rspray_task(chat, text_list, count, delay):
        try:
            for _ in range(count):
                try: await client.send_message(chat, random.choice(text_list))
                except: pass
                await asyncio.sleep(delay)
        except asyncio.CancelledError: pass
        finally: state.active_tasks.pop("spray", None)

    async def multispray_task(chat, lines, delay):
        try:
            while "spray" in state.active_tasks:
                for line in lines:
                    if "spray" not in state.active_tasks: break
                    try: await client.send_message(chat, line)
                    except: pass
                    await asyncio.sleep(delay)
        except asyncio.CancelledError: pass
        finally: state.active_tasks.pop("spray", None)

    @command("spray")
    async def cmd_spray(event):
        args = event.raw_text.split(maxsplit=1)
        if len(args) < 2: return await event.reply("⚠️ Usage: `.spray <text>`")
        if "spray" in state.active_tasks: return await event.reply("⚠️ A spray is already running.")
        state.active_tasks["spray"] = asyncio.create_task(spray_task(event.chat, args[1], 10, state.spray_delay))
        await event.reply(f"✅ Spray started for 10 messages with delay {state.spray_delay}s.")

    @command("dspray")
    async def cmd_dspray(event):
        args = event.raw_text.split(maxsplit=1)
        if len(args) < 2: return await event.reply("⚠️ Usage: `.dspray <text>`")
        try:
            async for msg in client.iter_messages(event.chat, limit=10):
                await msg.delete(); await asyncio.sleep(0.1)
        except Exception: pass
        if "spray" in state.active_tasks: state.active_tasks["spray"].cancel()
        state.active_tasks["spray"] = asyncio.create_task(spray_task(event.chat, args[1], 10, state.spray_delay))
        await event.reply(f"✅ Deleted 10 messages and started spray.")

    @command("tspray")
    async def cmd_tspray(event):
        args = event.raw_text.split(maxsplit=3)
        if len(args) < 4: return await event.reply("⚠️ Usage: `.tspray <count> <delay_sec> <text>`")
        try: count, delay, text = int(args[1]), float(args[2]), args[3]
        except ValueError: return await event.reply("⚠️ Count/delay must be numbers.")
        if "spray" in state.active_tasks: state.active_tasks["spray"].cancel()
        state.active_tasks["spray"] = asyncio.create_task(spray_task(event.chat, text, count, delay))
        await event.reply(f"✅ Timed spray started: {count} messages.")

    @command("rspray")
    async def cmd_rspray(event):
        if "spray" in state.active_tasks: state.active_tasks["spray"].cancel()
        text_list = state.saved_texts if state.saved_texts else all_texts
        if not text_list: return await event.reply("⚠️ No texts available.")
        state.active_tasks["spray"] = asyncio.create_task(rspray_task(event.chat, text_list, 20, state.spray_delay))
        await event.reply(f"✅ Random spray started (20 msgs).")

    @command("multispray")
    async def cmd_multispray(event):
        args = event.raw_text.split(maxsplit=1)
        if len(args) < 2: return await event.reply("⚠️ Usage: `.multispray <t1|t2|...>`")
        lines = [line.strip() for line in args[1].split("|") if line.strip()]
        if not lines: return await event.reply("⚠️ No valid lines.")
        if "spray" in state.active_tasks: state.active_tasks["spray"].cancel()
        state.active_tasks["spray"] = asyncio.create_task(multispray_task(event.chat, lines, state.spray_delay))
        await event.reply(f"✅ Multi-spray started with {len(lines)} lines.")

    @command("countspray")
    async def cmd_countspray(event):
        args = event.raw_text.split(maxsplit=2)
        if len(args) < 3: return await event.reply("⚠️ Usage: `.countspray <count> <text>`")
        try: count, text = int(args[1]), args[2]
        except ValueError: return await event.reply("⚠️ Count must be a number.")
        if "spray" in state.active_tasks: state.active_tasks["spray"].cancel()
        state.active_tasks["spray"] = asyncio.create_task(spray_task(event.chat, text, count, state.spray_delay))
        await event.reply(f"✅ Count spray started: {count} messages.")

    @command("spraydelay")
    async def cmd_spraydelay(event):
        args = event.raw_text.split(maxsplit=1)
        if len(args) < 2: return await event.reply(f"ℹ️ Current spray delay: {state.spray_delay}s")
        try:
            val = float(args[1])
            if val < 0.1: return await event.reply("⚠️ Min delay 0.1s")
            state.spray_delay = val
            await event.reply(f"✅ Spray delay set to {state.spray_delay}s")
        except ValueError: await event.reply("⚠️ Invalid number.")

    @command("stopspray")
    async def cmd_stopspray(event):
        if "spray" in state.active_tasks:
            state.active_tasks["spray"].cancel()
            await event.reply("✅ Spray stopped.")
        else: await event.reply("ℹ️ No active spray.")

    # ------------------------- ADVANCED SPAM -------------------------
    @command("advspam")
    async def advspam_cmd(event):
        args = event.text.strip().split(None, 2)
        if len(args) < 3: return await event.respond("**Usage:** `.advspam <mode> <text>`\n**Modes:** fast, medium, slow, burst, random, tsunami, nightmare")
        mode, text = args[1].lower(), args[2]
        chat_id = event.chat_id
        valid_modes = ['fast', 'medium', 'slow', 'burst', 'random', 'tsunami', 'nightmare']
        if mode not in valid_modes: return await event.respond(f"❌ **Invalid mode!**")
        
        state.adv_spam_active[chat_id] = f"{mode}:{text}"
        msg = await event.respond("🚀 **PREPARING SPAM ENGINE...**")
        await asyncio.sleep(0.3)
        await msg.edit(f"📢 **SPAM ON:** {mode.upper()}")

        async def spam_task():
            while chat_id in state.adv_spam_active:
                try:
                    spam_data = state.adv_spam_active[chat_id]
                    if ':' not in spam_data: break
                    current_mode, spam_text = spam_data.split(':', 1)

                    if current_mode == 'fast': await client.send_message(chat_id, spam_text); await asyncio.sleep(0.1)
                    elif current_mode == 'medium': await client.send_message(chat_id, spam_text); await asyncio.sleep(0.5)
                    elif current_mode == 'slow': await client.send_message(chat_id, spam_text); await asyncio.sleep(2)
                    elif current_mode == 'burst':
                        for _ in range(10): await client.send_message(chat_id, spam_text); await asyncio.sleep(0.01)
                        await asyncio.sleep(5)
                    elif current_mode == 'random': await client.send_message(chat_id, spam_text); await asyncio.sleep(random.uniform(0.1, 3.0))
                    elif current_mode == 'tsunami':
                        for _ in range(50): await client.send_message(chat_id, spam_text); await asyncio.sleep(0.01)
                        await asyncio.sleep(10)
                    elif current_mode == 'nightmare':
                        for _ in range(5): await client.send_message(chat_id, spam_text); await asyncio.sleep(0.01)
                        await asyncio.sleep(1)
                except FloodWaitError as e: await asyncio.sleep(e.seconds)
                except Exception: continue
            state.adv_spam_active.pop(chat_id, None)

        state.active_tasks[f"advspam_{chat_id}"] = asyncio.create_task(spam_task())

    @command("stopadvspam")
    async def stopadvspam_cmd(event):
        chat_id = event.chat_id
        if chat_id in state.adv_spam_active:
            del state.adv_spam_active[chat_id]
            if f"advspam_{chat_id}" in state.active_tasks: state.active_tasks[f"advspam_{chat_id}"].cancel()
            await event.respond("✅ **ADV SPAM OFF**")

    @command("spam")
    async def spam_alias(event): await advspam_cmd(event)

    # ------------------------- TEXT MANAGER -------------------------
    @command("addtext")
    async def cmd_addtext(event):
        args = event.raw_text.split(maxsplit=1)
        if len(args) < 2: return await event.reply("⚠️ Usage: `.addtext <text>`")
        state.saved_texts.append(args[1])
        await event.reply(f"✅ Text added. Total: {len(state.saved_texts)}")

    @command("listtexts")
    async def cmd_listtexts(event):
        if not state.saved_texts: return await event.reply("ℹ️ No saved texts.")
        text_list = "\n".join([f"{i+1}. {t[:50]}..." if len(t)>50 else f"{i+1}. {t}" for i,t in enumerate(state.saved_texts)])
        await event.reply(f"📝 **Saved Texts ({len(state.saved_texts)})**\n{text_list}")

    @command("edittext")
    async def cmd_edittext(event):
        args = event.raw_text.split(maxsplit=2)
        if len(args) < 3: return await event.reply("⚠️ Usage: `.edittext <index> <new_text>`")
        try:
            idx = int(args[1]) - 1
            if idx < 0 or idx >= len(state.saved_texts): return await event.reply("⚠️ Invalid index.")
            state.saved_texts[idx] = args[2]
            await event.reply(f"✅ Text {idx+1} updated.")
        except ValueError: await event.reply("⚠️ Index must be a number.")

    @command("deltext")
    async def cmd_deltext(event):
        args = event.raw_text.split(maxsplit=1)
        if len(args) < 2: return await event.reply("⚠️ Usage: `.deltext <index>`")
        try:
            idx = int(args[1]) - 1
            if idx < 0 or idx >= len(state.saved_texts): return await event.reply("⚠️ Invalid index.")
            removed = state.saved_texts.pop(idx)
            await event.reply(f"✅ Removed text: `{removed[:30]}...`")
        except ValueError: await event.reply("⚠️ Index must be a number.")

    @command("cleartext")
    async def cmd_cleartext(event):
        state.saved_texts.clear()
        await event.reply("✅ All saved texts cleared.")

    # ------------------------- FAST GC -------------------------
    @command("fastgc")
    async def cmd_fastgc(event):
        args = event.raw_text.split(maxsplit=3)
        if len(args) < 4 or args[1].lower() != "set": return await event.reply("⚠️ Usage: `.fastgc set <emoji> <template>`")
        state.fast_gc_trigger, state.fast_gc_template = args[2], args[3]
        await event.reply(f"✅ Fast GC set: trigger '{state.fast_gc_trigger}' → template '{state.fast_gc_template}'")

    @command("fastgc stop")
    async def cmd_fastgc_stop(event):
        state.fast_gc_trigger, state.fast_gc_template = None, None
        await event.reply("✅ Fast GC stopped.")

    # ------------------------- ADMIN COMMANDS -------------------------
    @command("mute")
    async def cmd_mute(event):
        user = await get_user_from_arg(event)
        if not user: return
        
        if event.is_group:
            try:
                await client.edit_permissions(event.chat_id, user, ChatBannedRights(until_date=None, send_messages=True, send_media=True, send_stickers=True, send_gifs=True, send_games=True, send_inline=True, send_polls=True))
                await event.reply(f"🔇 Muted {utils.get_display_name(user)}.")
            except Exception as e: await event.reply(f"❌ Failed: {e}")
        else:
            state.delete_target_users[event.chat_id].add(user.id)
            state.auto_delete_chats[event.chat_id] = True
            await event.reply(f"🔇 Muted {utils.get_display_name(user)} in DM (Auto-deleting messages).")

    @command("unmute")
    async def cmd_unmute(event):
        user = await get_user_from_arg(event)
        if not user: return
        
        if event.is_group:
            try:
                await client.edit_permissions(event.chat_id, user, ChatBannedRights(until_date=None, send_messages=False, send_media=False, send_stickers=False, send_gifs=False, send_games=False, send_inline=False, send_polls=False))
                await event.reply(f"🔊 Unmuted {utils.get_display_name(user)}.")
            except Exception as e: await event.reply(f"❌ Failed: {e}")
        else:
            if event.chat_id in state.delete_target_users:
                state.delete_target_users[event.chat_id].discard(user.id)
            await event.reply(f"🔊 Unmuted {utils.get_display_name(user)} in DM.")

    @command("demote")
    async def cmd_demote(event):
        if not event.is_group: return await event.reply("⚠️ Groups only.")
        user = await get_user_from_arg(event)
        if not user: return
        try:
            await client.edit_admin(event.chat_id, user, ChatAdminRights(post_messages=False, add_admins=False, invite_users=False, change_info=False, ban_users=False, pin_messages=False, manage_call=False, anonymous=False, manage_chat=False, delete_messages=False, restrict_users=False))
            await event.reply(f"⬇️ Demoted {utils.get_display_name(user)}.")
        except Exception as e: await event.reply(f"❌ Failed: {e}")

    @command("promote")
    async def cmd_promote(event):
        if not event.is_group: return await event.reply("⚠️ Groups only.")
        user = await get_user_from_arg(event)
        if not user: return
        try:
            await client.edit_admin(event.chat_id, user, ChatAdminRights(post_messages=True, add_admins=False, invite_users=True, change_info=True, ban_users=True, pin_messages=True, manage_call=True, anonymous=False, manage_chat=True, delete_messages=True, restrict_users=True))
            await event.reply(f"⬆️ Promoted {utils.get_display_name(user)}.")
        except Exception as e: await event.reply(f"❌ Failed: {e}")

    @command("kick")
    async def cmd_kick(event):
        if not event.is_group: return await event.reply("⚠️ Groups only.")
        user = await get_user_from_arg(event)
        if not user: return
        try:
            await client.kick_participant(event.chat_id, user)
            await event.reply(f"👢 Kicked {utils.get_display_name(user)}.")
        except Exception as e: await event.reply(f"❌ Failed: {e}")

    @command("ban")
    async def cmd_ban(event):
        if not event.is_group: return await event.reply("⚠️ Groups only.")
        user = await get_user_from_arg(event)
        if not user: return
        try:
            await client.edit_permissions(event.chat_id, user, ChatBannedRights(until_date=None, view_messages=True, send_messages=True, send_media=True, send_stickers=True, send_gifs=True, send_games=True, send_inline=True, send_polls=True, change_info=True, invite_users=True, pin_messages=True))
            await event.reply(f"🚫 Banned {utils.get_display_name(user)}.")
        except Exception as e: await event.reply(f"❌ Failed: {e}")

    # ------------------------- MENUS -------------------------
    @command("menu")
    async def cmd_menu(event):
        msg = await event.reply("🔄 **INITIALIZING MASTER MENU...**")
        await asyncio.sleep(0.2)
        await msg.edit("⚙️ **LOADING MODULES...**")
        await asyncio.sleep(0.2)
        menu = """
╔═══════════════════════════════════════════╗
║         💖  𝐁𝐄𝐁𝐎 𝐔𝐋𝐓𝐈𝐌𝐀𝐓𝐄 𝐌𝐄𝐍𝐔  💖        ║
╚═══════════════════════════════════════════╝

  📌 `.menu`      → This Menu
  📌 `.flowmenu`  → Flow Bot Menu
  📌 `.advmenu`   → Advanced Security Menu
  📌 `.about`     → About BEBO
  📌 `.banner`    → Show ASCII Art

【 🛠️ 𝗕𝗔𝗦𝗜𝗖 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 】
  `/on`, `/off`, `/ping`, `/echo`, `/stats`, `/info`, `/restart`, `/switch`

【 ⚔️ 𝗥𝗔𝗜𝗗 𝗘𝗡𝗚𝗜𝗡𝗘 】
  💬 Reply      → `.reply @user`    | `.sreply`
  🤣 RR         → `.rr @user`       | `.srr`
  🚩 Flag       → `.flag @user`     | `.sflag`
  💗 Heart      → `.hrr @user`      | `.shrr`
  😈 God        → `.replygod @user` | `.sgod`
  📌 Limited    → `.replybebo @user <text> <count>` | `.sstop`
  ⚡ Super      → `.superraid @user`| `.stopsuper`
  🔥 BEBO Raid  → `.raid <count>`   | `.stopraid`

【 💣 𝗦𝗣𝗔𝗠 𝗦𝗬𝗦𝗧𝗘𝗠 】
  ✦ `.spam <mode> <text>` (fast, medium, slow, burst, random, tsunami, nightmare)
  ✦ `.spray <text>`          → 10x spray
  ✦ `.dspray <text>`         → delete & spray
  ✦ `.tspray <n> <del> <t>`  → timed spray
  ✦ `.rspray`                → random text spam
  ✦ `.multispray <t1|t2...>` 
  ✦ `.countspray <n> <text>`
  ✦ `.spraydelay <sec>`
  ✦ `.stopspray` / `.stopadvspam`

【 📝 𝗧𝗘𝗫𝗧 𝗠𝗔𝗡𝗔𝗚𝗘𝗥 】
  `.addtext`, `.listtexts`, `.edittext`, `.deltext`, `.cleartext`

【 🚀 𝗙𝗔𝗦𝗧 𝗚𝗖 】
  `.fastgc set <emoji> <template>` | `.fastgc stop`

【 👑 𝗔𝗗𝗠𝗜𝗡 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 】
  `.mute`, `.unmute`, `.promote`, `.demote`, `.kick`, `.ban`
  `.pin` (reply), `.unpin`, `.slowmode <sec>`, `.setgrouptitle <title>`
  `.setgrouppic` (reply to photo), `.adminlist`, `.banlist`
  `.purge <n>` (delete n messages)

【 ✨ 𝗨𝗧𝗜𝗟𝗜𝗧𝗬 & 𝗙𝗨𝗡 】
  `.react`       → React to every msg 
  `.sreact`      → Stop reactions
  `.id @user`    → get user/chat ID
  `.tagall`      → mention everyone
  `.warn @user`  → warn a user
  `.kickme`      → leave group
  `.join <link>` → join via link
  `.setpfp`      → set profile pic
  `.setname`     → set bot's name
  `.setbio`      → set bot's bio
  `.autoreply`   → toggle auto-reply
  Fun: `.motivate`, `.truth`, `.dare`, `.shayari`, `.joke`, `.quote`

╔═══════════════════════════════════════════╗
║         💖  BEBO — 𝗔𝗹𝗹 𝗥𝗶𝗴𝗵𝘁𝘀 𝗥𝗲𝘀𝗲𝗿𝘃𝗲𝗱       ║
╚═══════════════════════════════════════════╝
        """
        await msg.edit(menu)

    @command("advmenu")
    async def cmd_advmenu(event):
        msg = await event.reply("🔄 **INITIALIZING SECURITY...**")
        await asyncio.sleep(0.3)
        menu = """
╔═══════════════════════════════════════════╗
║    🛡️  𝐁𝐄𝐁𝐎 𝐀𝐃𝐕𝐀𝐍𝐂𝐄𝐃 𝐒𝐄𝐂𝐔𝐑𝐈𝐓𝐘 𝐌𝐄𝐍𝐔  🛡️   ║
╚═══════════════════════════════════════════╝

【 🗑️ 𝗠𝗨𝗧𝗘 𝗖𝗢𝗡𝗧𝗥𝗢𝗟𝗦 】
  • `.sabchup` / `.speakall`
  • `.chup` / `.bol` (reply to user)
  • `.safe @user`

【 💣 𝗔𝗗𝗩𝗔𝗡𝗖𝗘𝗗 𝗦𝗣𝗔𝗠 & 𝗥𝗔𝗜𝗗 】
  • `.advspam <mode> <text>`
  • `.stopadvspam`
  • `.replyraid @user` | `.stopreplyraid`
  • `.autoswipe <text>` | `.stopautoswipe`
  • `.advmultireply <n> <text>` | `.stopadvmultireply`

【 🔄 𝗡𝗔𝗠𝗘 𝗖𝗢𝗡𝗧𝗥𝗢𝗟𝗦 】
  • `.namechange [mode] [ms]` 
  • `.namedelay <ms>` | `.stopnamechange`
  • `.blitz [mode]` | `.stopblitz`

【 🔐 𝗦𝗘𝗖𝗨𝗥𝗜𝗧𝗬 𝗟𝗢𝗖𝗞𝗦 】
  • `.lockname` | `.lockgroup` | `.unlockgroup`
  • `.lockchat` | `.unlockchat` 
  • `.locknamechange` | `.unlocknamechange`

【 🛡️ 𝗣𝗥𝗢𝗧𝗘𝗖𝗧𝗜𝗢𝗡 & 𝗘𝗠𝗘𝗥𝗚𝗘𝗡𝗖𝗬 】
  • `.boost on/off` | `.assist on/off` | `.perf`
  • `.terminate` | `.killname` 
  • `.dominate` | `.stopdominate`
  • `.emergency` | `.stopemergency`

【 📦 𝗨𝗧𝗜𝗟𝗜𝗧𝗜𝗘𝗦 】
  • `.makegc <name>` | `.lockswipe @user <text>`
  • `.hindivoice <text>` 

╔═══════════════════════════════════════════╗
║     🛡️  BEBO — 𝗨𝗹𝘁𝗶𝗺𝗮𝘁𝗲 𝗣𝗿𝗼𝘁𝗲𝗰𝘁𝗶𝗼𝗻     ║
╚═══════════════════════════════════════════╝
        """
        await msg.edit(menu)

    @command("flowmenu")
    async def cmd_flowmenu(event):
        msg = await event.reply("🌊 **INITIALIZING FLOW ENGINE...**")
        await asyncio.sleep(0.3)
        menu = """
╔═══════════════════════════════════════════╗
║          🌊  𝐁𝐄𝐁𝐎 𝐅𝐋𝐎𝐖 𝐁𝐎𝐓 𝐌𝐄𝐍𝐔  🌊       ║
╚═══════════════════════════════════════════╝

  🌊 This is the high-speed flow engine.
  Use `.swipe` to start a swipe flood.

【 🌊 𝗙𝗟𝗢𝗪 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 】
  ✦ `.swipe <text>`     → swipe with custom text
  ✦ `.swipe`            → swipe using default texts
  ✦ `.stopswipe`        → stop swipe flood

【 🚀 𝗙𝗟𝗢𝗪 𝗦𝗣𝗘𝗘𝗗 】
  ✦ `.flowdelay <sec>`  → set delay between messages
  ✦ `.flowcount <n>`    → set number of messages per swipe

【 💡 𝗧𝗜𝗣 】
  Swipe uses the powerful text library from BEBO.
  You can also add your own texts with `.addtext`.

╔═══════════════════════════════════════════╗
║          🌊  BEBO — 𝗙𝗹𝗼𝘄 𝘄𝗶𝘁𝗵 𝗣𝗼𝘄𝗲𝗿       ║
╚═══════════════════════════════════════════╝
        """
        await msg.edit(menu)

    @command("help")
    async def cmd_help(event):
        await cmd_menu(event)

    # ------------------------- FLOW BOT -------------------------
    async def swipe_loop(chat, text):
        try:
            for _ in range(state.flow_count):
                if not state.flow_mode or "swipe" not in state.active_tasks: break
                try: await client.send_message(chat, text)
                except: pass
                await asyncio.sleep(state.flow_delay)
        except asyncio.CancelledError: pass
        finally: state.active_tasks.pop("swipe", None)

    @flow_command("swipe")
    async def cmd_swipe(event):
        args = event.raw_text.split(maxsplit=1)
        text = args[1] if len(args) > 1 else (random.choice(state.saved_texts) if state.saved_texts else random.choice(all_texts))
        if "swipe" in state.active_tasks: state.active_tasks["swipe"].cancel()
        state.active_tasks["swipe"] = asyncio.create_task(swipe_loop(event.chat, text))
        await event.reply(f"✅ Swipe started! {state.flow_count} messages with delay {state.flow_delay}s.")

    @flow_command("stopswipe")
    async def cmd_stopswipe(event):
        if "swipe" in state.active_tasks:
            state.active_tasks["swipe"].cancel()
            await event.reply("✅ Swipe stopped.")
        else: await event.reply("ℹ️ No active swipe.")

    @flow_command("flowdelay")
    async def cmd_flowdelay(event):
        try:
            val = float(event.raw_text.split(maxsplit=1)[1])
            if val < 0.05: return await event.reply("⚠️ Min 0.05s")
            state.flow_delay = val
            await event.reply(f"✅ Flow delay set to {state.flow_delay}s")
        except: await event.reply("⚠️ Invalid delay.")

    @flow_command("flowcount")
    async def cmd_flowcount(event):
        try:
            val = int(event.raw_text.split(maxsplit=1)[1])
            if val < 1: return await event.reply("⚠️ Min 1")
            state.flow_count = val
            await event.reply(f"✅ Flow count set to {state.flow_count}")
        except: await event.reply("⚠️ Invalid count.")

    # ------------------------- BEAUTIFICATION -------------------------
    @command("start")
    async def cmd_start_ub(event):
        msg = await event.reply("⏳ **Starting BEBO...**")
        for i in range(1, 11):
            bar = "█" * i + "░" * (10 - i)
            await msg.edit(f"⏳ **Loading BEBO**  [{bar}] {i*10}%")
            await asyncio.sleep(0.3)
        await cmd_menu(event)
        await msg.delete()

    BANNER = r"""
  ╔═╗╦ ╦╔═╗╔═╗╔═╗
  ║ ╦║ ║║ ╦║╣ ╚═╗
  ╚═╝╚═╝╚═╝╚═╝╚═╝
  ╔═╗╔╗╔╔═╗╦ ╦╔═╗
  ╠═╣║║║║ ╦║ ║║╣
  ╩ ╩╝╚╝╚═╝╚═╝╚═╝
          💖 𝐁𝐄𝐁𝐎 💖
"""
    @command("welcome")
    async def cmd_welcome(event):
        await event.reply(f"╔══════════════════════════════════════════╗\n║                                          ║\n║   ✨  𝐖𝐄𝐋𝐂𝐎𝐌𝐄  𝐓𝐎  𝐁𝐄𝐁𝐎  ✨     ║\n║                                          ║\n║   💖  The most powerful userbot          ║\n║   ⚡  Fast, reliable, and stylish        ║\n║                                          ║\n║   🛠️  Use `.menu` to explore             ║\n║   🌊  Use `.flowmenu` for Flow mode      ║\n║                                          ║\n║   🎀  Made with ❤️ for the community    ║\n║                                          ║\n╚══════════════════════════════════════════╝\n\n{BANNER}")

    @command("about")
    async def cmd_about(event):
        await event.reply("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n      💖  𝐀𝐁𝐎𝐔𝐓  𝐁𝐄𝐁𝐎  💖\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n  🔹 **Version** : 4.0 (Ultimate Dynamic Edition)\n  🔹 **Author**  : BEBO Team\n  🔹 **License** : All Rights Reserved\n  🔹 **Language** : Python (Telethon)\n\n  🌟 **Features** :\n  • Merged BEBO engines\n  • Advanced Security & Defense protocols\n  • Ultra‑fast raid & spam (Tsunami, Blitz)\n  • Intelligent Auto-Delete & Smart Mute\n  • Flow mode with swipe flood\n  • 500+ built‑in texts\n  • Cloud dummy server\n\n  💡 **Credits** : Powered by Telethon\n  🛡️ **BEBO** — Built with ❤️.\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    @command("banner")
    async def cmd_banner(event): await event.reply(f"`{BANNER}`")

    # ------------------------- ADVANCED TOOLS -------------------------
    @command("sabchup")
    async def sabchup_cmd(event):
        msg = await event.respond("🔒 **LOCKING ALL MESSAGES...**")
        await asyncio.sleep(0.3)
        state.auto_delete_chats[event.chat_id] = True
        await msg.edit("🤐 **SABCHUP MODE ON** (0.05s delay)")

    @command("speakall")
    async def speakall_cmd(event):
        msg = await event.respond("🔓 **UNLOCKING MESSAGES...**")
        await asyncio.sleep(0.3)
        state.auto_delete_chats.pop(event.chat_id, None)
        state.delete_target_users.pop(event.chat_id, None)
        state.delete_target_usernames.pop(event.chat_id, None)
        await msg.edit("🗣️ **SPEAKALL - Auto-delete OFF**")

    @command("chup")
    async def chup_cmd(event):
        if event.is_reply:
            reply_msg = await event.get_reply_message()
            uid = reply_msg.sender_id
            username = getattr(getattr(reply_msg, 'sender', None), 'username', None)
            state.delete_target_users[event.chat_id].add(uid)
            if username: state.delete_target_usernames[event.chat_id].add(username.lower())
            state.auto_delete_chats[event.chat_id] = True
            msg = await event.respond("🎯 **TARGET ACQUIRED...**")
            await asyncio.sleep(0.3)
            await msg.edit(f"🤐 **CHUP!** (User muted forever)")
        else: await event.respond("Reply to a message with `.chup`")

    @command("bol")
    async def bol_cmd(event):
        if event.is_reply:
            reply_msg = await event.get_reply_message()
            uid = reply_msg.sender_id
            username = getattr(getattr(reply_msg, 'sender', None), 'username', None)
            if event.chat_id in state.delete_target_users: state.delete_target_users[event.chat_id].discard(uid)
            if username and event.chat_id in state.delete_target_usernames: state.delete_target_usernames[event.chat_id].discard(username.lower())
            msg = await event.respond("🔄 **RELEASING TARGET...**")
            await asyncio.sleep(0.3)
            await msg.edit(f"🗣️ **BOL!** (User unmuted)")
        else: await event.respond("Reply to a message with `.bol`")

    @command("safe")
    async def safe_cmd(event):
        args = event.text.strip().split()[1:]
        if not args and not event.is_reply:
            if not state.safe_users: return await event.respond("🛡️ **Safe list empty**\nUse: `.safe @user`")
            else: return await event.respond(f"🛡️ **Safe users:** {len(state.safe_users)}")
        if event.is_reply:
            reply_msg = await event.get_reply_message()
            uid = reply_msg.sender_id
            username = getattr(getattr(reply_msg, 'sender', None), 'username', None)
            state.safe_users.add(uid)
            if username: state.safe_usernames[username.lower()] = uid
            return await event.respond(f"✅ **Protected user**")
        for arg in args:
            username = arg.lstrip('@')
            try:
                ent = await client.get_entity(username)
                state.safe_users.add(ent.id)
                state.safe_usernames[username.lower()] = ent.id
            except: pass
        await event.respond(f"✅ **Protected {len(args)} users**")

    @client.on(events.NewMessage(pattern=r'^\.boost (on|off)$'))
    async def boost_cmd(event):
        if not await is_authorized(event): return
        state.boost_mode = event.pattern_match.group(1) == "on"
        state.cfg = state.boost_cfg.copy() if state.boost_mode else state.normal_cfg.copy()
        await event.respond(f"⚡ **BOOST MODE:** {'ON' if state.boost_mode else 'OFF'}")
        await event.delete()

    @client.on(events.NewMessage(pattern=r'^\.assist (on|off)$'))
    async def assist_cmd(event):
        if not await is_authorized(event): return
        state.critical_mode = event.pattern_match.group(1) == "on"
        state.cfg = state.crit_cfg.copy() if state.critical_mode else state.normal_cfg.copy()
        await event.respond(f"🛡️ **CRITICAL MODE:** {'ON' if state.critical_mode else 'OFF'}")
        await event.delete()

    @command("perf")
    async def perf_cmd(event):
        up = int(time.monotonic() - state.metrics["start"])
        rate = state.metrics["msg"] / max(1, up)
        await event.respond(f"⟦ LIVE PERFORMANCE ⟧\nUptime: {up}s\nMsg/s: {rate:.2f}\nMutes: {state.metrics['mutes']}\nBoost: {state.boost_mode}\nCritical: {state.critical_mode}")
        await event.delete()

    @command("autoswipe")
    async def autoswipe_cmd(event):
        args = event.text.strip().split(None, 1)
        if len(args) < 2: return await event.respond("**Usage:** `.autoswipe <text>`")
        state.autoswipe_active[event.chat_id] = args[1]
        await event.respond(f"🔄 **AUTO-SWIPE ON:** {args[1]}")

    @command("stopautoswipe")
    async def stopautoswipe_cmd(event):
        state.autoswipe_active.pop(event.chat_id, None)
        await event.respond("✅ **AUTO-SWIPE OFF**")

    @command("advmultireply")
    async def advmultireply_cmd(event):
        args = event.text.strip().split(None, 2)
        if len(args) < 3: return await event.respond("**Usage:** `.advmultireply <times> <text>`")
        try:
            times = int(args[1])
            if not (1 <= times <= 50): return await event.respond("⚠️ **Times 1-50**")
            state.autoswipe_active[event.chat_id] = f"MULTI:{times}:{args[2]}"
            msg = await event.respond("🔁 **INITIALIZING MULTI-REPLY...**")
            await asyncio.sleep(0.3)
            await msg.edit(f"🔁 **MULTI-REPLY ON**\n📢 Sending {times}x: {args[2]}")
        except: return await event.respond("❌ **Invalid number!**")

    @command("stopadvmultireply")
    async def stopadvmultireply_cmd(event):
        if event.chat_id in state.autoswipe_active and str(state.autoswipe_active[event.chat_id]).startswith("MULTI:"):
            del state.autoswipe_active[event.chat_id]
            return await event.respond("✅ **MULTI-REPLY OFF**")
        await event.respond("❌ **Multi-reply is not active**")

    @command("namechange")
    async def namechange_cmd(event):
        args = event.text.strip().split()
        delay, mode = 0.1, "normal"
        if len(args) > 1:
            if args[1].lower() in ['time', 'emoji', 'owns', 'enters', 'dad']:
                mode = args[1].lower()
                if len(args) > 2:
                    try: delay = float(args[2]) / 1000
                    except: pass
            else:
                try: delay = float(args[1]) / 1000
                except: pass

        chat_id = event.chat_id
        try:
            chat = await event.get_chat()
            if not hasattr(chat, 'title'): return await event.respond("❌ **Groups only!**")
        except: return await event.respond("❌ **Cannot access chat**")

        state.namechange_active[chat_id] = True
        msg = await event.respond("🔄 **PREPARING NAME CHANGE MODULE...**")
        await asyncio.sleep(0.3)
        await msg.edit(f"🔄 **NAME CHANGE ON**\n📝 Mode: {mode}\n⏱️ {delay*1000:.0f}ms")

        async def namechange_task():
            original_title = chat.title
            counter = 0
            is_channel = hasattr(chat, 'megagroup') or hasattr(chat, 'broadcast')
            while state.namechange_active.get(chat_id):
                try:
                    curr_delay = state.namechange_delays.get(chat_id, delay)
                    if mode == 'time': new_name = f"⏰ {datetime.now().strftime('%H:%M:%S')} {random.choice(RANDOM_EMOJIS)} {original_title}"
                    elif mode == 'emoji': new_name = f"{''.join([random.choice(RANDOM_EMOJIS) for _ in range(5)])} {original_title} {''.join([random.choice(COUNTRY_EMOJIS) for _ in range(3)])}"
                    elif mode == 'owns': new_name = f"👑 BEBO OWNS {random.choice(RANDOM_EMOJIS)} {original_title} {random.choice(COUNTRY_EMOJIS)}"
                    elif mode == 'enters': new_name = f"🚪 BEBO ENTERS {random.choice(RANDOM_EMOJIS)} {original_title} 🔥"
                    elif mode == 'dad': new_name = f"👨 BEBO YOUR DAD {random.choice(RANDOM_EMOJIS)} {original_title} 💀"
                    else: new_name = f"{random.choice(RANDOM_EMOJIS)} {original_title} {random.choice(COUNTRY_EMOJIS)} #{counter}"

                    if is_channel: await client(EditTitleRequest(channel=chat_id, title=new_name))
                    else: await client(EditChatTitleRequest(chat_id=chat_id, title=new_name))
                    counter += 1
                    await asyncio.sleep(curr_delay)
                except Exception: continue
            state.namechange_active.pop(chat_id, None)

        state.active_tasks[f"nm_{chat_id}"] = asyncio.create_task(namechange_task())

    @command("namedelay")
    async def namedelay_cmd(event):
        args = event.text.strip().split()
        if event.chat_id not in state.namechange_active: return await event.respond("❌ **Not active!**")
        if len(args) < 2: return await event.respond("⚙️ **Usage:** `.namedelay <ms>`")
        try:
            state.namechange_delays[event.chat_id] = float(args[1]) / 1000
            await event.respond(f"⚙️ **Delay changed to: {args[1]}ms**")
        except: await event.respond("❌ **Invalid delay amount!**")

    @command("stopnamechange")
    async def stopnamechange_cmd(event):
        if event.chat_id in state.namechange_active:
            state.namechange_active.pop(event.chat_id, None)
            task = state.active_tasks.pop(f"nm_{event.chat_id}", None)
            if task: task.cancel()
            await event.respond("✅ **NAME CHANGE STOPPED**")

    @command("blitz")
    async def blitz_cmd(event):
        chat_id = event.chat_id
        try:
            chat = await event.get_chat()
            if not hasattr(chat, 'title'): return
        except: return
        
        original_title = chat.title
        is_channel = hasattr(chat, 'megagroup') or hasattr(chat, 'broadcast')
        state.blitz_active[chat_id] = True
        
        msg = await event.respond("⚡ **WARMING UP BLITZ...**")
        await asyncio.sleep(0.3)
        status_msg = await msg.edit(f"⚡ **BEBO BLITZ MODE**\n🎯 100K changes\n💀 3s flood waits")

        async def blitz_task():
            counter, flood_waits = 0, 0
            start_time = time.time()
            while counter < 100000 and state.blitz_active.get(chat_id):
                try:
                    new_name = f"{random.choice(RANDOM_EMOJIS)} {original_title} {random.choice(COUNTRY_EMOJIS)} #{counter}"
                    if is_channel: await client(EditTitleRequest(channel=chat_id, title=new_name))
                    else: await client(EditChatTitleRequest(chat_id=chat_id, title=new_name))
                    counter += 1
                    if counter % 1000 == 0:
                        try: await status_msg.edit(f"⚡ **BEBO BLITZ**\n📊 {counter:,}/100K\n⚡ {counter / max(1, time.time() - start_time):.1f}/s\n💀 Floods: {flood_waits}")
                        except: pass
                except Exception as e:
                    if 'flood' in str(e).lower():
                        flood_waits += 1
                        await asyncio.sleep(3)
                    continue
            state.blitz_active.pop(chat_id, None)
            try: await status_msg.edit(f"✅ **BEBO BLITZ COMPLETE OR STOPPED!**\n📊 {counter:,}\n⏱️ {time.time() - start_time:.1f}s\n🔥 DONE!")
            except: pass

        state.active_tasks[f"blitz_{chat_id}"] = asyncio.create_task(blitz_task())

    @command("stopblitz")
    async def stopblitz_cmd(event):
        if event.chat_id in state.blitz_active:
            state.blitz_active.pop(event.chat_id, None)
            task = state.active_tasks.pop(f"blitz_{event.chat_id}", None)
            if task: task.cancel()
            await event.respond("✅ **BLITZ STOPPED**")

    @command("lockname")
    async def lockname_cmd(event):
        chat = await event.get_chat()
        state.locked_titles[event.chat_id] = chat.title
        await event.respond(f"🔒 **NAME LOCKED BY BEBO:** {chat.title}")

    @command("lockgroup")
    async def lockgroup_cmd(event):
        state.locked_groups.add(event.chat_id)
        await event.respond("🔐 **GROUP LOCKED BY BEBO**")

    @command("unlockgroup")
    async def unlockgroup_cmd(event):
        state.locked_groups.discard(event.chat_id)
        await event.respond("🔓 **UNLOCKED BY BEBO**")

    @command("lockchat")
    async def lockchat_cmd(event):
        state.locked_chat.add(event.chat_id)
        await event.respond("💬 **CHAT LOCKED BY BEBO**")

    @command("unlockchat")
    async def unlockchat_cmd(event):
        state.locked_chat.discard(event.chat_id)
        await event.respond("💬 **CHAT UNLOCKED BY BEBO**")

    @command("locknamechange")
    async def locknamechange_cmd(event):
        chat = await event.get_chat()
        state.locked_name_change.add(event.chat_id)
        state.locked_titles[event.chat_id] = chat.title
        await event.respond(f"🔒 **NAME CHANGE LOCKED BY BEBO**")

    @command("unlocknamechange")
    async def unlocknamechange_cmd(event):
        state.locked_name_change.discard(event.chat_id)
        await event.respond("🔓 **NAME CHANGE UNLOCKED BY BEBO**")

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
            except: pass
        await status_msg.edit(f"✅ **BEBO SENT {sent} COMMANDS**")
        await asyncio.sleep(2)
        await status_msg.delete()

    @command("killname")
    async def killname_cmd(event):
        args = event.text.strip().split(None, 1)
        chat_id = event.chat_id
        if len(args) > 1: original_name = args[1]
        else:
            try: chat = await event.get_chat(); original_name = chat.title.split()[0]
            except: original_name = "Group"
        status_msg = await event.respond("💀 **BEBO IS KILLING NAME CHANGERS...**")
        for cmd in ['.stopnamechange', '.stopname', '.stopnm', '.stop']:
            try: msg = await client.send_message(chat_id, cmd); await asyncio.sleep(0.05); await msg.delete()
            except: pass
        try:
            chat = await event.get_chat()
            is_channel = hasattr(chat, 'megagroup') or hasattr(chat, 'broadcast')
            for _ in range(5):
                try:
                    if is_channel: await client(EditTitleRequest(channel=chat_id, title=original_name))
                    else: await client(EditChatTitleRequest(chat_id=chat_id, title=original_name))
                    await asyncio.sleep(0.2)
                except: pass
            await status_msg.edit(f"✅ **BEBO TERMINATED THE PROCESS!**\n📝 {original_name}")
        except: await status_msg.edit("⚠️ **Sent commands**")
        await asyncio.sleep(2)
        await status_msg.delete()

    @command("dominate")
    async def dominate_cmd(event):
        chat_id = event.chat_id
        if chat_id in state.adv_spam_active and 'DOMINATE' in str(state.adv_spam_active.get(chat_id, '')): return await event.respond("⚠️ **Already active!**")
        all_stop_commands = ['.stop', '.stopall', '.end', '.stopadvspam', '.stopspray', '.stopraid', '.stopnamechange', '.stopdel', '.stopswipe', '.stoppromote', '.stopkick', '.stopban']
        state.adv_spam_active[chat_id] = 'DOMINATE_MODE_ACTIVE'
        msg = await event.respond("🔌 **POWERING UP DOMINATION...**")
        await asyncio.sleep(0.3)
        await msg.edit("👑 **BEBO DOMINATION ON**\n💀 Blocking all enemy bots!")
        
        async def dominate_task():
            while state.adv_spam_active.get(chat_id) == 'DOMINATE_MODE_ACTIVE':
                try:
                    m = await client.send_message(chat_id, random.choice(all_stop_commands))
                    await asyncio.sleep(0.01)
                    try: await m.delete()
                    except: pass
                except: continue
                
        state.active_tasks[f"dominate_{chat_id}"] = asyncio.create_task(dominate_task())

    @command("stopdominate")
    async def stopdominate_cmd(event):
        if event.chat_id in state.adv_spam_active and 'DOMINATE' in str(state.adv_spam_active.get(event.chat_id, '')):
            del state.adv_spam_active[event.chat_id]
            task = state.active_tasks.pop(f"dominate_{event.chat_id}", None)
            if task: task.cancel()
            await event.respond("✅ **BEBO DOMINATION STOPPED**")

    @command("emergency")
    async def emergency_cmd(event):
        chat_id = event.chat_id
        if state.emergency_active.get(chat_id): return await event.respond("⚠️ **Already active!**")
        state.emergency_active[chat_id] = True
        msg = await event.respond("⚠️ **WARNING: ENGAGING OVERDRIVE...**")
        await asyncio.sleep(0.3)
        await msg.edit("🚨 **BEBO EMERGENCY MODE** 🚨\n\n💀 **MAXIMUM OVERDRIVE!**\n⚡ 1000 changes/sec\n💥 1000 msgs/sec\n🔁 100x replies\n\n⚠️ **OVERWHELMING SPEED!**")

        async def emergency_namechange():
            try:
                chat = await event.get_chat()
                if not hasattr(chat, 'title'): return
                original_title = chat.title
                is_channel = hasattr(chat, 'megagroup') or hasattr(chat, 'broadcast')
                counter = 0
                while state.emergency_active.get(chat_id):
                    try:
                        new_name = f"{random.choice(RANDOM_EMOJIS)}💀BEBO EMERGENCY💀 {original_title} #{counter}"
                        if is_channel: await client(EditTitleRequest(channel=chat_id, title=new_name))
                        else: await client(EditChatTitleRequest(chat_id=chat_id, title=new_name))
                        counter += 1
                        await asyncio.sleep(0.001)
                    except: await asyncio.sleep(0.001)
            except: pass

        async def emergency_spam():
            while state.emergency_active.get(chat_id):
                try:
                    await client.send_message(chat_id, "🚨 BEBO EMERGENCY 🚨")
                    await asyncio.sleep(0.001)
                except: await asyncio.sleep(0.001)

        state.autoswipe_active[chat_id] = "MULTI:100:🚨 BEBO EMERGENCY 🚨"
        state.active_tasks[f"em_nm_{chat_id}"] = asyncio.create_task(emergency_namechange())
        state.active_tasks[f"em_sp_{chat_id}"] = asyncio.create_task(emergency_spam())

    @command("stopemergency")
    async def stopemergency_cmd(event):
        chat_id = event.chat_id
        if state.emergency_active.get(chat_id):
            state.emergency_active[chat_id] = False
            state.autoswipe_active.pop(chat_id, None)
            for t in [f"em_nm_{chat_id}", f"em_sp_{chat_id}"]:
                task = state.active_tasks.pop(t, None)
                if task: task.cancel()
            await event.respond("✅ **BEBO EMERGENCY STOPPED**")

    @command("makegc")
    async def makegc_cmd(event):
        args = event.text.strip().split(maxsplit=1)
        if len(args) < 2: return await event.respond("Usage: `.makegc <name>`")
        title = args[1]
        try:
            msg = await event.respond(f"🛠️ **CREATING CHAT...**")
            await asyncio.sleep(0.3)
            await client(CreateChatRequest(users=[user_id], title=title))
            await msg.edit(f"✅ **BEBO Created Chat:** {title}")
        except Exception as e: await event.respond(f"❌ {str(e)[:50]}")

    @command("lockswipe")
    async def lockswipe_cmd(event):
        parts = event.text.strip().split(maxsplit=2)
        if len(parts) < 3: return await event.respond("Usage: `.lockswipe @username <text>`")
        username, text = parts[1].lstrip('@'), parts[2]
        try:
            ent = await client.get_entity(username)
            state.swipe_targets[event.chat_id][ent.id] = text
            await event.respond(f"🔒 **LOCKED SWIPE BY BEBO:** @{username}")
        except: await event.respond("❌ **Failed**")

    if GTTS_AVAILABLE:
        @command("hindivoice")
        async def hindivoice_cmd(event):
            args = event.text.strip().split(maxsplit=1)
            if len(args) < 2: return await event.respond("Usage: `.hindivoice <text>`")
            text = args[1]
            file_name = f"hindi_{int(time.time())}.ogg"
            try:
                gTTS(text=text, lang="hi").save(file_name)
                await client.send_file(event.chat_id, file_name, voice_note=True)
                os.remove(file_name)
            except Exception as e: await event.respond(f"❌ {str(e)[:50]}")
            await event.delete()

    # ------------------------- UTILITIES -------------------------
    @command("id")
    async def cmd_id(event):
        args = event.raw_text.split(maxsplit=1)
        if len(args) > 1:
            target = args[1].strip()
            try:
                if target.startswith("@"): target = target[1:]
                if target.isdigit(): entity = await client.get_entity(int(target))
                else: entity = await client.get_entity(target)
                await event.reply(f"🆔 **ID** of `{utils.get_display_name(entity)}` : `{entity.id}`")
            except Exception as e: await event.reply(f"❌ Could not fetch ID: {e}")
        else:
            chat = await event.get_chat()
            sender = await event.get_sender()
            await event.reply(f"📌 **Current Chat ID** : `{event.chat_id}`\n👤 **Your ID** : `{sender.id}`\n📛 **Chat Title** : `{getattr(chat, 'title', 'N/A')}`")

    @command("tagall")
    async def cmd_tagall(event):
        if not event.is_group: return await event.reply("⚠️ Groups only.")
        args = event.raw_text.split(maxsplit=1)
        custom_text = args[1] if len(args) > 1 else "Attention!"
        try:
            participants = await client.get_participants(event.chat)
            mentions = [f"@{u.username}" if u.username else f"[{u.first_name}](tg://user?id={u.id})" for u in participants if not (u.bot or u.deleted)]
            if not mentions: return await event.reply("No active members found.")
            for i in range(0, len(mentions), 50):
                await client.send_message(event.chat, f"{custom_text}\n" + " ".join(mentions[i:i+50]))
                await asyncio.sleep(1)
            await event.reply(f"✅ Tagged {len(mentions)} members.")
        except Exception as e: await event.reply(f"❌ Failed: {e}")

    @command("warn")
    async def cmd_warn(event):
        user = await get_user_from_arg(event)
        if not user: return
        state.warnings[user.id] = state.warnings.get(user.id, 0) + 1
        count = state.warnings[user.id]
        msg = f"⚠️ **{utils.get_display_name(user)}** has been warned ({count}/3)."
        if count >= 3:
            msg += "\n🔨 Auto‑kick activated! Kicking user..."
            await event.reply(msg)
            try: await client.kick_participant(event.chat, user)
            except Exception as e: await event.reply(f"❌ Could not kick: {e}")
            del state.warnings[user.id]
        else: await event.reply(msg)

    @command("kickme")
    async def cmd_kickme(event):
        await event.reply("👋 Leaving this group...")
        await client.leave_chat(event.chat)

    @command("join")
    async def cmd_join(event):
        args = event.raw_text.split(maxsplit=1)
        if len(args) < 2: return await event.reply("⚠️ Usage: `.join <invite_link>`")
        try:
            await client.join_channel(args[1].strip())
            await event.reply(f"✅ Joined: {args[1].strip()}")
        except Exception as e: await event.reply(f"❌ Failed to join: {e}")

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
                except Exception as e: await event.reply(f"❌ Failed: {e}")
            else: await event.reply("⚠️ Reply to a photo message.")
        else: await event.reply("⚠️ Reply to a photo with `.setpfp`.")

    @command("setname")
    async def cmd_setname(event):
        args = event.raw_text.split(maxsplit=1)
        if len(args) < 2: return await event.reply("⚠️ Usage: `.setname <name>`")
        try:
            await client.edit_profile(first_name=args[1])
            await event.reply(f"✅ Name changed to: **{args[1]}**")
        except Exception as e: await event.reply(f"❌ Failed: {e}")

    @command("setbio")
    async def cmd_setbio(event):
        args = event.raw_text.split(maxsplit=1)
        if len(args) < 2: return await event.reply("⚠️ Usage: `.setbio <bio>`")
        try:
            await client.edit_profile(about=args[1])
            await event.reply(f"✅ Bio updated.")
        except Exception as e: await event.reply(f"❌ Failed: {e}")

    @command("adminlist")
    async def cmd_adminlist(event):
        if not event.is_group: return await event.reply("⚠️ Groups only.")
        try:
            admins = [f"• {utils.get_display_name(p)}" async for p in client.iter_participants(event.chat, filter="admin")]
            if admins: await event.reply(f"👑 **Admins** :\n" + "\n".join(admins))
            else: await event.reply("No admins found.")
        except Exception as e: await event.reply(f"❌ Failed: {e}")

    @command("banlist")
    async def cmd_banlist(event):
        if not event.is_group: return await event.reply("⚠️ Groups only.")
        try:
            banned = [f"• {utils.get_display_name(p)}" async for p in client.iter_participants(event.chat, filter="banned")]
            if banned: await event.reply(f"🚫 **Banned Users** :\n" + "\n".join(banned))
            else: await event.reply("No banned users.")
        except Exception as e: await event.reply(f"❌ Failed: {e}")

    @command("slowmode")
    async def cmd_slowmode(event):
        args = event.raw_text.split(maxsplit=1)
        if len(args) < 2: return await event.reply("⚠️ Usage: `.slowmode <seconds>` (0 to disable)")
        try:
            seconds = int(args[1])
            await client.edit_admin(event.chat, ChatAdminRights(slowmode=seconds))
            await event.reply(f"✅ Slow mode set to {seconds} seconds.")
        except Exception as e: await event.reply(f"❌ Failed: {e}")

    @command("setgrouptitle")
    async def cmd_setgrouptitle(event):
        if not event.is_group: return await event.reply("⚠️ Groups only.")
        args = event.raw_text.split(maxsplit=1)
        if len(args) < 2: return await event.reply("⚠️ Usage: `.setgrouptitle <title>`")
        try:
            await client.edit_group_title(event.chat, args[1])
            await event.reply(f"✅ Group title changed to: **{args[1]}**")
        except Exception as e: await event.reply(f"❌ Failed: {e}")

    @command("setgrouppic")
    async def cmd_setgrouppic(event):
        if not event.is_group: return await event.reply("⚠️ Groups only.")
        if event.reply_to_msg_id:
            msg = await event.get_reply_message()
            if msg.photo:
                try:
                    await client.download_media(msg.photo, "temp_grouppic.jpg")
                    await client.edit_group_photo(event.chat, "temp_grouppic.jpg")
                    os.remove("temp_grouppic.jpg")
                    await event.reply("✅ Group photo updated.")
                except Exception as e: await event.reply(f"❌ Failed: {e}")
            else: await event.reply("⚠️ Reply to a photo.")
        else: await event.reply("⚠️ Reply to a photo with `.setgrouppic`.")

    @command("autoreply")
    async def cmd_autoreply(event):
        args = event.raw_text.split(maxsplit=1)
        if len(args) < 2: return await event.reply(f"ℹ️ Auto‑reply is currently **{'ON' if state.auto_reply_on else 'OFF'}**.")
        if args[1].lower() == "on": state.auto_reply_on = True; await event.reply("✅ Auto‑reply enabled.")
        elif args[1].lower() == "off": state.auto_reply_on = False; await event.reply("✅ Auto‑reply disabled.")
        else: await event.reply("⚠️ Usage: `.autoreply on/off`")

    @client.on(events.NewMessage)
    async def auto_reply_handler(event):
        if not state.auto_reply_on or event.sender_id == user_id: return
        if event.is_group or event.is_private:
            reply = random.choice(state.saved_texts) if state.saved_texts else random.choice(all_texts)
            try: await event.reply(reply)
            except Exception as e: logger.warning(f"Auto‑reply failed: {e}")

    # ------------------------- FUN -------------------------
    motivation_quotes = [
        "Believe you can and you're halfway there. – Theodore Roosevelt",
        "The only way to do great work is to love what you do. – Steve Jobs",
        "Success is not final, failure is not fatal: it is the courage to continue that counts. – Winston Churchill",
        "The future belongs to those who believe in the beauty of their dreams. – Eleanor Roosevelt",
        "It does not matter how slowly you go as long as you do not stop. – Confucius",
    ]
    @command("motivate")
    async def cmd_motivate(event): await event.reply(f"💪 **Motivation** : {random.choice(motivation_quotes)}")

    truths = [
        "What is the biggest lie you've ever told?",
        "Have you ever cheated on a test?",
        "What is the most embarrassing thing you've done in public?",
        "Who is your secret crush?",
        "Have you ever lied to your best friend?",
    ]
    @command("truth")
    async def cmd_truth(event): await event.reply(f"🔮 **Truth** : {random.choice(truths)}")

    dares = [
        "Do 20 push-ups right now.",
        "Sing the national anthem loudly.",
        "Send a random emoji to your last chat.",
        "Speak in a British accent for the next 5 minutes.",
        "Swap your profile picture with a meme for an hour.",
    ]
    @command("dare")
    async def cmd_dare(event): await event.reply(f"⚡ **Dare** : {random.choice(dares)}")

    shayaris = [
        "तुम्हें देखा तो ये ख़याल आया,\nज़िन्दगी धूप, तुम घना साया।",
        "मोहब्बत की राहें मुश्किल हैं,\nफिर भी हमने ये राह चुनी है।",
        "तेरी यादों में बीती है रात,\nसुबह हुई तो फिर से तेरी बात।",
        "तेरे बिना दिल है बेकरार,\nमाँग ले मुझसे हर बार प्यार।",
    ]
    @command("shayari")
    async def cmd_shayari(event): await event.reply(f"💕 **Shayari** :\n{random.choice(shayaris)}")

    jokes = [
        "Why don't scientists trust atoms? Because they make up everything!",
        "What do you call a bear with no teeth? A gummy bear!",
        "Why did the scarecrow win an award? Because he was outstanding in his field!",
        "What do you call fake spaghetti? An impasta!",
    ]
    @command("joke")
    async def cmd_joke(event): await event.reply(f"😂 **Joke** : {random.choice(jokes)}")

    quotes = [
        "The only limit to our realization of tomorrow is our doubts of today. – FDR",
        "In the middle of difficulty lies opportunity. – Einstein",
        "Do or do not. There is no try. – Yoda",
        "Be the change you wish to see in the world. – Gandhi",
    ]
    @command("quote")
    async def cmd_quote(event): await event.reply(f"📖 **Quote** : {random.choice(quotes)}")


# ════════════════════════════════════════════════════════════════════════════════
#   DATABASE MANAGER
# ════════════════════════════════════════════════════════════════════════════════
class DBManager:
    def __init__(self, filename="hosting_db.json"):
        self.filename = filename
        self.data = {
            "users": {}, 
            "accounts": {}, 
            "blocked": [],
            "sudo": [],
            "bot_settings": {"is_on": True},
            "welcome_video": None
        }
        self.load()

    def load(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r") as f:
                    self.data = json.load(f)
            except Exception: pass

    def save(self):
        try:
            with open(self.filename, "w") as f:
                json.dump(self.data, f, indent=2)
        except Exception: pass

    def is_sudo(self, uid, owner_id):
        return uid == owner_id or uid in self.data.get("sudo", [])

    def is_blocked(self, uid):
        return uid in self.data.get("blocked", [])

    def user_exists(self, uid):
        return str(uid) in self.data.get("users", {})

    def save_user_meta(self, uid, meta):
        uid = str(uid)
        if uid not in self.data["users"]:
            self.data["users"][uid] = {}
        self.data["users"][uid].update(meta)
        self.save()

    def get_accounts(self, uid):
        uid = str(uid)
        accs = self.data["accounts"].get(uid, {})
        return list(accs.values())

    def get_account(self, uid, slot):
        uid = str(uid)
        return self.data["accounts"].get(uid, {}).get(str(slot))

    def add_account(self, uid, acc_dict):
        uid = str(uid)
        if uid not in self.data["accounts"]:
            self.data["accounts"][uid] = {}
        self.data["accounts"][uid][str(acc_dict["slot"])] = acc_dict
        self.save()

    def remove_account(self, uid, slot):
        uid = str(uid)
        if uid in self.data["accounts"] and str(slot) in self.data["accounts"][uid]:
            del self.data["accounts"][uid][str(slot)]
            self.save()

    def get_welcome_video(self):
        return self.data.get("welcome_video")

    def set_welcome_video(self, data):
        self.data["welcome_video"] = data
        self.save()

    def remove_welcome_video(self):
        self.data["welcome_video"] = None
        self.save()

    def hosted_count(self):
        return sum(len(accs) for accs in self.data["accounts"].values())

    def get_all_users(self):
        return list(self.data["users"].keys())

    def user_count(self):
        return len(self.data["users"])

    def get_blocked(self):
        return self.data.get("blocked", [])

    def block_user(self, uid):
        if uid not in self.data["blocked"]:
            self.data["blocked"].append(uid)
            self.save()

    def unblock_user(self, uid):
        if uid in self.data["blocked"]:
            self.data["blocked"].remove(uid)
            self.save()

    def get_sudo_users(self):
        return self.data.get("sudo", [])

    def add_sudo(self, uid):
        if uid not in self.data["sudo"]:
            self.data["sudo"].append(uid)
            self.save()

    def remove_sudo(self, uid):
        if uid in self.data["sudo"]:
            self.data["sudo"].remove(uid)
            self.save()

    def is_bot_on(self):
        return self.data.get("bot_settings", {}).get("is_on", True)

    def set_bot_settings(self, settings):
        if "bot_settings" not in self.data:
            self.data["bot_settings"] = {}
        self.data["bot_settings"].update(settings)
        self.save()

db = DBManager()

# ════════════════════════════════════════════════════════════════════════════════
#   RUNNER MANAGER
# ════════════════════════════════════════════════════════════════════════════════
active_runtimes = {}

def _run_telethon_client(uid, slot, api_id, api_hash, session_string):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        client = TelegramClient(StringSession(session_string), int(api_id), api_hash, loop=loop)
        
        # Attach the full BEBO userbot engine logic
        register_userbot_engine(client, int(uid))
        
        loop.run_until_complete(client.connect())
        if not loop.run_until_complete(client.is_user_authorized()):
            logger.warning(f"Userbot {uid}:{slot} is not authorized.")
            return
            
        active_runtimes[(str(uid), str(slot))] = {
            "client": client,
            "loop": loop,
            "start_time": time.time()
        }
        logger.info(f"Userbot successfully started for user {uid} (slot {slot})")
        loop.run_until_complete(client.run_until_disconnected())
    except Exception as e:
        logger.error(f"Userbot thread error: {e}")
    finally:
        active_runtimes.pop((str(uid), str(slot)), None)

class RunnerManager:
    def is_running(self, uid, slot):
        return (str(uid), str(slot)) in active_runtimes

    def get_uptime(self, uid, slot):
        key = (str(uid), str(slot))
        if key in active_runtimes:
            e = int(time.time() - active_runtimes[key]["start_time"])
            h, r = divmod(e, 3600); m, s = divmod(r, 60)
            return f"{h}h {m}m {s}s"
        return "N/A"

    def running_count(self):
        return len(active_runtimes)

    def start_userbot(self, uid, slot, api_id, api_hash, session_string, uid_str):
        key = (str(uid), str(slot))
        if key in active_runtimes:
            return True
        try:
            t = threading.Thread(
                target=_run_telethon_client, 
                args=(uid, slot, api_id, api_hash, session_string), 
                daemon=True
            )
            t.start()
            time.sleep(1)
            return True
        except Exception as e:
            logger.error(f"Failed to start thread: {e}")
            return False

    def stop_userbot(self, uid, slot):
        key = (str(uid), str(slot))
        if key in active_runtimes:
            try:
                loop = active_runtimes[key]["loop"]
                client = active_runtimes[key]["client"]
                asyncio.run_coroutine_threadsafe(client.disconnect(), loop)
            except Exception:
                pass
        return True

    def restart_userbot(self, uid, slot, api_id, api_hash, session_string, uid_str):
        self.stop_userbot(uid, slot)
        time.sleep(1)
        return self.start_userbot(uid, slot, api_id, api_hash, session_string, uid_str)

    def stop_all_for_user(self, uid):
        slots_to_stop = [s for (u, s) in active_runtimes.keys() if u == str(uid)]
        for slot in slots_to_stop:
            self.stop_userbot(uid, slot)

runner = RunnerManager()

# ════════════════════════════════════════════════════════════════════════════════
#   FONT STYLES
# ════════════════════════════════════════════════════════════════════════════════

def bold_serif(t: str) -> str:
    result = ""
    for c in t:
        if 'A' <= c <= 'Z': result += chr(ord(c) - ord('A') + 0x1D400)
        elif 'a' <= c <= 'z': result += chr(ord(c) - ord('a') + 0x1D41A)
        elif '0' <= c <= '9': result += chr(ord(c) - ord('0') + 0x1D7CE)
        else: result += c
    return result

def italic_serif(t: str) -> str:
    special = {'h': '𝒽', 'e': '𝑒', 'i': '𝑖', 'j': '𝑗'}
    result = ""
    for c in t:
        if c in special: result += special[c]
        elif 'A' <= c <= 'Z': result += chr(ord(c) - ord('A') + 0x1D434)
        elif 'a' <= c <= 'z': result += chr(ord(c) - ord('a') + 0x1D44E)
        else: result += c
    return result

def script(t: str) -> str:
    result = ""
    for c in t:
        if 'A' <= c <= 'Z': result += chr(ord(c) - ord('A') + 0x1D4D0)
        elif 'a' <= c <= 'z': result += chr(ord(c) - ord('a') + 0x1D4EA)
        else: result += c
    return result

def double_struck(t: str) -> str:
    special_map = {'C': 'ℂ', 'H': 'ℍ', 'N': 'ℕ', 'P': 'ℙ', 'Q': 'ℚ', 'R': 'ℝ', 'Z': 'ℤ'}
    result = ""
    for c in t:
        if c in special_map: result += special_map[c]
        elif 'A' <= c <= 'Z': result += chr(ord(c) - ord('A') + 0x1D538)
        elif 'a' <= c <= 'z': result += chr(ord(c) - ord('a') + 0x1D552)
        elif '0' <= c <= '9': result += chr(ord(c) - ord('0') + 0x1D7D8)
        else: result += c
    return result

def sans_bold(t: str) -> str:
    result = ""
    for c in t:
        if 'A' <= c <= 'Z': result += chr(ord(c) - ord('A') + 0x1D5D4)
        elif 'a' <= c <= 'z': result += chr(ord(c) - ord('a') + 0x1D5EE)
        elif '0' <= c <= '9': result += chr(ord(c) - ord('0') + 0x1D7EC)
        else: result += c
    return result

def mono(t: str) -> str:
    result = ""
    for c in t:
        if 'A' <= c <= 'Z': result += chr(ord(c) - ord('A') + 0x1D670)
        elif 'a' <= c <= 'z': result += chr(ord(c) - ord('a') + 0x1D68A)
        elif '0' <= c <= '9': result += chr(ord(c) - ord('0') + 0x1D7F6)
        else: result += c
    return result

def fraktur(t: str) -> str:
    special = {'C': 'ℭ', 'H': 'ℌ', 'I': 'ℑ', 'R': 'ℜ', 'Z': 'ℨ'}
    result = ""
    for c in t:
        if c in special: result += special[c]
        elif 'A' <= c <= 'Z': result += chr(ord(c) - ord('A') + 0x1D504)
        elif 'a' <= c <= 'z': result += chr(ord(c) - ord('a') + 0x1D51E)
        else: result += c
    return result

def bold_italic_serif(t: str) -> str:
    result = ""
    for c in t:
        if 'A' <= c <= 'Z': result += chr(ord(c) - ord('A') + 0x1D468)
        elif 'a' <= c <= 'z': result += chr(ord(c) - ord('a') + 0x1D482)
        else: result += c
    return result

DIV  = "━━━━━━━━━━━━━━━━━━━━━━━━━━"
DIV2 = "·͜·͜·͜·͜·͜·͜·͜·͜·͜·͜·͜·͜·͜·͜·͜·͜·͜·"
DIV3 = "⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯"
TOP  = "╔══════════════════════════╗"
BOT  = "╚══════════════════════════╝"
MID  = "╠══════════════════════════╣"

# ════════════════════════════════════════════════════════════════════════════════
#   HELPERS
# ════════════════════════════════════════════════════════════════════════════════

def is_owner(uid): return uid == OWNER_ID
def is_premium(uid): return is_owner(uid) or db.is_sudo(uid, OWNER_ID)

def uptime_str():
    e = int(time.time() - START_TIME)
    h, r = divmod(e, 3600); m, s = divmod(r, 60)
    return f"{h}h {m}m {s}s"

def _phone_label(acct: dict) -> str:
    phone = acct.get("phone", "")
    return phone if phone else f"Account #{acct.get('slot', 0) + 1}"

async def owner_only(update: Update) -> bool:
    if not is_owner(update.effective_user.id):
        await update.message.reply_text(
            f"{TOP}\n║  🔒  {bold_serif('Access Denied')}  🔒  ║\n{BOT}\n\n"
            f"{script('This command is restricted to')}\n👑 {sans_bold('Owners Only')}",
            parse_mode=ParseMode.MARKDOWN,
        )
        return False
    return True

async def premium_only(update: Update) -> bool:
    if not is_premium(update.effective_user.id):
        await update.message.reply_text(
            f"🌟 {bold_serif('Premium Required')}\n\n"
            f"{script('This feature is for')}\n"
            f"👑 {sans_bold('Owners')} & {sans_bold('Premium Users')} {script('only')}\n\n"
            f"📩 {mono('Contact:')} {SUPPORT_USERNAME}",
            parse_mode=ParseMode.MARKDOWN,
        )
        return False
    return True

async def check_blocked(update: Update) -> bool:
    if db.is_blocked(update.effective_user.id):
        await update.message.reply_text(
            f"🚫 {bold_serif('You have been Blocked')}\n\n"
            f"{script('Contact support to appeal.')}",
            parse_mode=ParseMode.MARKDOWN,
        )
        return False
    return True

async def cleanup_pending(uid: int):
    data = pending_logins.pop(uid, None)
    if data and data.get("client"):
        try: await data["client"].disconnect()
        except: pass


# ════════════════════════════════════════════════════════════════════════════════
#   /start
# ════════════════════════════════════════════════════════════════════════════════

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_blocked(update): return
    uid  = update.effective_user.id
    name = update.effective_user.first_name or "User"

    if not db.user_exists(uid):
        db.save_user_meta(uid, {"first_name": name, "joined_at": int(time.time())})

    accounts = db.get_accounts(uid)
    hosted   = [a for a in accounts if a.get("hosted")]
    running  = [a for a in hosted if runner.is_running(uid, a["slot"])]

    if hosted:
        status_line = (
            f"\n📱 {fraktur('Accounts')} : {mono(str(len(hosted)))} hosted  "
            f"| {mono(str(len(running)))} running"
        )
    else:
        status_line = f"\n⚪ {fraktur('Userbot')}: {italic_serif('Not hosted yet')}"

    welcome_video = db.get_welcome_video()
    if welcome_video and welcome_video.get("file_id"):
        try:
            if welcome_video.get("is_video_note"):
                await context.bot.send_video_note(
                    chat_id=update.effective_chat.id,
                    video_note=welcome_video["file_id"],
                )
            else:
                await context.bot.send_video(
                    chat_id=update.effective_chat.id,
                    video=welcome_video["file_id"],
                )
        except Exception as e:
            logger.warning(f"Failed to send welcome video: {e}")

    keyboard = [
        [
            InlineKeyboardButton("🚀  𝗛𝗼𝘀𝘁 𝗠𝘆 𝗨𝘀𝗲𝗿𝗯𝗼𝘁", callback_data="host"),
        ],
        [
            InlineKeyboardButton("📋  𝗠𝗮𝘀𝘁𝗲𝗿 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀", callback_data="commands"),
            InlineKeyboardButton("🌊  𝗙𝗹𝗼𝘄 𝗠𝗲𝗻𝘂",       callback_data="flow_menu"),
        ],
        [
            InlineKeyboardButton("📊  𝗦𝘁𝗮𝘁𝘂𝘀",   callback_data="status"),
            InlineKeyboardButton("🗑️  𝗟𝗼𝗴𝗼𝘂𝘁",   callback_data="menu_logout"),
        ],
        [
            InlineKeyboardButton("📞  𝗦𝘂𝗽𝗽𝗼𝗿𝘁",          callback_data="support"),
            InlineKeyboardButton("❓  𝗛𝗲𝗹𝗽 & 𝗚𝘂𝗶𝗱𝗲", callback_data="help"),
        ],
    ]
    if is_owner(uid):
        keyboard.append([
            InlineKeyboardButton("📢  𝗕𝗿𝗼𝗮𝗱𝗰𝗮𝘀𝘁", callback_data="broadcast_menu"),
            InlineKeyboardButton("⚙️  𝗦𝗲𝘁𝘁𝗶𝗻𝗴𝘀",   callback_data="settings_menu"),
        ])

    text = (
        f"👑 **BEBO PREMIUM USERBOT ARCHITECTURE** 👑\n"
        f"{DIV}\n"
        f"✨ Welcome back, {bold_serif(name)}!\n\n"
        f"» **Engine:** `v6.0-BEBO-DYNAMIC`\n"
        f"» **Status:** `ONLINE & SECURE`\n\n"
        f"🪪 {fraktur('Your ID')} : `{uid}`\n"
        f"{status_line}\n\n"
        f"{italic_serif('Select an option below')} 👇"
    )

    await update.message.reply_text(
        text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

# ════════════════════════════════════════════════════════════════════════════════
#   /setwelcomevideo (Owner)
# ════════════════════════════════════════════════════════════════════════════════

async def cmd_setwelcomevideo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await owner_only(update): return
    reply = update.message.reply_to_message
    if not reply:
        await update.message.reply_text(
            f"📽️ {bold_serif('Set Welcome Video')}\n\n"
            f"{script('Reply to a video or video note with')}\n"
            f"{mono('/setwelcomevideo')}",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    file_id = None
    is_video_note = False

    if reply.video:
        file_id = reply.video.file_id
    elif reply.video_note:
        file_id = reply.video_note.file_id
        is_video_note = True
    else:
        await update.message.reply_text(
            f"❌ {bold_serif('Reply must be a video or video note.')}",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    db.set_welcome_video({"file_id": file_id, "is_video_note": is_video_note})
    await update.message.reply_text(
        f"✅ {bold_serif('Welcome video set successfully!')}\n\n"
        f"📹 {script('New users will see this video on /start')}",
        parse_mode=ParseMode.MARKDOWN,
    )

# ════════════════════════════════════════════════════════════════════════════════
#   /removewelcomevideo (Owner)
# ════════════════════════════════════════════════════════════════════════════════

async def cmd_removewelcomevideo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await owner_only(update): return
    if db.get_welcome_video() is None:
        await update.message.reply_text(
            f"⚠️ {italic_serif('No welcome video is currently set.')}",
            parse_mode=ParseMode.MARKDOWN,
        )
        return
    db.remove_welcome_video()
    await update.message.reply_text(
        f"🗑️ {bold_serif('Welcome video removed.')}\n\n"
        f"{script('The /start message will now show only text.')}",
        parse_mode=ParseMode.MARKDOWN,
    )

# ════════════════════════════════════════════════════════════════════════════════
#   /help
# ════════════════════════════════════════════════════════════════════════════════

async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_blocked(update): return
    text = (
        f"❓ {double_struck('Help')} & {double_struck('Commands')}\n"
        f"{DIV}\n\n"
        f"{'━'*3} {sans_bold('User Commands')} {'━'*3}\n\n"
        f"🔹 {mono('/start')}       {script('Grand Welcome Screen')}\n"
        f"🔹 {mono('/help')}        {script('This Help Menu')}\n"
        f"🔹 {mono('/commands')}    {script('Master Features Menu')}\n"
        f"🔹 {mono('/flowmenu')}    {script('Flow Bot Features Menu')}\n"
        f"🔹 {mono('/host')}        {script('Add & Deploy Account')}\n"
        f"🔹 {mono('/myaccounts')}  {script('Manage All Accounts')}\n"
        f"🔹 {mono('/status')}      {script('Check All Userbots')}\n"
        f"🔹 {mono('/restart')}     {script('Restart Userbot')}\n"
        f"🔹 {mono('/logout')}      {script('Logout an Account')}\n"
        f"🔹 {mono('/support')}     {script('Contact Admin')}\n\n"
        f"{DIV}\n"
        f"{'━'*3} 👑 {sans_bold('Owner Commands')} {'━'*3}\n\n"
        f"🔺 {mono('/restartall')}    {fraktur('Restart All Userbots')}\n"
        f"🔺 {mono('/refresh')}       {fraktur('Refresh Bot State')}\n"
        f"🔺 {mono('/sudolist')}      {fraktur('Manage Sudo Users')}\n"
        f"🔺 {mono('/setdp')}         {fraktur('Set Display Photo')}\n"
        f"🔺 {mono('/block')}         {fraktur('Block a User')}\n"
        f"🔺 {mono('/unblock')}       {fraktur('Unblock a User')}\n"
        f"🔺 {mono('/blockeduser')}   {fraktur('View Blocked List')}\n"
        f"🔺 {mono('/stats')}         {fraktur('Bot Statistics')}\n"
        f"🔺 {mono('/secretfunction')} {fraktur('Secret Commands')}\n"
        f"🔺 {mono('/setwelcomevideo')} {fraktur('Set Welcome Video')}\n"
        f"🔺 {mono('/removewelcomevideo')} {fraktur('Remove Welcome Video')}\n"
        f"🔺 {mono('/setbot')}        {fraktur('ON/OFF Bot')}\n"
        f"{DIV}"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

# ════════════════════════════════════════════════════════════════════════════════
#   MENUS
# ════════════════════════════════════════════════════════════════════════════════

async def cmd_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_blocked(update): return
    # Animated implementation handled in bot callback, static here
    menu = """
╔═══════════════════════════════════════════╗
║         💖  𝐁𝐄𝐁𝐎 𝐔𝐋𝐓𝐈𝐌𝐀𝐓𝐄 𝐌𝐄𝐍𝐔  💖        ║
╚═══════════════════════════════════════════╝
    (Reply on Userbot side using `.menu` for full interface)
    """
    await update.message.reply_text(menu, parse_mode=ParseMode.MARKDOWN)

async def cmd_flowmenu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_blocked(update): return
    menu = """
╔═══════════════════════════════════════════╗
║          🌊  𝐁𝐄𝐁𝐎 𝐅𝐋𝐎𝐖 𝐁𝐎𝐓 𝐌𝐄𝐍𝐔  🌊       ║
╚═══════════════════════════════════════════╝
    (Reply on Userbot side using `.flowmenu` for full interface)
    """
    await update.message.reply_text(menu, parse_mode=ParseMode.MARKDOWN)

# ════════════════════════════════════════════════════════════════════════════════
#   /host — Phone + OTP Login Flow
# ════════════════════════════════════════════════════════════════════════════════

async def cmd_host_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        await update.callback_query.answer()
        reply = update.callback_query.message.reply_text
    else:
        reply = update.message.reply_text

    if not await check_blocked(update): return ConversationHandler.END
    uid = update.effective_user.id

    accounts = db.get_accounts(uid)
    hosted   = [a for a in accounts if a.get("hosted")]
    if len(hosted) >= MAX_ACCOUNTS_PER_USER:
        await reply(
            f"📱 {bold_serif('Account Limit Reached')}\n\n"
            f"{script('You already have')} {mono(str(len(hosted)))} {script('accounts hosted.')}\n"
            f"📌 {italic_serif('Maximum:')} {mono(str(MAX_ACCOUNTS_PER_USER))} {italic_serif('per user')}\n\n"
            f"🗑️ {script('Logout an account first:')} /logout",
            parse_mode=ParseMode.MARKDOWN,
        )
        return ConversationHandler.END

    total = db.hosted_count()
    if total >= MAX_USERBOTS and not is_premium(uid):
        await reply(
            f"😔 {sans_bold('Slots Full')} ({total}/{MAX_USERBOTS})\n\n"
            f"{script('Contact')} {SUPPORT_USERNAME} {script('to get a slot.')}",
            parse_mode=ParseMode.MARKDOWN,
        )
        return ConversationHandler.END

    await cleanup_pending(uid)

    extra = f"\n\n📱 {italic_serif('Account')} {mono(str(len(hosted)+1))} {italic_serif('of')} {mono(str(MAX_ACCOUNTS_PER_USER))}" if hosted else ""

    await reply(
        f"{TOP}\n"
        f"║  🚀  {bold_serif('Deploy Your Userbot')}  🚀  ║\n"
        f"{BOT}\n\n"
        f"📱 {sans_bold('Step 1 of 3')}\n"
        f"{DIV3}\n"
        f"{script('Enter your Telegram Phone Number')}\n\n"
        f"🌍 {fraktur('Format')}: {mono('+91XXXXXXXXXX')}\n"
        f"_(country code ke saath)_{extra}\n\n"
        f"🔴 {italic_serif('Send /cancel to abort')}",
        parse_mode=ParseMode.MARKDOWN,
    )
    return ASK_PHONE

async def host_got_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid   = update.effective_user.id
    phone = update.message.text.strip()
    digits = phone.replace("+", "").replace(" ", "").replace("-", "")
    if not digits.isdigit() or len(digits) < 7:
        await update.message.reply_text(
            f"❌ {bold_serif('Invalid Number')}\n\n"
            f"{script('Please enter in format')}: {mono('+91XXXXXXXXXX')}",
            parse_mode=ParseMode.MARKDOWN,
        )
        return ASK_PHONE

    msg = await update.message.reply_text(
        f"⏳ {sans_bold('Sending OTP to Telegram')}... 📨"
    )
    try:
        client = TelegramClient(StringSession(), TELEGRAM_API_ID, TELEGRAM_API_HASH)
        await client.connect()
        result = await client.send_code_request(phone)
        pending_logins[uid] = {
            "client": client,
            "phone":  phone,
            "phone_code_hash": result.phone_code_hash,
        }
        await msg.edit_text(
            f"{TOP}\n"
            f"║  📨  {bold_serif('OTP Sent Successfully')}  📨  ║\n"
            f"{BOT}\n\n"
            f"📱 {fraktur('Number')}: {mono(phone)}\n\n"
            f"📩 {sans_bold('Step 2 of 3')}\n"
            f"{DIV3}\n"
            f"{script('Enter the Login Code from your Telegram app')}\n\n"
            f"💡 {italic_serif('Tip: Send with spaces to avoid auto-forward')}\n"
            f"    {mono('Example')}: {bold_serif('1 2 3 4 5')}",
            parse_mode=ParseMode.MARKDOWN,
        )
        return ASK_CODE
    except FloodWaitError as e:
        await cleanup_pending(uid)
        await msg.edit_text(
            f"⏳ {sans_bold('Flood Wait!')} {mono(str(e.seconds) + 's')} baad try karo."
        )
        return ConversationHandler.END
    except Exception as e:
        await cleanup_pending(uid)
        await msg.edit_text(
            f"❌ {bold_serif('Error')}\n{mono(str(e)[:120])}\n\n{script('Try again:')} /host",
            parse_mode=ParseMode.MARKDOWN,
        )
        return ConversationHandler.END

async def host_got_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid  = update.effective_user.id
    code = update.message.text.strip().replace(" ", "")

    pending = pending_logins.get(uid)
    if not pending:
        await update.message.reply_text(
            f"❌ {sans_bold('Session expired. Try /host again.')}"
        )
        return ConversationHandler.END

    client: TelegramClient = pending["client"]
    phone: str = pending["phone"]
    hash_: str = pending["phone_code_hash"]

    msg = await update.message.reply_text(f"🔐 {sans_bold('Verifying OTP')}...")
    try:
        await client.sign_in(phone, code, phone_code_hash=hash_)
        session_string = client.session.save()
        await client.disconnect()
        pending_logins.pop(uid, None)
        await _deploy_userbot(update, context, uid, session_string, phone, msg)
        return ConversationHandler.END

    except SessionPasswordNeededError:
        await msg.edit_text(
            f"{TOP}\n║  🔒  {bold_serif('2FA Detected')}  🔒  ║\n{BOT}\n\n"
            f"🛡️ {sans_bold('Step 3 of 3')}\n{DIV3}\n"
            f"{script('Your account has Two-Step Verification')}\n\n"
            f"🔑 {fraktur('Enter your 2FA Password')}:",
            parse_mode=ParseMode.MARKDOWN,
        )
        return ASK_2FA

    except PhoneCodeInvalidError:
        await msg.edit_text(
            f"❌ {bold_serif('Wrong Code!')} Dobara enter karo:\n\n"
            f"💡 {mono('Spaces ke saath')}: {bold_serif('1 2 3 4 5')}",
            parse_mode=ParseMode.MARKDOWN,
        )
        return ASK_CODE

    except PhoneCodeExpiredError:
        await cleanup_pending(uid)
        await msg.edit_text(
            f"⏳ {sans_bold('Code Expired!')} Dobara /host karo.",
            parse_mode=ParseMode.MARKDOWN,
        )
        return ConversationHandler.END

    except Exception as e:
        await cleanup_pending(uid)
        await msg.edit_text(
            f"❌ {bold_serif('Error')}\n{mono(str(e)[:120])}\n\nDobara /host karo.",
            parse_mode=ParseMode.MARKDOWN,
        )
        return ConversationHandler.END

async def host_got_2fa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid      = update.effective_user.id
    password = update.message.text.strip()
    pending  = pending_logins.get(uid)
    if not pending:
        await update.message.reply_text("❌ Session expire ho gayi. /host karo.")
        return ConversationHandler.END

    client: TelegramClient = pending["client"]
    phone: str = pending.get("phone", "")
    msg = await update.message.reply_text(f"🔐 {sans_bold('Verifying 2FA Password')}...")
    try:
        await client.sign_in(password=password)
        session_string = client.session.save()
        await client.disconnect()
        pending_logins.pop(uid, None)
        await _deploy_userbot(update, context, uid, session_string, phone, msg)
        return ConversationHandler.END
    except Exception as e:
        await cleanup_pending(uid)
        await msg.edit_text(
            f"❌ {bold_serif('Wrong 2FA Password')}\n"
            f"{mono(str(e)[:120])}\n\nDobara /host karo.",
            parse_mode=ParseMode.MARKDOWN,
        )
        return ConversationHandler.END

async def _deploy_userbot(update, context, uid, session_string, phone, msg):
    name     = update.effective_user.first_name or "User"
    accounts = db.get_accounts(uid)
    existing = {a.get("slot") for a in accounts}
    slot = 0
    while slot in existing:
        slot += 1
    acc_num = slot + 1

    # ─── Terminal Animation ───
    frames = [
        "🟢 `[▱▱▱▱▱▱▱▱▱] Booting BEBO Dynamic Kernel...`",
        "🟡 `[▰▰▰▱▱▱▱▱▱] Injecting Modules...`",
        "🟠 `[▰▰▰▰▰▰▱▱▱] Bypassing Security...`",
        "🔴 `[▰▰▰▰▰▰▰▰▱] Establishing Uplink...`",
        f"✅ `[▰▰▰▰▰▰▰▰▰] Link Established for Slot #{acc_num}!`"
    ]
    for frame in frames:
        try:
            await msg.edit_text(frame, parse_mode=ParseMode.MARKDOWN)
            await asyncio.sleep(0.5)
        except Exception:
            pass

    ok = runner.start_userbot(
        uid, slot, str(TELEGRAM_API_ID), TELEGRAM_API_HASH, session_string, str(uid),
    )
    
    if ok:
        db.save_user_meta(uid, {"first_name": name})
        db.add_account(uid, {
            "slot":           slot,
            "session_string": session_string,
            "hosted":         True,
            "hosted_at":      int(time.time()),
            "phone":          phone,
        })
        
        deploy_caption = (
            f"{TOP}\n"
            f"║  🎉  {bold_serif('Deploy Successful')}  🎉  ║\n"
            f"{BOT}\n\n"
            f"✅ {sans_bold('Account')} : {mono('#' + str(acc_num))}\n"
            f"📱 {sans_bold('Phone')}   : {mono(phone if phone else 'N/A')}\n"
            f"⚡ {sans_bold('Version')} : {mono('v6.0-BEBO-DYNAMIC')}\n"
            f"📦 {sans_bold('Commands')}: {mono('500+')}\n\n"
            f"{DIV}\n"
            f"🔹 {italic_serif('Kisi bhi chat mein')} {mono('.alive')} {italic_serif('bhejo')}\n"
            f"🔹 {italic_serif('Commands dekhne ke liye')} {mono('.menu')} {italic_serif('bhejo')}\n"
            f"🔹 /myaccounts {italic_serif('se sab accounts dekho')}\n"
            f"🔹 /host {italic_serif('se aur account add karo')}"
        )
        
        try:
            await msg.edit_text(
                deploy_caption,
                parse_mode=ParseMode.MARKDOWN,
            )
        except Exception:
            await update.effective_chat.send_message(
                deploy_caption,
                parse_mode=ParseMode.MARKDOWN,
            )
    else:
        try:
            await msg.edit_text(
                f"❌ {bold_serif('Deploy Failed')}\n\n"
                f"{script('Possible reasons:')}\n"
                f"• {fraktur('Account banned by Telegram')}\n"
                f"• {fraktur('Server error')}\n\n"
                f"📩 {sans_bold('Support')}: {SUPPORT_USERNAME}",
                parse_mode=ParseMode.MARKDOWN,
            )
        except Exception:
            await update.effective_chat.send_message(
                "❌ Deploy Failed. Please try /host again.",
                parse_mode=ParseMode.MARKDOWN,
            )

async def host_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await cleanup_pending(update.effective_user.id)
    await update.message.reply_text(
        f"🚫 {bold_serif('Login Cancelled')}\n\n"
        f"{script('Use /host to try again anytime.')}"
    )
    return ConversationHandler.END

# ════════════════════════════════════════════════════════════════════════════════
#   /broadcast (Owner)
# ════════════════════════════════════════════════════════════════════════════════

async def cmd_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await owner_only(update): return

    reply = update.message.reply_to_message
    text_arg = " ".join(context.args).strip()

    if not reply and not text_arg:
        await update.message.reply_text(
            f"{TOP}\n"
            f"║  📢  {bold_serif('Broadcast Center')}  📢  ║\n"
            f"{BOT}\n\n"
            f"📝 {script('Reply to any message with')} {mono('/broadcast')}\n"
            f"or {script('use')} {mono('/broadcast your message here')}\n\n"
            f"✨ {italic_serif('Media, photos, videos and files are supported when replying.')}",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    users = []
    for uid_str in db.get_all_users():
        try:
            target_uid = int(uid_str)
        except Exception:
            continue
        if target_uid == OWNER_ID or db.is_blocked(target_uid):
            continue
        users.append(target_uid)

    total = len(users)
    if total == 0:
        await update.message.reply_text(
            f"⚠️ {bold_serif('No eligible users found.')}",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    progress = await update.message.reply_text(
        f"📢 {bold_serif('Broadcast Starting')}...\n"
        f"⏳ {script('Preparing')} • {mono(f'0/{total}')}",
        parse_mode=ParseMode.MARKDOWN,
    )

    sent = 0
    failed = 0
    for index, target_uid in enumerate(users, 1):
        try:
            if reply:
                await context.bot.copy_message(
                    chat_id=target_uid,
                    from_chat_id=update.effective_chat.id,
                    message_id=reply.message_id,
                )
            else:
                await context.bot.send_message(
                    chat_id=target_uid,
                    text=text_arg,
                )
            sent += 1
        except Exception as e:
            failed += 1
            logger.warning(f"Broadcast failed for {target_uid}: {str(e)[:100]}")

        if index == 1 or index % 10 == 0 or index == total:
            frames = ["📢", "📣", "🚀", "✨", "📡"]
            frame = frames[(index // 10) % len(frames)]
            try:
                await progress.edit_text(
                    f"{frame} {bold_serif('Broadcasting')}...\n"
                    f"⏳ {script('Progress')} • {mono(f'{index}/{total}')}\n"
                    f"✅ {mono(str(sent))}  ❌ {mono(str(failed))}",
                    parse_mode=ParseMode.MARKDOWN,
                )
            except Exception:
                pass

    await progress.edit_text(
        f"{TOP}\n"
        f"║  ✅  {bold_serif('Broadcast Complete')}  ✅  ║\n"
        f"{BOT}\n\n"
        f"📨 {sans_bold('Sent')}    : {mono(str(sent))}\n"
        f"❌ {sans_bold('Failed')}  : {mono(str(failed))}\n"
        f"👥 {sans_bold('Total')}   : {mono(str(total))}\n\n"
        f"{DIV}\n"
        f"✨ {italic_serif('Broadcast finished successfully.')}",
        parse_mode=ParseMode.MARKDOWN,
    )

# ════════════════════════════════════════════════════════════════════════════════
#   /myaccounts
# ════════════════════════════════════════════════════════════════════════════════

async def cmd_myaccounts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_blocked(update): return
    uid      = update.effective_user.id
    accounts = db.get_accounts(uid)
    hosted   = [a for a in accounts if a.get("hosted")]

    if not hosted:
        keyboard = [[InlineKeyboardButton("🚀 Host My First Userbot", callback_data="host")]]
        await update.message.reply_text(
            f"📱 {bold_serif('No Accounts Hosted Yet')}\n\n"
            f"{script('Get started with /host')}\n"
            f"{italic_serif('Host up to')} {mono(str(MAX_ACCOUNTS_PER_USER))} {italic_serif('accounts!')}",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return

    lines = []
    keyboard = []
    for acct in hosted:
        slot   = acct.get("slot", 0)
        alive  = runner.is_running(uid, slot)
        uptime = runner.get_uptime(uid, slot) if alive else None
        icon   = "🟢" if alive else "🔴"
        phone  = _phone_label(acct)
        up_str = f"  ⏱️ {uptime}" if uptime else ""
        lines.append(
            f"{icon} {bold_serif('Acc #' + str(slot+1))} — {mono(phone)}{up_str}"
        )
        row = []
        if alive:
            row.append(InlineKeyboardButton(f"🔄 Restart #{slot+1}", callback_data=f"restart_acc_{slot}"))
        else:
            row.append(InlineKeyboardButton(f"▶️ Start #{slot+1}",   callback_data=f"start_acc_{slot}"))
        row.append(InlineKeyboardButton(f"🗑️ Logout #{slot+1}", callback_data=f"logout_acc_{slot}"))
        keyboard.append(row)

    if len(hosted) < MAX_ACCOUNTS_PER_USER:
        keyboard.append([InlineKeyboardButton("➕ Add Another Account", callback_data="add_acc")])

    header = (
        f"{TOP}\n"
        f"║  📱  {double_struck('My Accounts')} ({len(hosted)}/{MAX_ACCOUNTS_PER_USER})  📱  ║\n"
        f"{BOT}\n\n"
    )
    body = "\n".join(lines)
    footer = f"\n\n{DIV}\n🔹 /host {italic_serif('— add account')}"

    await update.message.reply_text(
        header + body + footer,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

# ════════════════════════════════════════════════════════════════════════════════
#   /status
# ════════════════════════════════════════════════════════════════════════════════

async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_blocked(update): return
    uid      = update.effective_user.id
    accounts = db.get_accounts(uid)
    hosted   = [a for a in accounts if a.get("hosted")]

    if not hosted:
        await update.message.reply_text(
            f"❌ {bold_serif('No Userbot Found')}\n\n"
            f"{script('Deploy one using')} /host",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    import datetime
    lines = []
    for acct in hosted:
        slot     = acct.get("slot", 0)
        alive    = runner.is_running(uid, slot)
        uptime   = runner.get_uptime(uid, slot) if alive else "—"
        hosted_at = acct.get("hosted_at", 0)
        since = datetime.datetime.fromtimestamp(hosted_at).strftime("%d %b %Y  %H:%M") if hosted_at else "—"
        icon = "🟢" if alive else "🔴"
        phone = _phone_label(acct)
        lines.append(
            f"{icon} {sans_bold('Account #' + str(slot+1))} — {mono(phone)}\n"
            f"   ⏱️ {italic_serif('Uptime')} : {mono(uptime)}\n"
            f"   📅 {italic_serif('Hosted')} : {mono(since)}"
        )

    footer = ""
    if any(not runner.is_running(uid, a["slot"]) for a in hosted):
        footer = f"\n\n🔄 {italic_serif('Use /restart to revive stopped accounts.')}"

    await update.message.reply_text(
        f"{TOP}\n║  📊  {double_struck('Userbot Status')}  📊  ║\n{BOT}\n\n"
        + "\n\n".join(lines) +
        f"\n\n{DIV}"
        f"\n⚡ {sans_bold('Version')} : {mono('v6.0-BEBO-DYNAMIC')}"
        f"{footer}",
        parse_mode=ParseMode.MARKDOWN,
    )

# ════════════════════════════════════════════════════════════════════════════════
#   /restart
# ════════════════════════════════════════════════════════════════════════════════

async def cmd_restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_blocked(update): return
    uid      = update.effective_user.id
    accounts = db.get_accounts(uid)
    hosted   = [a for a in accounts if a.get("hosted")]

    if not hosted:
        await update.message.reply_text(
            f"❌ {bold_serif('No Userbot Found.')} {script('Use /host first.')}",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    if len(hosted) == 1:
        acct = hosted[0]
        slot = acct["slot"]
        await _do_restart(update, uid, slot, acct)
        return

    keyboard = []
    for acct in hosted:
        slot  = acct["slot"]
        phone = _phone_label(acct)
        alive = runner.is_running(uid, slot)
        icon  = "🟢" if alive else "🔴"
        keyboard.append([
            InlineKeyboardButton(
                f"{icon} Restart #{slot+1} — {phone}",
                callback_data=f"restart_acc_{slot}",
            )
        ])
    keyboard.append([InlineKeyboardButton("❌ Cancel", callback_data="cancel_action")])

    await update.message.reply_text(
        f"🔄 {bold_serif('Which account to restart?')}\n\n"
        f"{script('Select below')} 👇",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

async def _do_restart(update_or_query, uid, slot, acct):
    is_cb = hasattr(update_or_query, "callback_query") and update_or_query.callback_query
    if is_cb:
        msg_obj = update_or_query.callback_query.message
        send = msg_obj.reply_text
    else:
        send = update_or_query.message.reply_text

    msg = await send(f"🔄 {sans_bold('Restarting Account')} #{slot+1}...")
    ok = runner.restart_userbot(
        uid, slot, str(TELEGRAM_API_ID), TELEGRAM_API_HASH,
        acct.get("session_string", ""), str(uid),
    )
    if ok:
        await msg.edit_text(
            f"✅ {double_struck('Account #' + str(slot+1) + ' Restarted')}!\n\n"
            f"🟢 {sans_bold('Status')}: {script('Running')}\n"
            f"⚡ {italic_serif('Test with')} {mono('.alive')}",
            parse_mode=ParseMode.MARKDOWN,
        )
    else:
        await msg.edit_text(
            f"❌ {bold_serif('Restart Failed')}\n\n"
            f"📩 {script('Contact')} {SUPPORT_USERNAME}",
            parse_mode=ParseMode.MARKDOWN,
        )

# ════════════════════════════════════════════════════════════════════════════════
#   /logout
# ════════════════════════════════════════════════════════════════════════════════

async def cmd_logout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_blocked(update): return
    uid      = update.effective_user.id
    accounts = db.get_accounts(uid)
    hosted   = [a for a in accounts if a.get("hosted")]

    if not hosted:
        await update.message.reply_text(
            f"❌ {italic_serif('Koi active userbot nahi hai.')}"
        )
        return

    if len(hosted) == 1:
        acct = hosted[0]
        slot = acct["slot"]
        phone = _phone_label(acct)
        keyboard = [[
            InlineKeyboardButton("✅ Haan, Logout Karo", callback_data=f"confirm_logout_{slot}"),
            InlineKeyboardButton("❌ Cancel",            callback_data="cancel_action"),
        ]]
        await update.message.reply_text(
            f"⚠️ {bold_serif('Logout Confirmation')}\n\n"
            f"📱 {sans_bold('Account')} : {mono(phone)}\n\n"
            f"{script('Logout karne se session delete ho jayega.')}\n"
            f"{italic_serif('Dobara host karne ke liye /host karo.')}",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return

    keyboard = []
    for acct in hosted:
        slot  = acct["slot"]
        phone = _phone_label(acct)
        alive = runner.is_running(uid, slot)
        icon  = "🟢" if alive else "🔴"
        keyboard.append([
            InlineKeyboardButton(
                f"{icon} Logout #{slot+1} — {phone}",
                callback_data=f"logout_acc_{slot}",
            )
        ])
    keyboard.append([InlineKeyboardButton("❌ Cancel", callback_data="cancel_action")])

    await update.message.reply_text(
        f"🗑️ {bold_serif('Kaunsa Account Logout Karna Hai?')}\n\n"
        f"{script('Select below')} 👇",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

async def _do_logout(uid, slot):
    runner.stop_userbot(uid, slot)
    db.remove_account(uid, slot)
    session_dir = f"data/sessions/{uid}/{slot}"
    shutil.rmtree(session_dir, ignore_errors=True)

# ════════════════════════════════════════════════════════════════════════════════
#   /support & Admin Controls
# ════════════════════════════════════════════════════════════════════════════════

async def cmd_support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_blocked(update): return
    await update.message.reply_text(
        f"{TOP}\n║  📞  {double_struck('Support Center')}  📞  ║\n{BOT}\n\n"
        f"👤 {sans_bold('Admin')}    : {SUPPORT_USERNAME}\n"
        f"⚡ {sans_bold('Response')} : {script('Fast')}\n\n"
        f"{DIV}\n"
        f"🔧 {bold_serif('Try these first:')}\n\n"
        f"🔹 /myaccounts — {italic_serif('Sab accounts dekho')}\n"
        f"🔹 /restart    — {italic_serif('Userbot restart karo')}\n"
        f"🔹 /status     — {italic_serif('Status check karo')}\n"
        f"🔹 /logout → /host — {italic_serif('Re-deploy karo')}",
        parse_mode=ParseMode.MARKDOWN,
    )

async def cmd_supportraid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_blocked(update): return
    if not await premium_only(update): return
    args   = context.args
    target = " ".join(args) if args else None
    if not target:
        await update.message.reply_text(
            f"⚔️ {bold_serif('Pro Support Raid')}\n\n"
            f"📌 {sans_bold('Usage')}: {mono('/supportraid @username')}",
            parse_mode=ParseMode.MARKDOWN,
        )
        return
    await update.message.reply_text(
        f"{TOP}\n║  ⚔️  {bold_serif('Support Raid Launched')}  ⚔️  ║\n{BOT}\n\n"
        f"🎯 {sans_bold('Target')} : {mono(target)}\n"
        f"🌪️ {script('All premium userbots activated!')}\n"
        f"⚡ {fraktur('Raid Mode')}: {double_struck('MAX POWER')}",
        parse_mode=ParseMode.MARKDOWN,
    )

async def cmd_restartall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await owner_only(update): return
    msg   = await update.message.reply_text(f"🔄 {sans_bold('Restarting All Userbots')}...")
    count = 0
    for uid_str in db.get_all_users():
        uid = int(uid_str)
        if db.is_blocked(uid): continue
        for acct in db.get_accounts(uid):
            if not acct.get("hosted") or not acct.get("session_string"): continue
            slot = acct["slot"]
            ok = runner.restart_userbot(
                uid, slot, str(TELEGRAM_API_ID), TELEGRAM_API_HASH,
                acct["session_string"], uid_str,
            )
            if ok: count += 1
    await msg.edit_text(
        f"✅ {double_struck('Restart Complete')}\n\n"
        f"🟢 {sans_bold('Restarted')}: {mono(str(count))} {script('userbots')}",
        parse_mode=ParseMode.MARKDOWN,
    )

async def cmd_refresh(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await owner_only(update): return
    await update.message.reply_text(
        f"🔁 {bold_serif('Bot State Refreshed')}\n\n"
        f"🟢 {sans_bold('Running')} : {mono(str(runner.running_count()))}\n"
        f"📦 {sans_bold('Total')}   : {mono(str(db.hosted_count()))}\n"
        f"🕒 {sans_bold('Uptime')}  : {mono(uptime_str())}",
        parse_mode=ParseMode.MARKDOWN,
    )

async def cmd_sudolist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await owner_only(update): return
    args  = context.args
    sudos = db.get_sudo_users()

    if args and args[0] == "add" and len(args) > 1:
        try:
            db.add_sudo(int(args[1]))
            await update.message.reply_text(
                f"✅ {mono(args[1])} {script('added to Sudo Users.')}",
                parse_mode=ParseMode.MARKDOWN,
            )
        except: await update.message.reply_text("❌ Invalid ID.")
        return

    if args and args[0] == "del" and len(args) > 1:
        try:
            db.remove_sudo(int(args[1]))
            await update.message.reply_text(
                f"✅ {mono(args[1])} {script('removed from Sudo Users.')}",
                parse_mode=ParseMode.MARKDOWN,
            )
        except: await update.message.reply_text("❌ Invalid ID.")
        return

    if not sudos:
        await update.message.reply_text(
            f"📋 {bold_serif('No Sudo Users yet.')}\n\nAdd: {mono('/sudolist add <uid>')}",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    lines = "\n".join(f"  👑 {mono(str(u))}" for u in sudos)
    await update.message.reply_text(
        f"{TOP}\n║  👑  {double_struck('Sudo Users')} ({len(sudos)})  👑  ║\n{BOT}\n\n"
        f"{lines}\n\n{DIV}\n"
        f"➕ {mono('/sudolist add <uid>')}\n"
        f"➖ {mono('/sudolist del <uid>')}",
        parse_mode=ParseMode.MARKDOWN,
    )

async def cmd_setdp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await owner_only(update): return
    if not update.message.reply_to_message or not update.message.reply_to_message.photo:
        await update.message.reply_text(f"📸 {script('Kisi photo ko reply karo.')}")
        return
    photo = update.message.reply_to_message.photo[-1]
    file  = await context.bot.get_file(photo.file_id)
    data  = await file.download_as_bytearray()
    from io import BytesIO
    try:
        await context.bot.set_my_profile_photo(BytesIO(bytes(data)))
        await update.message.reply_text(f"✅ {bold_serif('Display Photo Updated')}!")
    except Exception as e:
        await update.message.reply_text(
            f"❌ {sans_bold('Failed')}: {mono(str(e)[:80])}",
            parse_mode=ParseMode.MARKDOWN,
        )

async def cmd_block(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await owner_only(update): return
    if not context.args:
        await update.message.reply_text(
            f"📌 {sans_bold('Usage')}: {mono('/block <user_id>')}",
            parse_mode=ParseMode.MARKDOWN,
        )
        return
    try:
        target = int(context.args[0])
        if target == OWNER_ID:
            await update.message.reply_text(f"❌ {italic_serif('Owner ko block nahi kar sakte.')}")
            return
        db.block_user(target)
        runner.stop_all_for_user(target)
        await update.message.reply_text(
            f"🚫 {bold_serif('User Blocked')}\n\n"
            f"🆔 {mono(str(target))}\n"
            f"🔴 {script('All userbots stopped.')}",
            parse_mode=ParseMode.MARKDOWN,
        )
    except ValueError:
        await update.message.reply_text("❌ Invalid ID.")

async def cmd_unblock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await owner_only(update): return
    if not context.args:
        await update.message.reply_text(
            f"📌 {sans_bold('Usage')}: {mono('/unblock <user_id>')}",
            parse_mode=ParseMode.MARKDOWN,
        )
        return
    try:
        db.unblock_user(int(context.args[0]))
        await update.message.reply_text(
            f"✅ {bold_serif('User Unblocked')}\n🆔 {mono(context.args[0])}",
            parse_mode=ParseMode.MARKDOWN,
        )
    except ValueError:
        await update.message.reply_text("❌ Invalid ID.")

async def cmd_blockeduser(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await owner_only(update): return
    blocked = db.get_blocked()
    if not blocked:
        await update.message.reply_text(f"✅ {script('No blocked users.')}")
        return
    lines = "\n".join(f"  🚫 {mono(str(u))}" for u in blocked)
    await update.message.reply_text(
        f"{TOP}\n║  🚫  {double_struck('Blocked Users')} ({len(blocked)})  🚫  ║\n{BOT}\n\n"
        f"{lines}",
        parse_mode=ParseMode.MARKDOWN,
    )

async def cmd_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await owner_only(update): return
    total   = db.user_count()
    hosted  = db.hosted_count()
    running = runner.running_count()
    blocked = len(db.get_blocked())
    sudos   = len(db.get_sudo_users())

    await update.message.reply_text(
        f"{TOP}\n║  📊  {double_struck('Bot Statistics')}  📊  ║\n{BOT}\n\n"
        f"👥 {sans_bold('Total Users')}    : {double_struck(str(total))}\n"
        f"🚀 {sans_bold('Hosted Accounts')}: {double_struck(str(hosted))}\n"
        f"🟢 {sans_bold('Running')}        : {double_struck(str(running))}\n"
        f"🔴 {sans_bold('Stopped')}        : {double_struck(str(hosted - running))}\n"
        f"🚫 {sans_bold('Blocked')}        : {double_struck(str(blocked))}\n"
        f"👑 {sans_bold('Sudo Users')}     : {double_struck(str(sudos))}\n"
        f"📦 {sans_bold('Max Slots')}      : {double_struck(str(MAX_USERBOTS))}\n"
        f"{DIV}\n"
        f"🕒 {sans_bold('Bot Uptime')} : {mono(uptime_str())}",
        parse_mode=ParseMode.MARKDOWN,
    )

async def cmd_secretfunction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await owner_only(update): return
    await update.message.reply_text(
        f"{TOP}\n║  🔐  {bold_serif('Secret Commands')}  🔐  ║\n{BOT}\n\n"
        f"🔺 {mono('/sudolist add <uid>')}  — {fraktur('Add Premium User')}\n"
        f"🔺 {mono('/sudolist del <uid>')}  — {fraktur('Remove Premium User')}\n"
        f"🔺 {mono('/block <uid>')}         — {fraktur('Ban & Kill All Userbots')}\n"
        f"🔺 {mono('/unblock <uid>')}       — {fraktur('Unban User')}\n"
        f"🔺 {mono('/restartall')}          — {fraktur('Restart All Userbots')}\n"
        f"🔺 {mono('/refresh')}             — {fraktur('Refresh Bot State')}\n"
        f"🔺 {mono('/stats')}               — {fraktur('Full Statistics')}\n"
        f"🔺 {mono('/setdp')}               — {fraktur('Set Display Photo')}\n"
        f"🔺 {mono('/blockeduser')}         — {fraktur('View Blocked List')}\n"
        f"🔺 {mono('/secretfunction')}      — {fraktur('This Menu')}\n"
        f"🔺 {mono('/setwelcomevideo')}     — {fraktur('Set Welcome Video')}\n"
        f"🔺 {mono('/removewelcomevideo')}  — {fraktur('Remove Welcome Video')}\n"
        f"🔺 {mono('/setbot')}              — {fraktur('ON/OFF Bot')}",
        parse_mode=ParseMode.MARKDOWN,
    )

async def cmd_setbot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await owner_only(update): return
    args = context.args
    if not args or args[0].lower() not in ["on", "off"]:
        current = "ON" if db.is_bot_on() else "OFF"
        await update.message.reply_text(
            f"⚙️ {bold_serif('Bot Status')}\n\n"
            f"📊 {sans_bold('Current')} : {mono(current)}\n\n"
            f"📌 {sans_bold('Usage')}: {mono('/setbot on/off')}",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    new_state = args[0].lower() == "on"
    db.set_bot_settings({"is_on": new_state})
    status = "ON 🟢" if new_state else "OFF 🔴"
    await update.message.reply_text(
        f"✅ {bold_serif('Bot Status Updated')}\n\n"
        f"📊 {sans_bold('Status')} : {mono(status)}",
        parse_mode=ParseMode.MARKDOWN,
    )

# ════════════════════════════════════════════════════════════════════════════════
#   CALLBACK QUERY HANDLER
# ════════════════════════════════════════════════════════════════════════════════

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not db.is_bot_on():
        await update.callback_query.answer("⚠️ Bot is currently OFF", show_alert=True)
        return

    query = update.callback_query
    await query.answer()
    uid  = update.effective_user.id
    data = query.data

    if data == "cancel_action":
        await query.message.edit_text(f"🚫 {italic_serif('Cancelled.')}")
        return

    if data == "broadcast_menu":
        if not is_owner(uid):
            await query.answer("🔒 Owner only", show_alert=True)
            return
        await query.message.reply_text(
            f"{TOP}\n"
            f"║  📢  {bold_serif('Broadcast Center')}  📢  ║\n"
            f"{BOT}\n\n"
            f"📝 {script('Reply to any message with')} {mono('/broadcast')}\n"
            f"or use {mono('/broadcast your message')}\n\n"
            f"✨ {italic_serif('Button animation + live progress is enabled.')}",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    if data == "settings_menu":
        if not is_owner(uid):
            await query.answer("🔒 Owner only", show_alert=True)
            return
        current_status = "ON 🟢" if db.is_bot_on() else "OFF 🔴"
        keyboard = [
            [InlineKeyboardButton(f"🟢 Bot is {current_status}", callback_data="toggle_bot")],
            [InlineKeyboardButton("🔙 Back", callback_data="back_to_start")],
        ]
        await query.message.reply_text(
            f"{TOP}\n"
            f"║  ⚙️  {bold_serif('Bot Settings')}  ⚙️  ║\n"
            f"{BOT}\n\n"
            f"📊 {sans_bold('Bot Status')} : {mono(current_status)}\n"
            f"🆔 {sans_bold('Owner ID')}  : `{OWNER_ID}`\n"
            f"🔑 {sans_bold('API ID')}    : `{TELEGRAM_API_ID}`\n"
            f"🔐 {sans_bold('API Hash')}  : `{TELEGRAM_API_HASH[:8]}...`\n\n"
            f"{DIV}\n"
            f"💡 {italic_serif('Toggle bot status below')}",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return

    if data == "toggle_bot":
        if not is_owner(uid):
            await query.answer("🔒 Owner only", show_alert=True)
            return
        current = db.is_bot_on()
        db.set_bot_settings({"is_on": not current})
        new_status = "ON 🟢" if not current else "OFF 🔴"
        await query.message.edit_text(
            f"✅ {bold_serif('Bot Status Updated')}\n\n"
            f"📊 {sans_bold('Status')} : {mono(new_status)}",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    if data == "back_to_start":
        await cmd_start(update, context)
        return

    if data == "commands":
        msg = await query.message.reply_text("🔄 **INITIALIZING MASTER MENU...**")
        await asyncio.sleep(0.2)
        await msg.edit("⚙️ **LOADING MODULES...**")
        await asyncio.sleep(0.2)
        menu = """
╔═══════════════════════════════════════════╗
║         💖  𝐁𝐄𝐁𝐎 𝐔𝐋𝐓𝐈𝐌𝐀𝐓𝐄 𝐌𝐄𝐍𝐔  💖        ║
╚═══════════════════════════════════════════╝
    (Reply on Userbot side using `.menu` for full interface)
    """
        await msg.edit(menu, parse_mode=ParseMode.MARKDOWN)
        return

    if data == "flow_menu":
        msg = await query.message.reply_text("🌊 **INITIALIZING FLOW ENGINE...**")
        await asyncio.sleep(0.3)
        menu = """
╔═══════════════════════════════════════════╗
║          🌊  𝐁𝐄𝐁𝐎 𝐅𝐋𝐎𝐖 𝐁𝐎𝐓 𝐌𝐄𝐍𝐔  🌊       ║
╚═══════════════════════════════════════════╝
    (Reply on Userbot side using `.flowmenu` for full interface)
    """
        await msg.edit(menu, parse_mode=ParseMode.MARKDOWN)
        return

    if data == "status":
        accounts = db.get_accounts(uid)
        hosted   = [a for a in accounts if a.get("hosted")]
        if not hosted:
            await query.message.reply_text(
                f"❌ {bold_serif('No Userbot Hosted')}\n\n"
                f"{script('Use /host to deploy your first account.')}",
                parse_mode=ParseMode.MARKDOWN,
            )
            return
        import datetime
        lines = []
        for acct in hosted:
            slot     = acct.get("slot", 0)
            alive    = runner.is_running(uid, slot)
            uptime   = runner.get_uptime(uid, slot) if alive else "—"
            hosted_at = acct.get("hosted_at", 0)
            since = datetime.datetime.fromtimestamp(hosted_at).strftime("%d %b %Y") if hosted_at else "—"
            icon  = "🟢" if alive else "🔴"
            phone = _phone_label(acct)
            lines.append(
                f"{icon} {sans_bold('Acc #' + str(slot+1))} — {mono(phone)}\n"
                f"   ⏱️ {uptime}  📅 {since}"
            )
        footer = ""
        if any(not runner.is_running(uid, a["slot"]) for a in hosted):
            footer = f"\n\n🔄 {italic_serif('/restart se revive karo.')}"
        await query.message.reply_text(
            f"{TOP}\n║  📊  {double_struck('Userbot Status')}  📊  ║\n{BOT}\n\n"
            + "\n\n".join(lines) +
            f"\n\n{DIV}"
            f"\n⚡ {sans_bold('Version')} : {mono('v6.0-BEBO-DYNAMIC')}"
            f"{footer}",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    if data == "menu_logout":
        accounts = db.get_accounts(uid)
        hosted   = [a for a in accounts if a.get("hosted")]
        if not hosted:
            await query.message.reply_text(
                f"❌ {italic_serif('Koi active userbot nahi hai.')}"
            )
            return
        if len(hosted) == 1:
            acct  = hosted[0]
            slot  = acct["slot"]
            phone = _phone_label(acct)
            kb = [[
                InlineKeyboardButton("✅ Haan, Logout Karo", callback_data=f"confirm_logout_{slot}"),
                InlineKeyboardButton("❌ Cancel",            callback_data="cancel_action"),
            ]]
            await query.message.reply_text(
                f"⚠️ {bold_serif('Logout Confirmation')}\n\n"
                f"📱 {sans_bold('Account')} : {mono(phone)}\n\n"
                f"{script('Session delete ho jayega.')}\n"
                f"{italic_serif('Dobara /host se add kar sakte ho.')}",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(kb),
            )
        else:
            kb = []
            for acct in hosted:
                slot  = acct["slot"]
                phone = _phone_label(acct)
                alive = runner.is_running(uid, slot)
                icon  = "🟢" if alive else "🔴"
                kb.append([InlineKeyboardButton(
                    f"{icon} Logout #{slot+1} — {phone}",
                    callback_data=f"logout_acc_{slot}",
                )])
            kb.append([InlineKeyboardButton("❌ Cancel", callback_data="cancel_action")])
            await query.message.reply_text(
                f"🗑️ {bold_serif('Kaunsa Account Logout Karna Hai?')}\n\n"
                f"{script('Select below')} 👇",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(kb),
            )
        return

    if data == "support":
        await query.message.reply_text(
            f"{TOP}\n║  📞  {double_struck('Support Center')}  📞  ║\n{BOT}\n\n"
            f"👤 {sans_bold('Bot Owner')}  : {SUPPORT_USERNAME}\n"
            f"⚡ {sans_bold('Response')}   : {script('Fast')}\n\n"
            f"{DIV}\n"
            f"🔧 {bold_serif('Pehle Yeh Try Karo:')}\n\n"
            f"🔹 /myaccounts — {italic_serif('sab accounts dekho')}\n"
            f"🔹 /restart    — {italic_serif('userbot restart karo')}\n"
            f"🔹 /status     — {italic_serif('status check karo')}\n"
            f"🔹 /logout     — {italic_serif('aur dobara /host karo')}\n\n"
            f"{DIV}\n"
            f"🤖 {bold_serif('Bot Owner')}: {SUPPORT_USERNAME}",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    if data == "help":
        await query.message.reply_text(
            f"╔══════════════════════════════╗\n"
            f"║  📖  {bold_serif('BOT USAGE GUIDE')}  📖  ║\n"
            f"╚══════════════════════════════╝\n\n"
            f"{'━'*30}\n"
            f"🚀 {sans_bold('STEP 1')} — {bold_serif('Bot Start Karo')}\n"
            f"{'━'*30}\n"
            f"➡️ {script('Is bot pe')} /start {script('bhejo')}\n"
            f"✅ {italic_serif('Welcome screen aayega')}\n\n"
            f"{'━'*30}\n"
            f"📱 {sans_bold('STEP 2')} — {bold_serif('Account Host Karo')}\n"
            f"{'━'*30}\n"
            f"➡️ {mono('Host My Userbot')} {script('button tap karo')}\n"
            f"➡️ {script('Apna phone number enter karo')}\n"
            f"    {mono('Format: +91XXXXXXXXXX')}\n"
            f"➡️ {script('Telegram se OTP aayega')}\n"
            f"    💡 {italic_serif('OTP spaces ke saath bhejo:')}\n"
            f"    {mono('1 2 3 4 5')} ← {italic_serif('aisa karo')}\n"
            f"➡️ {script('2FA hai toh password bhi daalo')}\n"
            f"✅ {italic_serif('Userbot deploy ho jayega!')}\n\n"
            f"{'━'*30}\n"
            f"⚡ {sans_bold('STEP 3')} — {bold_serif('Commands Chalao')}\n"
            f"{'━'*30}\n"
            f"➡️ {script('Kisi bhi chat mein jao')}\n"
            f"➡️ {script('Dot')} {mono('.')} {script('se command likho:')}\n\n"
            f"    {mono('.alive')}  → {script('Bot alive check karo')}\n"
            f"    {mono('.ping')}   → {script('Speed check')}\n"
            f"    {mono('.menu')}   → {script('Commands list')}\n"
            f"    {mono('.attack')} → {script('Attack karo')}\n"
            f"    {mono('.roast')}  → {script('Roast karo')}\n"
            f"    {mono('.swipe')}  → {script('Swipe flood shuru')}\n\n"
            f"{'━'*30}\n"
            f"🔄 {sans_bold('STEP 4')} — {bold_serif('Manage Karo')}\n"
            f"{'━'*30}\n"
            f"    /myaccounts — {script('Sab accounts')}\n"
            f"    /status     — {script('Status dekho')}\n"
            f"    /restart    — {script('Restart karo')}\n"
            f"    /logout     — {script('Logout karo')}\n"
            f"    /host       — {script('Naya account add karo')}\n\n"
            f"{'━'*30}\n"
            f"⚠️ {sans_bold('IMPORTANT')}\n"
            f"{'━'*30}\n"
            f"🔸 {italic_serif('Sirf tumhara OWN account command chalayega')}\n"
            f"🔸 {italic_serif('Kisi dusre ka message ignore hoga')}\n"
            f"🔸 {italic_serif('Max')} {mono('3')} {italic_serif('accounts ek saath host ho sakte hain')}\n\n"
            f"{'━'*30}\n"
            f"🌟 {bold_serif('Bot Owner')}: {SUPPORT_USERNAME}\n"
            f"⚡ {bold_serif('Powered by BEBO ENGINE')}",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    if data.startswith("restart_acc_"):
        try:
            slot = int(data.split("_")[-1])
        except ValueError:
            return
        acct = db.get_account(uid, slot)
        if not acct:
            await query.message.reply_text(f"❌ {italic_serif('Account not found.')}")
            return
        msg = await query.message.reply_text(
            f"🔄 {sans_bold('Restarting Account')} #{slot+1}..."
        )
        ok = runner.restart_userbot(
            uid, slot, str(TELEGRAM_API_ID), TELEGRAM_API_HASH,
            acct.get("session_string", ""), str(uid),
        )
        if ok:
            await msg.edit_text(
                f"✅ {double_struck('Account #' + str(slot+1) + ' Restarted')}!\n\n"
                f"🟢 {sans_bold('Status')}: {script('Running')}\n"
                f"⚡ {italic_serif('Test with')} {mono('.alive')}",
                parse_mode=ParseMode.MARKDOWN,
            )
        else:
            await msg.edit_text(f"❌ {bold_serif('Restart Failed')}\n📩 {SUPPORT_USERNAME}")
        return

    if data.startswith("start_acc_"):
        try:
            slot = int(data.split("_")[-1])
        except ValueError:
            return
        acct = db.get_account(uid, slot)
        if not acct:
            await query.message.reply_text(f"❌ {italic_serif('Account not found.')}")
            return
        msg = await query.message.reply_text(
            f"▶️ {sans_bold('Starting Account')} #{slot+1}..."
        )
        ok = runner.start_userbot(
            uid, slot, str(TELEGRAM_API_ID), TELEGRAM_API_HASH,
            acct.get("session_string", ""), str(uid),
        )
        if ok:
            await msg.edit_text(
                f"✅ {double_struck('Account #' + str(slot+1) + ' Started')}!\n\n"
                f"🟢 {sans_bold('Status')}: {script('Running')}\n"
                f"⚡ {italic_serif('Test with')} {mono('.alive')}",
                parse_mode=ParseMode.MARKDOWN,
            )
        else:
            await msg.edit_text(f"❌ {bold_serif('Start Failed')}\n📩 {SUPPORT_USERNAME}")
        return

    if data.startswith("logout_acc_"):
        try:
            slot = int(data.split("_")[-1])
        except ValueError:
            return
        acct  = db.get_account(uid, slot)
        if not acct:
            await query.message.reply_text(f"❌ {italic_serif('Account not found.')}")
            return
        phone = _phone_label(acct)
        keyboard = [[
            InlineKeyboardButton("✅ Haan, Logout Karo", callback_data=f"confirm_logout_{slot}"),
            InlineKeyboardButton("❌ Cancel",            callback_data="cancel_action"),
        ]]
        await query.message.reply_text(
            f"⚠️ {bold_serif('Logout Confirmation')}\n\n"
            f"📱 {sans_bold('Account')} #{slot+1} : {mono(phone)}\n\n"
            f"{script('Session delete ho jayega.')}\n"
            f"{italic_serif('Dobara /host se add kar sakte ho.')}",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return

    if data.startswith("confirm_logout_"):
        try:
            slot = int(data.split("_")[-1])
        except ValueError:
            return
        acct  = db.get_account(uid, slot)
        phone = _phone_label(acct) if acct else f"#{slot+1}"
        await _do_logout(uid, slot)
        await query.message.edit_text(
            f"{TOP}\n║  👋  {bold_serif('Logged Out')}  👋  ║\n{BOT}\n\n"
            f"📱 {sans_bold('Account')} : {mono(phone)}\n"
            f"🗑️ {sans_bold('Session')} : {script('Cleared')}\n\n"
            f"🚀 {fraktur('Re-deploy anytime:')} /host\n"
            f"📱 {fraktur('See accounts:')} /myaccounts",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    if data == "add_acc":
        accounts = db.get_accounts(uid)
        hosted   = [a for a in accounts if a.get("hosted")]
        if len(hosted) >= MAX_ACCOUNTS_PER_USER:
            await query.message.reply_text(
                f"📱 {bold_serif('Account Limit Reached')}\n\n"
                f"{script('Maximum')} {mono(str(MAX_ACCOUNTS_PER_USER))} {script('accounts.')}\n"
                f"🗑️ {script('Logout one first:')} /logout",
                parse_mode=ParseMode.MARKDOWN,
            )
            return
        await query.message.reply_text(
            f"🚀 {bold_serif('Add New Account')}\n\n"
            f"{script('Send')} /host {script('to start the login flow.')}",
            parse_mode=ParseMode.MARKDOWN,
        )
        return


# ════════════════════════════════════════════════════════════════════════════════
#   AUTO HEALTH CHECK
# ════════════════════════════════════════════════════════════════════════════════

async def auto_health_check(context: ContextTypes.DEFAULT_TYPE):
    if not db.is_bot_on():
        return
    for uid_str in db.get_all_users():
        uid = int(uid_str)
        if db.is_blocked(uid): continue
        for acct in db.get_accounts(uid):
            if not acct.get("hosted") or not acct.get("session_string"): continue
            slot = acct["slot"]
            if not runner.is_running(uid, slot):
                runner.start_userbot(
                    uid, slot, str(TELEGRAM_API_ID), TELEGRAM_API_HASH,
                    acct["session_string"], uid_str,
                )


# ════════════════════════════════════════════════════════════════════════════════
#   STARTUP & MAIN
# ════════════════════════════════════════════════════════════════════════════════

async def post_init(application: Application):
    await application.bot.set_my_commands([
        BotCommand("start",           "Grand Welcome"),
        BotCommand("help",            "All Commands"),
        BotCommand("commands",        "Master Features Menu"),
        BotCommand("flowmenu",        "Flow Bot Features Menu"),
        BotCommand("host",            "Add & Deploy Account"),
        BotCommand("myaccounts",      "Manage All Accounts"),
        BotCommand("status",          "Check Userbot Status"),
        BotCommand("restart",         "Restart Userbot"),
        BotCommand("logout",          "Logout an Account"),
        BotCommand("support",         "Get Support"),
        BotCommand("supportraid",     "Pro Raid (Premium)"),
        BotCommand("restartall",      "Restart All (Owner)"),
        BotCommand("refresh",         "Refresh State (Owner)"),
        BotCommand("sudolist",        "Sudo Users (Owner)"),
        BotCommand("setdp",           "Set Display Photo (Owner)"),
        BotCommand("block",           "Block User (Owner)"),
        BotCommand("unblock",         "Unblock User (Owner)"),
        BotCommand("blockeduser",     "Blocked List (Owner)"),
        BotCommand("stats",           "Bot Statistics (Owner)"),
        BotCommand("secretfunction",  "Secret Commands (Owner)"),
        BotCommand("setwelcomevideo", "Set Welcome Video (Owner)"),
        BotCommand("removewelcomevideo", "Remove Welcome Video (Owner)"),
        BotCommand("broadcast",         "Broadcast Message (Owner)"),
        BotCommand("setbot",          "ON/OFF Bot (Owner)"),
    ])
    if db.is_bot_on():
        count = 0
        for uid_str in db.get_all_users():
            uid = int(uid_str)
            if db.is_blocked(uid): continue
            for acct in db.get_accounts(uid):
                if not acct.get("hosted") or not acct.get("session_string"): continue
                ok = runner.start_userbot(
                    uid, acct["slot"], str(TELEGRAM_API_ID), TELEGRAM_API_HASH,
                    acct["session_string"], uid_str,
                )
                if ok: count += 1
        logger.info(f"[STARTUP] Auto-started {count} userbots.")
    else:
        logger.info("[STARTUP] Bot is OFF — skipping auto-start.")


def main():
    if not BOT_TOKEN:  raise ValueError("BOT_TOKEN not set!")
    if not OWNER_ID:   raise ValueError("OWNER_ID not set!")

    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()

    host_conv = ConversationHandler(
        entry_points=[
            CommandHandler("host", cmd_host_start),
            CallbackQueryHandler(cmd_host_start, pattern="^host$"),
        ],
        states={
            ASK_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, host_got_phone)],
            ASK_CODE:  [MessageHandler(filters.TEXT & ~filters.COMMAND, host_got_code)],
            ASK_2FA:   [MessageHandler(filters.TEXT & ~filters.COMMAND, host_got_2fa)],
        },
        fallbacks=[CommandHandler("cancel", host_cancel)],
        allow_reentry=True,
    )

    app.add_handler(CommandHandler("start",           cmd_start))
    app.add_handler(CommandHandler("help",            cmd_help))
    app.add_handler(CommandHandler("commands",        cmd_commands))
    app.add_handler(CommandHandler("flowmenu",        cmd_flowmenu))
    app.add_handler(host_conv)
    app.add_handler(CommandHandler("myaccounts",      cmd_myaccounts))
    app.add_handler(CommandHandler("status",          cmd_status))
    app.add_handler(CommandHandler("restart",         cmd_restart))
    app.add_handler(CommandHandler("logout",          cmd_logout))
    app.add_handler(CommandHandler("support",         cmd_support))
    app.add_handler(CommandHandler("supportraid",     cmd_supportraid))
    app.add_handler(CommandHandler("restartall",      cmd_restartall))
    app.add_handler(CommandHandler("refresh",         cmd_refresh))
    app.add_handler(CommandHandler("sudolist",        cmd_sudolist))
    app.add_handler(CommandHandler("setdp",           cmd_setdp))
    app.add_handler(CommandHandler("block",           cmd_block))
    app.add_handler(CommandHandler("unblock",         cmd_unblock))
    app.add_handler(CommandHandler("blockeduser",     cmd_blockeduser))
    app.add_handler(CommandHandler("stats",           cmd_stats))
    app.add_handler(CommandHandler("secretfunction",  cmd_secretfunction))
    app.add_handler(CommandHandler("setwelcomevideo", cmd_setwelcomevideo))
    app.add_handler(CommandHandler("removewelcomevideo", cmd_removewelcomevideo))
    app.add_handler(CommandHandler("broadcast",         cmd_broadcast))
    app.add_handler(CommandHandler("setbot",            cmd_setbot))
    app.add_handler(CallbackQueryHandler(callback_handler))

    if app.job_queue:
        app.job_queue.run_repeating(auto_health_check, interval=300, first=60)

    logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    logger.info("🤖  BEBO Premium Hoster Bot STARTED!")
    logger.info(f"👑  Owner ID: {OWNER_ID}")
    logger.info(f"📊  Bot Status: {'ON' if db.is_bot_on() else 'OFF'}")
    logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
