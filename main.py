import sys
import os
import re
import time
import json
import ctypes
import random
import threading
import subprocess
import webbrowser
import base64
import io
import asyncio
import tempfile
import difflib
from datetime import datetime
from PyQt5.QtWidgets import (QApplication,QWidget,QLabel,QPushButton,QVBoxLayout,QHBoxLayout,QFrame,QGraphicsDropShadowEffect,QMenu,QSystemTrayIcon,QLineEdit,QSizePolicy,QScrollArea,QTextEdit,QAction,QTextBrowser,QSlider,QDialog,QFileDialog)
from PyQt5.QtCore import (Qt,QTimer,QPropertyAnimation,QEasingCurve,QThread,pyqtSignal,QPoint,QRect,QUrl,QSize)
from PyQt5.QtWebEngineWidgets import QWebEngineView,QWebEnginePage,QWebEngineSettings
from PyQt5.QtGui import QColor,QCursor,QFont,QIcon,QPixmap,QPainter
from PyQt5.QtMultimedia import QMediaPlayer,QMediaContent
from google import genai
try:
    import keyboard
    HAS_KEYBOARD=True
except ImportError:
    HAS_KEYBOARD=False
try:
    import pyautogui
    from PIL import Image
    HAS_SCREENSHOT=True
except ImportError:
    HAS_SCREENSHOT=False
try:
    import speech_recognition as sr
    HAS_SPEECH=True
except ImportError:
    HAS_SPEECH=False
try:
    import edge_tts
    HAS_EDGE_TTS=True
except ImportError:
    HAS_EDGE_TTS=False
try:
    import pyttsx3
    HAS_TTS=True
except ImportError:
    HAS_TTS=False
sys.argv.append("--disable-gpu-shader-disk-cache")
sys.argv.append("--disable-gpu-cache")
BASE_DIR=os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE=os.path.join(BASE_DIR,"config.json")
SAVE_FILE=os.path.join(BASE_DIR,"savegame.json")
CHAT_HISTORY_FILE=os.path.join(BASE_DIR,"chat_history.json")
SETTINGS_FILE=os.path.join(BASE_DIR,"companion_settings.json")
EMOTION_FILE=os.path.join(BASE_DIR,"miyuki_emotion.json")
COMMAND_FILE=os.path.join(BASE_DIR,"miyuki_command_bridge.json")
LEARNED_COMMANDS_FILE=os.path.join(BASE_DIR,"learned_commands.json")
gemini_client=None
tts_engine=None
tts_lock=threading.Lock()
media_player=None
PALETTE={
    "bg_primary":"#0A0A0F",
    "bg_secondary":"#111118",
    "bg_card":"#16161E",
    "bg_input":"#1C1C26",
    "border":"#2A2A3A",
    "border_subtle":"#1E1E2A",
    "accent":"#7C6DFA",
    "accent_soft":"#9D91FB",
    "accent_dim":"rgba(124,109,250,0.12)",
    "accent_border":"rgba(124,109,250,0.25)",
    "text_primary":"#F0EEF8",
    "text_secondary":"#9896A8",
    "text_muted":"#5A5868",
    "success":"#4ADE80",
    "warning":"#F59E0B",
    "danger":"#F87171",
    "info":"#60A5FA",
}
FONT_SIZES={
    "title":36,
    "subtitle":20,
    "heading":24,
    "body":22,
    "body_small":20,
    "input":20,
    "button":20,
    "label":18,
    "caption":16,
    "menu":18,
    "tooltip":15,
    "badge":16,
    "code":18,
    "status":20,
    "sender":18,
    "chat_base":24,
}
VOICE_PROFILES={
    "gentle":  {"name":"en-US-AvaNeural","rate":"+1%", "pitch":"+0Hz"},
    "excited": {"name":"en-US-AvaNeural","rate":"+1%","pitch":"+0Hz"},
    "caring":  {"name":"en-US-AvaNeural","rate":"+1%", "pitch":"+0Hz"},
    "playful": {"name":"en-US-AvaNeural","rate":"+1%","pitch":"+0Hz"},
    "comfort": {"name":"en-US-AvaNeural","rate":"+1%", "pitch":"+0Hz"},
    "proud":   {"name":"en-US-AvaNeural","rate":"+1%", "pitch":"+0Hz"},
    "worried": {"name":"en-US-AvaNeural","rate":"+1%","pitch":"+0Hz"},
    "default": {"name":"en-US-AvaNeural","rate":"+1%", "pitch":"+0Hz"},
}
EMOTION_VOICE_MAP={"happy":"excited","excited":"excited","proud":"proud","tired":"comfort","worried":"worried","watching":"default","loving":"gentle","caring":"caring","playful":"playful","curious":"default","jealous":"worried","neutral":"default","shocked":"excited","touched":"gentle","headpat":"gentle","poke":"playful","smug":"proud","sleepy":"comfort","determined":"proud","grateful":"gentle","shy":"gentle","comfort":"comfort","confused":"worried","nostalgic":"gentle","angry":"worried","lonely":"comfort","relieved":"gentle"}
EMOTION_STATUS_COLORS={"happy":"#4ADE80","excited":"#60A5FA","proud":"#7C6DFA","tired":"#6B7280","worried":"#F59E0B","watching":"#94A3B8","loving":"#F472B6","caring":"#34D399","playful":"#A78BFA","curious":"#38BDF8","jealous":"#FB923C","neutral":"#94A3B8","shocked":"#F87171","touched":"#4ADE80","headpat":"#4ADE80","poke":"#FB923C","smug":"#7C6DFA","sleepy":"#6B7280","determined":"#60A5FA","grateful":"#4ADE80","shy":"#F472B6","comfort":"#34D399","confused":"#38BDF8","nostalgic":"#A78BFA","angry":"#F87171","lonely":"#94A3B8","relieved":"#7C6DFA"}
EMOTION_DISPLAY_NAMES={"happy":"Happy","excited":"Excited","proud":"Proud","tired":"Tired","worried":"Worried","watching":"Watching","loving":"Loving","caring":"Caring","playful":"Playful","curious":"Curious","jealous":"Jealous","neutral":"Neutral","shocked":"Shocked","touched":"Touched","headpat":"Headpat","poke":"Poke","smug":"Smug","sleepy":"Sleepy","determined":"Determined","grateful":"Grateful","shy":"Shy","comfort":"Comfort","confused":"Confused","nostalgic":"Nostalgic","angry":"Angry","lonely":"Lonely","relieved":"Relieved"}
SPEAK_IMPORTANT_ONLY=True
IMPORTANT_APP_TYPES={"gaming","coding","learning"}
SILENT_APP_TYPES={"browsing","social","music","shopping","entertainment","work","ai"}
SILENT_STATUS_UPDATES=True
def should_speak_status(app_type,text):
    if app_type in SILENT_APP_TYPES:
        return False
    if app_type in IMPORTANT_APP_TYPES:
        return False
    return True
def should_speak_quote(text):
    keywords=["break","hour","hours","minutes","stretch","hydrate","water","sleep","rest","late","3 am","midnight","posture","eyes","take a break","health","well done","proud","amazing","achieved","back","welcome","warning","careful","posture","missed"]
    tl=text.lower()
    return any(k in tl for k in keywords)
def generate_smart_voice_text(full_text,player_name):
    has_code=bool(re.search(r'```[\s\S]*?```',full_text))
    clean_text=re.sub(r'```[\s\S]*?```','',full_text).strip()
    clean_text=re.sub(r'\[CMD:[^\]]+\]','',clean_text).strip()
    clean_text=re.sub(r'https?://\S+','',clean_text).strip()
    clean_text=re.sub(r'\s+',' ',clean_text).strip()
    clean_text=re.sub(r'[^\w\s.,!?\'"()-]','',clean_text).strip()
    word_count=len(clean_text.split())
    if has_code:
        sentences=re.split(r'[.!?]+',clean_text)
        first_part=' '.join(sentences[:2]).strip() if sentences else clean_text[:100]
        if len(first_part)<20:
            first_part="Done!"
        return f"{first_part} Check the chat for the full code, {player_name}!"
    if word_count<=60:
        return clean_text
    sentences=re.split(r'[.!?]+',clean_text)
    sentences=[s.strip() for s in sentences if s.strip()]
    summary_sentences=[]
    char_count=0
    for s in sentences:
        if char_count+len(s)<350 and len(summary_sentences)<3:
            summary_sentences.append(s)
            char_count+=len(s)
        if char_count>=300 or len(summary_sentences)>=3:
            break
    if summary_sentences:
        result='. '.join(summary_sentences)
        if not result.endswith(('!','?','.')):
            result+='.'
        return f"{result} Check the chat for more details, {player_name}!"
    return clean_text[:350]
def generate_command_response_voice(app_name,app_type,player_name):
    clean_name=app_name.replace(".exe","").replace("https://","").replace("http://","").replace("www.","").split("/")[0].strip()
    if not clean_name:
        clean_name="that"
    responses={
        "gaming":[
            f"Opened {clean_name} for you! Go have fun, {player_name}!",
            f"{clean_name} is ready! Enjoy the game, {player_name}!",
        ],
        "coding":[
            f"Opened {clean_name}! Time to build something great, {player_name}!",
            f"{clean_name} is up and ready for you, {player_name}!",
        ],
        "web":[
            f"Opened {clean_name} for you, {player_name}!",
            f"Here you go, {player_name}! {clean_name} is ready!",
        ],
        "app":[
            f"Launched {clean_name} for you, {player_name}!",
            f"{clean_name} is now open, {player_name}!",
        ],
        "folder":[
            f"Opened the {clean_name} folder for you, {player_name}!",
            f"Here is your {clean_name} folder, {player_name}!",
        ],
        "system":[
            f"Opened {clean_name} for you, {player_name}!",
            f"{clean_name} is ready, {player_name}!",
        ],
    }
    pool=responses.get(app_type,responses["app"])
    return random.choice(pool)
def load_config():
    defaults={"api_key":"","player_name":"","voice_id":"en-US-AvaNeural"}
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE,"r") as f:
                saved=json.load(f)
                defaults.update(saved)
    except Exception:
        pass
    return defaults
def save_config(config):
    try:
        with open(CONFIG_FILE,"w") as f:
            json.dump(config,f,indent=2)
    except Exception:
        pass
def get_api_key():
    config=load_config()
    return config.get("api_key","")
def reset_all_data():
    files=[CONFIG_FILE,SAVE_FILE,CHAT_HISTORY_FILE,SETTINGS_FILE,EMOTION_FILE,COMMAND_FILE,LEARNED_COMMANDS_FILE]
    for f in files:
        try:
            if os.path.exists(f):
                os.remove(f)
        except Exception:
            pass
def restart_application():
    python=sys.executable
    os.execl(python,python,*sys.argv)
def get_player_name():
    config=load_config()
    name=config.get("player_name","")
    if name:
        return name
    try:
        if os.path.exists(SAVE_FILE):
            with open(SAVE_FILE,"r") as f:
                return json.load(f).get("name","Friend")
    except Exception:
        pass
    return "Friend"
def load_settings():
    defaults={"sound_enabled":True,"idle_transparency":True,"player_name":"","tts_enabled":True,"tts_volume":0.8,"chat_font_size":16}
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE,"r") as f:
                defaults.update(json.load(f))
    except Exception:
        pass
    return defaults
def save_settings(settings):
    try:
        with open(SETTINGS_FILE,"w") as f:
            json.dump(settings,f)
    except Exception:
        pass
def send_emotion(emotion,message="",duration=5000):
    data={"emotion":emotion,"message":message,"timestamp":time.time(),"duration":duration}
    try:
        with open(EMOTION_FILE,"w") as f:
            json.dump(data,f)
    except Exception:
        pass
def read_emotion():
    try:
        if os.path.exists(EMOTION_FILE):
            with open(EMOTION_FILE,"r") as f:
                return json.load(f)
    except Exception:
        pass
    return {"emotion":"neutral","message":"","timestamp":0,"duration":0}
def get_gemini_client():
    global gemini_client
    if gemini_client is None:
        api_key=get_api_key()
        if api_key:
            gemini_client=genai.Client(api_key=api_key)
    return gemini_client
def capture_screen():
    if not HAS_SCREENSHOT:
        return None
    try:
        return pyautogui.screenshot()
    except Exception:
        return None
def image_to_base64(image):
    if image is None:
        return None
    try:
        buffer=io.BytesIO()
        image.save(buffer,format="PNG")
        return base64.b64encode(buffer.getvalue()).decode("utf-8")
    except Exception:
        return None
def get_weather():
    try:
        import urllib.request
        url="https://wttr.in/?format=%t+%C"
        req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"})
        with urllib.request.urlopen(req,timeout=3) as response:
            data=response.read().decode("utf-8").strip()
            return data if data else "Weather unavailable"
    except Exception:
        return "Weather unavailable"
def get_active_window_title():
    try:
        hwnd=ctypes.windll.user32.GetForegroundWindow()
        length=ctypes.windll.user32.GetWindowTextLengthW(hwnd)
        if length==0:
            return ""
        buf=ctypes.create_unicode_buffer(length+1)
        ctypes.windll.user32.GetWindowTextW(hwnd,buf,length+1)
        return buf.value.lower().strip()
    except Exception:
        return ""
def get_active_process_name():
    try:
        hwnd=ctypes.windll.user32.GetForegroundWindow()
        pid=ctypes.c_ulong()
        ctypes.windll.user32.GetWindowThreadProcessId(hwnd,ctypes.byref(pid))
        handle=ctypes.windll.kernel32.OpenProcess(0x0410,False,pid.value)
        buf=ctypes.create_unicode_buffer(260)
        ctypes.windll.psapi.GetModuleFileNameExW(handle,None,buf,260)
        ctypes.windll.kernel32.CloseHandle(handle)
        return os.path.basename(buf.value).lower()
    except Exception:
        return ""
COMMAND_MAP={"open notepad":{"type":"app","target":"notepad.exe","response":"Notepad is open for you!","emotion":"happy"},"open calculator":{"type":"app","target":"calc.exe","response":"Calculator is ready!","emotion":"curious"},"open paint":{"type":"app","target":"mspaint.exe","response":"Paint is open! Get creative!","emotion":"excited"},"open cmd":{"type":"app","target":"cmd.exe","response":"Command prompt is ready!","emotion":"proud"},"open powershell":{"type":"app","target":"powershell.exe","response":"PowerShell is ready for you!","emotion":"determined"},"open terminal":{"type":"app","target":"wt.exe","response":"Terminal is open and ready!","emotion":"proud"},"open explorer":{"type":"app","target":"explorer.exe","response":"File Explorer is open!","emotion":"curious"},"open task manager":{"type":"app","target":"taskmgr.exe","response":"Task Manager is up!","emotion":"worried"},"open settings":{"type":"system","target":"ms-settings:","response":"Settings is open!","emotion":"watching"},"open control panel":{"type":"app","target":"control.exe","response":"Control Panel is ready!","emotion":"watching"},"open snipping tool":{"type":"app","target":"snippingtool.exe","response":"Snipping Tool is ready!","emotion":"happy"},"open word":{"type":"app","target":"winword.exe","response":"Word is open! Start writing!","emotion":"watching"},"open excel":{"type":"app","target":"excel.exe","response":"Excel is ready for you!","emotion":"determined"},"open powerpoint":{"type":"app","target":"powerpnt.exe","response":"PowerPoint is ready!","emotion":"excited"},"open outlook":{"type":"app","target":"outlook.exe","response":"Outlook is open!","emotion":"watching"},"open onenote":{"type":"app","target":"onenote.exe","response":"OneNote is open!","emotion":"happy"},"open teams":{"type":"system","target":"ms-teams:","response":"Teams is ready!","emotion":"watching"},"open chrome":{"type":"app","target":"chrome.exe","response":"Chrome is open!","emotion":"curious"},"open firefox":{"type":"app","target":"firefox.exe","response":"Firefox is ready!","emotion":"proud"},"open edge":{"type":"app","target":"msedge.exe","response":"Edge is open!","emotion":"watching"},"open brave":{"type":"app","target":"brave.exe","response":"Brave browser is open!","emotion":"proud"},"open opera":{"type":"app","target":"opera.exe","response":"Opera is ready!","emotion":"happy"},"open discord":{"type":"app","target":"discord.exe","response":"Discord is open! Enjoy chatting!","emotion":"happy"},"open spotify":{"type":"app","target":"spotify.exe","response":"Spotify is ready! Enjoy the music!","emotion":"happy"},"open steam":{"type":"system","target":"steam://open/main","response":"Steam is opening! Ready to game?","emotion":"excited"},"open epic":{"type":"app","target":"epicgameslauncher.exe","response":"Epic Games is open!","emotion":"excited"},"open obs":{"type":"app","target":"obs64.exe","response":"OBS is ready! Start recording!","emotion":"excited"},"open vlc":{"type":"app","target":"vlc.exe","response":"VLC is open! Enjoy!","emotion":"happy"},"open zoom":{"type":"app","target":"zoom.exe","response":"Zoom is ready!","emotion":"watching"},"open slack":{"type":"app","target":"slack.exe","response":"Slack is open!","emotion":"watching"},"open telegram":{"type":"app","target":"telegram.exe","response":"Telegram is open!","emotion":"happy"},"open whatsapp":{"type":"app","target":"whatsapp.exe","response":"WhatsApp is open!","emotion":"happy"},"open vscode":{"type":"app","target":"code","response":"VS Code is ready! Let's build something!","emotion":"excited"},"open visual studio":{"type":"app","target":"devenv.exe","response":"Visual Studio is loading!","emotion":"excited"},"open pycharm":{"type":"app","target":"pycharm64.exe","response":"PyCharm is ready! Let's code!","emotion":"proud"},"open android studio":{"type":"app","target":"studio64.exe","response":"Android Studio is open!","emotion":"excited"},"open blender":{"type":"app","target":"blender.exe","response":"Blender is ready! Get creative!","emotion":"excited"},"open unity":{"type":"app","target":"unity.exe","response":"Unity is loading!","emotion":"excited"},"open figma":{"type":"app","target":"figma.exe","response":"Figma is ready! Start designing!","emotion":"excited"},"open notion":{"type":"app","target":"notion.exe","response":"Notion is open! Stay organized!","emotion":"determined"},"open youtube":{"type":"web","target":"https://www.youtube.com","response":"YouTube is open! Enjoy!","emotion":"happy"},"open yt":{"type":"web","target":"https://www.youtube.com","response":"YouTube is open! Enjoy!","emotion":"happy"},"open google":{"type":"web","target":"https://www.google.com","response":"Google is ready!","emotion":"curious"},"open github":{"type":"web","target":"https://www.github.com","response":"GitHub is open! Let's build!","emotion":"proud"},"open gitlab":{"type":"web","target":"https://www.gitlab.com","response":"GitLab is open!","emotion":"proud"},"open gmail":{"type":"web","target":"https://mail.google.com","response":"Gmail is open!","emotion":"watching"},"open google drive":{"type":"web","target":"https://drive.google.com","response":"Google Drive is ready!","emotion":"happy"},"open google docs":{"type":"web","target":"https://docs.google.com","response":"Google Docs is open!","emotion":"watching"},"open google sheets":{"type":"web","target":"https://sheets.google.com","response":"Google Sheets is ready!","emotion":"watching"},"open google slides":{"type":"web","target":"https://slides.google.com","response":"Google Slides is open!","emotion":"watching"},"open google colab":{"type":"web","target":"https://colab.research.google.com","response":"Colab is ready! Free GPU time!","emotion":"excited"},"open colab":{"type":"web","target":"https://colab.research.google.com","response":"Colab is open!","emotion":"excited"},"open reddit":{"type":"web","target":"https://www.reddit.com","response":"Reddit is open!","emotion":"curious"},"open twitter":{"type":"web","target":"https://www.twitter.com","response":"Twitter is open!","emotion":"curious"},"open x":{"type":"web","target":"https://www.twitter.com","response":"X is open!","emotion":"curious"},"open instagram":{"type":"web","target":"https://www.instagram.com","response":"Instagram is open! Enjoy!","emotion":"happy"},"open ig":{"type":"web","target":"https://www.instagram.com","response":"Instagram is open!","emotion":"happy"},"open facebook":{"type":"web","target":"https://www.facebook.com","response":"Facebook is open!","emotion":"happy"},"open fb":{"type":"web","target":"https://www.facebook.com","response":"Facebook is open!","emotion":"happy"},"open linkedin":{"type":"web","target":"https://www.linkedin.com","response":"LinkedIn is open! Network away!","emotion":"proud"},"open whatsapp web":{"type":"web","target":"https://web.whatsapp.com","response":"WhatsApp Web is open!","emotion":"happy"},"open telegram web":{"type":"web","target":"https://web.telegram.org","response":"Telegram Web is ready!","emotion":"happy"},"open netflix":{"type":"web","target":"https://www.netflix.com","response":"Netflix is open! Enjoy the show!","emotion":"excited"},"open amazon":{"type":"web","target":"https://www.amazon.com","response":"Amazon is open!","emotion":"curious"},"open wikipedia":{"type":"web","target":"https://www.wikipedia.org","response":"Wikipedia is open! Learn something new!","emotion":"curious"},"open stackoverflow":{"type":"web","target":"https://stackoverflow.com","response":"Stack Overflow is ready! Find your answer!","emotion":"proud"},"open stack overflow":{"type":"web","target":"https://stackoverflow.com","response":"Stack Overflow is open!","emotion":"proud"},"open w3schools":{"type":"web","target":"https://www.w3schools.com","response":"W3Schools is open!","emotion":"happy"},"open coursera":{"type":"web","target":"https://www.coursera.org","response":"Coursera is open! Keep learning!","emotion":"proud"},"open udemy":{"type":"web","target":"https://www.udemy.com","response":"Udemy is open!","emotion":"excited"},"open khan academy":{"type":"web","target":"https://www.khanacademy.org","response":"Khan Academy is ready!","emotion":"proud"},"open leetcode":{"type":"web","target":"https://leetcode.com","response":"LeetCode is open! Grind time!","emotion":"determined"},"open neetcode":{"type":"web","target":"https://neetcode.io","response":"NeetCode is ready!","emotion":"proud"},"open hackerrank":{"type":"web","target":"https://www.hackerrank.com","response":"HackerRank is open!","emotion":"excited"},"open codeforces":{"type":"web","target":"https://codeforces.com","response":"Codeforces is open! Compete hard!","emotion":"determined"},"open codechef":{"type":"web","target":"https://www.codechef.com","response":"CodeChef is ready!","emotion":"excited"},"open geeksforgeeks":{"type":"web","target":"https://www.geeksforgeeks.org","response":"GeeksForGeeks is open!","emotion":"proud"},"open gfg":{"type":"web","target":"https://www.geeksforgeeks.org","response":"GFG is ready!","emotion":"proud"},"open chatgpt":{"type":"web","target":"https://chat.openai.com","response":"ChatGPT is open!","emotion":"playful"},"open claude":{"type":"web","target":"https://claude.ai","response":"Claude is open!","emotion":"playful"},"open gemini":{"type":"web","target":"https://gemini.google.com","response":"Gemini is open! That is my brain!","emotion":"proud"},"open perplexity":{"type":"web","target":"https://www.perplexity.ai","response":"Perplexity is open!","emotion":"curious"},"open canva":{"type":"web","target":"https://www.canva.com","response":"Canva is open! Create something beautiful!","emotion":"excited"},"open figma web":{"type":"web","target":"https://www.figma.com","response":"Figma Web is open!","emotion":"excited"},"open notion web":{"type":"web","target":"https://www.notion.so","response":"Notion is open! Stay organized!","emotion":"determined"},"open twitch":{"type":"web","target":"https://www.twitch.tv","response":"Twitch is open! Enjoy the streams!","emotion":"excited"},"open pinterest":{"type":"web","target":"https://www.pinterest.com","response":"Pinterest is open!","emotion":"happy"},"open tiktok":{"type":"web","target":"https://www.tiktok.com","response":"TikTok is open! Don't scroll too long!","emotion":"playful"},"open ebay":{"type":"web","target":"https://www.ebay.com","response":"eBay is open!","emotion":"curious"},"open zoom web":{"type":"web","target":"https://zoom.us","response":"Zoom Web is ready!","emotion":"watching"},"open slack web":{"type":"web","target":"https://slack.com","response":"Slack Web is open!","emotion":"watching"},"open spotify web":{"type":"web","target":"https://open.spotify.com","response":"Spotify Web is ready! Enjoy the music!","emotion":"happy"},"open replit":{"type":"web","target":"https://replit.com","response":"Replit is ready! Cloud coding time!","emotion":"excited"},"open kaggle":{"type":"web","target":"https://www.kaggle.com","response":"Kaggle is open!","emotion":"proud"},"open huggingface":{"type":"web","target":"https://huggingface.co","response":"HuggingFace is open!","emotion":"excited"},"open vercel":{"type":"web","target":"https://vercel.com","response":"Vercel is open! Deploy something great!","emotion":"proud"},"open netlify":{"type":"web","target":"https://www.netlify.com","response":"Netlify is open!","emotion":"proud"},"open render":{"type":"web","target":"https://render.com","response":"Render is open!","emotion":"happy"},"open medium":{"type":"web","target":"https://medium.com","response":"Medium is open! Read something good!","emotion":"curious"},"open devto":{"type":"web","target":"https://dev.to","response":"Dev.to is open!","emotion":"happy"},"open hashnode":{"type":"web","target":"https://hashnode.com","response":"Hashnode is open!","emotion":"proud"},"open codepen":{"type":"web","target":"https://codepen.io","response":"CodePen is ready!","emotion":"excited"},"open jsfiddle":{"type":"web","target":"https://jsfiddle.net","response":"JSFiddle is open!","emotion":"happy"},"open npmjs":{"type":"web","target":"https://www.npmjs.com","response":"NPM is open!","emotion":"watching"},"open pypi":{"type":"web","target":"https://pypi.org","response":"PyPI is open!","emotion":"proud"},"open docker hub":{"type":"web","target":"https://hub.docker.com","response":"Docker Hub is open!","emotion":"proud"},"open aws":{"type":"web","target":"https://aws.amazon.com","response":"AWS Console is open!","emotion":"determined"},"open azure":{"type":"web","target":"https://portal.azure.com","response":"Azure Portal is open!","emotion":"proud"},"open firebase":{"type":"web","target":"https://console.firebase.google.com","response":"Firebase Console is open!","emotion":"excited"},"open mongodb":{"type":"web","target":"https://cloud.mongodb.com","response":"MongoDB Atlas is open!","emotion":"proud"},"open postman":{"type":"web","target":"https://web.postman.co","response":"Postman is ready! Test those APIs!","emotion":"watching"},"open dribbble":{"type":"web","target":"https://dribbble.com","response":"Dribbble is open! Get inspired!","emotion":"excited"},"open behance":{"type":"web","target":"https://www.behance.net","response":"Behance is open!","emotion":"excited"},"open trello":{"type":"web","target":"https://trello.com","response":"Trello is open! Stay organized!","emotion":"determined"},"open jira":{"type":"web","target":"https://www.atlassian.com/software/jira","response":"Jira is open! Sprint time!","emotion":"determined"},"open snapchat":{"type":"web","target":"https://www.snapchat.com","response":"Snapchat is open!","emotion":"happy"},"open discord web":{"type":"web","target":"https://discord.com/app","response":"Discord Web is open!","emotion":"happy"},"open apple music":{"type":"web","target":"https://music.apple.com","response":"Apple Music is open! Enjoy!","emotion":"happy"},"open soundcloud":{"type":"web","target":"https://soundcloud.com","response":"SoundCloud is open! Enjoy the vibes!","emotion":"happy"},"open flipkart":{"type":"web","target":"https://www.flipkart.com","response":"Flipkart is open!","emotion":"curious"},"open documents":{"type":"folder","target":"Documents","response":"Documents folder is open!","emotion":"watching"},"open downloads":{"type":"folder","target":"Downloads","response":"Downloads folder is ready!","emotion":"curious"},"open desktop":{"type":"folder","target":"Desktop","response":"Desktop folder is open!","emotion":"watching"},"open pictures":{"type":"folder","target":"Pictures","response":"Pictures folder is open!","emotion":"happy"},"open music folder":{"type":"folder","target":"Music","response":"Music folder is ready!","emotion":"happy"},"open videos":{"type":"folder","target":"Videos","response":"Videos folder is open!","emotion":"excited"}}
ABBREVIATIONS={"yt":"youtube","ig":"instagram","fb":"facebook","tw":"twitter","wp":"whatsapp","tg":"telegram","dc":"discord","gm":"gmail","gh":"github","vs":"vscode","calc":"calculator","np":"notepad","gd":"google drive","nf":"netflix","amz":"amazon","wiki":"wikipedia","ppt":"powerpoint","docs":"google docs","lc":"leetcode","nc":"neetcode","hr":"hackerrank","cf":"codeforces","cc":"codechef","gfg":"geeksforgeeks"}
APP_WATCH_MAP={"github":{"emotion":"proud","text":"Coding on GitHub!","type":"coding","speak":False},"gitlab":{"emotion":"proud","text":"Coding on GitLab!","type":"coding","speak":False},"leetcode":{"emotion":"determined","text":"LeetCode grind!","type":"coding","speak":False},"neetcode":{"emotion":"proud","text":"NeetCode session!","type":"coding","speak":False},"hackerrank":{"emotion":"determined","text":"HackerRank challenge!","type":"coding","speak":False},"codeforces":{"emotion":"determined","text":"Codeforces — compete!","type":"coding","speak":False},"codechef":{"emotion":"excited","text":"CodeChef session!","type":"coding","speak":False},"geeksforgeeks":{"emotion":"proud","text":"Learning on GFG!","type":"learning","speak":False},"stackoverflow":{"emotion":"proud","text":"Stack Overflow session!","type":"coding","speak":False},"visual studio":{"emotion":"proud","text":"Coding in Visual Studio!","type":"coding","speak":False},"vs code":{"emotion":"excited","text":"VS Code is open!","type":"coding","speak":False},"code -":{"emotion":"excited","text":"VS Code session!","type":"coding","speak":False},"pycharm":{"emotion":"proud","text":"PyCharm — Python time!","type":"coding","speak":False},"sublime":{"emotion":"watching","text":"Sublime Text!","type":"coding","speak":False},"intellij":{"emotion":"proud","text":"IntelliJ — serious code!","type":"coding","speak":False},"android studio":{"emotion":"excited","text":"Android dev time!","type":"coding","speak":False},"vim":{"emotion":"proud","text":"Vim — respect!","type":"coding","speak":False},"neovim":{"emotion":"proud","text":"Neovim power user!","type":"coding","speak":False},"terminal":{"emotion":"determined","text":"Terminal work!","type":"coding","speak":False},"powershell":{"emotion":"determined","text":"PowerShell scripting!","type":"coding","speak":False},"cmd.exe":{"emotion":"watching","text":"CMD running!","type":"coding","speak":False},"postman":{"emotion":"curious","text":"API testing!","type":"coding","speak":False},"docker":{"emotion":"proud","text":"Docker — shipping it!","type":"coding","speak":False},"kaggle":{"emotion":"excited","text":"Kaggle data science!","type":"coding","speak":False},"huggingface":{"emotion":"excited","text":"HuggingFace AI!","type":"coding","speak":False},"jupyter":{"emotion":"proud","text":"Jupyter Notebook!","type":"coding","speak":False},"colab":{"emotion":"excited","text":"Colab — free GPU!","type":"coding","speak":False},"replit":{"emotion":"happy","text":"Replit cloud coding!","type":"coding","speak":False},"counter-strike":{"emotion":"excited","text":"CS — good luck!","type":"gaming","speak":True},"dota":{"emotion":"excited","text":"Dota 2 — focus up!","type":"gaming","speak":True},"call of duty":{"emotion":"excited","text":"CoD — stay sharp!","type":"gaming","speak":True},"elden ring":{"emotion":"determined","text":"Elden Ring — persist!","type":"gaming","speak":True},"minecraft":{"emotion":"happy","text":"Minecraft — build it!","type":"gaming","speak":True},"valorant":{"emotion":"excited","text":"Valorant — let's go!","type":"gaming","speak":True},"fortnite":{"emotion":"excited","text":"Fortnite — win it!","type":"gaming","speak":True},"genshin":{"emotion":"happy","text":"Genshin — enjoy!","type":"gaming","speak":True},"league of legends":{"emotion":"determined","text":"LoL — play well!","type":"gaming","speak":True},"apex legends":{"emotion":"excited","text":"Apex — be the champ!","type":"gaming","speak":True},"overwatch":{"emotion":"excited","text":"Overwatch — team up!","type":"gaming","speak":True},"roblox":{"emotion":"happy","text":"Roblox — have fun!","type":"gaming","speak":True},"stardew":{"emotion":"happy","text":"Stardew — just relax!","type":"gaming","speak":True},"among us":{"emotion":"playful","text":"Trust nobody here!","type":"gaming","speak":True},"terraria":{"emotion":"happy","text":"Terraria — build on!","type":"gaming","speak":True},"cyberpunk":{"emotion":"excited","text":"Cyberpunk — enjoy!","type":"gaming","speak":True},"steam":{"emotion":"excited","text":"Gaming time!","type":"gaming","speak":False},"gta":{"emotion":"excited","text":"GTA — have a blast!","type":"gaming","speak":True},"rocket league":{"emotion":"excited","text":"Rocket League!","type":"gaming","speak":True},"pubg":{"emotion":"excited","text":"PUBG — survive!","type":"gaming","speak":True},"dark souls":{"emotion":"determined","text":"Dark Souls — persist!","type":"gaming","speak":True},"coursera":{"emotion":"proud","text":"Coursera — learning!","type":"learning","speak":False},"udemy":{"emotion":"happy","text":"Udemy — keep going!","type":"learning","speak":False},"khan academy":{"emotion":"proud","text":"Khan Academy!","type":"learning","speak":False},"youtube":{"emotion":"watching","text":"Watching YouTube","type":"distraction","speak":False},"instagram":{"emotion":"watching","text":"On Instagram","type":"distraction","speak":False},"tiktok":{"emotion":"worried","text":"TikTok — watch the clock!","type":"distraction","speak":False},"reddit":{"emotion":"curious","text":"Browsing Reddit","type":"distraction","speak":False},"netflix":{"emotion":"excited","text":"Watching Netflix","type":"entertainment","speak":False},"twitch":{"emotion":"excited","text":"Watching Twitch","type":"entertainment","speak":False},"discord":{"emotion":"happy","text":"On Discord","type":"social","speak":False},"whatsapp":{"emotion":"happy","text":"On WhatsApp","type":"social","speak":False},"telegram":{"emotion":"happy","text":"On Telegram","type":"social","speak":False},"spotify":{"emotion":"happy","text":"Listening to Spotify","type":"music","speak":False},"word":{"emotion":"determined","text":"Writing in Word","type":"work","speak":False},"excel":{"emotion":"determined","text":"Working in Excel","type":"work","speak":False},"powerpoint":{"emotion":"excited","text":"Building a presentation","type":"work","speak":False},"notion":{"emotion":"determined","text":"Organizing in Notion","type":"work","speak":False},"figma":{"emotion":"excited","text":"Designing in Figma","type":"creative","speak":False},"photoshop":{"emotion":"excited","text":"Creating in Photoshop","type":"creative","speak":False},"blender":{"emotion":"excited","text":"3D work in Blender","type":"creative","speak":False},"obs":{"emotion":"excited","text":"Recording with OBS","type":"creative","speak":False},"chatgpt":{"emotion":"playful","text":"On ChatGPT","type":"ai","speak":False},"claude":{"emotion":"playful","text":"On Claude","type":"ai","speak":False},"gemini":{"emotion":"proud","text":"On Gemini — my brain!","type":"ai","speak":False},"chrome":{"emotion":"watching","text":"Browsing in Chrome","type":"browsing","speak":False},"firefox":{"emotion":"watching","text":"Browsing in Firefox","type":"browsing","speak":False},"edge":{"emotion":"watching","text":"Browsing in Edge","type":"browsing","speak":False},"brave":{"emotion":"proud","text":"Browsing in Brave","type":"browsing","speak":False}}
DISTRACTION_APPS=["youtube","tiktok","instagram","reddit","twitter","netflix","twitch"]
RANDOM_QUOTES=[{"text":"You are doing great!","emotion":"happy","speak":True},{"text":"Experts were once beginners too!","emotion":"proud","speak":True},{"text":"Breathe, you have got this!","emotion":"comfort","speak":True},{"text":"Stay hydrated!","emotion":"caring","speak":True},{"text":"Today builds tomorrow!","emotion":"proud","speak":False},{"text":"Small steps lead to big wins!","emotion":"happy","speak":False},{"text":"I am rooting for you!","emotion":"loving","speak":True},{"text":"Take a quick stretch!","emotion":"caring","speak":True},{"text":"Keep pushing forward!","emotion":"determined","speak":False},{"text":"Mistakes mean you are trying!","emotion":"proud","speak":False},{"text":"Have you eaten yet?","emotion":"caring","speak":True},{"text":"Progress over perfection!","emotion":"happy","speak":False},{"text":"Your dedication is inspiring!","emotion":"proud","speak":False},{"text":"Drink some water!","emotion":"caring","speak":True},{"text":"Sit up straight!","emotion":"caring","speak":True},{"text":"Consistency always wins!","emotion":"proud","speak":False},{"text":"Be kind to yourself!","emotion":"caring","speak":True},{"text":"Breaks boost your output!","emotion":"caring","speak":True},{"text":"Remember why you started!","emotion":"determined","speak":True},{"text":"Hard work always pays off!","emotion":"proud","speak":False},{"text":"Celebrate your small wins!","emotion":"excited","speak":True},{"text":"Rest is part of progress!","emotion":"caring","speak":True},{"text":"Future you says thank you!","emotion":"proud","speak":True},{"text":"Go {player_name}!","emotion":"excited","speak":True},{"text":"{player_name}, you have got this!","emotion":"loving","speak":True},{"text":"So proud of you, {player_name}!","emotion":"proud","speak":True},{"text":"{player_name}, stay focused!","emotion":"determined","speak":False}]
CODING_QUOTES=[{"text":"Clean code always wins!","emotion":"proud","speak":False},{"text":"Remember to commit your changes!","emotion":"watching","speak":True},{"text":"Test before pushing!","emotion":"caring","speak":True},{"text":"Try the rubber duck method!","emotion":"playful","speak":False},{"text":"Good names save so much time!","emotion":"proud","speak":False},{"text":"Bugs make you a stronger developer!","emotion":"proud","speak":False},{"text":"You are building something awesome!","emotion":"excited","speak":True},{"text":"Keep functions small and focused!","emotion":"watching","speak":False},{"text":"Git is your safety net!","emotion":"caring","speak":True},{"text":"Solve it first, optimize later!","emotion":"determined","speak":False},{"text":"Push your code, {player_name}!","emotion":"proud","speak":True},{"text":"Ship it, {player_name}!","emotion":"excited","speak":True}]
GAMING_QUOTES=[{"text":"Fun is what matters most!","emotion":"happy","speak":True},{"text":"You are getting better each round!","emotion":"proud","speak":True},{"text":"Remember to take breaks between matches!","emotion":"caring","speak":True},{"text":"Stay focused, you can win this!","emotion":"excited","speak":True},{"text":"Losing is just learning!","emotion":"comfort","speak":True},{"text":"Stay hydrated while gaming!","emotion":"caring","speak":True},{"text":"Stay cool, do not tilt!","emotion":"caring","speak":True},{"text":"Every pro was once a beginner!","emotion":"proud","speak":True},{"text":"Stretch your wrists!","emotion":"caring","speak":True},{"text":"Go get them, {player_name}!","emotion":"excited","speak":True},{"text":"Win this one, {player_name}!","emotion":"determined","speak":True}]
STUDY_QUOTES=[{"text":"Knowledge is real power!","emotion":"proud","speak":False},{"text":"25 minutes focus, 5 minutes break!","emotion":"caring","speak":True},{"text":"Understanding beats memorization!","emotion":"proud","speak":False},{"text":"You are investing in yourself!","emotion":"happy","speak":True},{"text":"Active recall is the key!","emotion":"determined","speak":False},{"text":"Your brain needs breaks too!","emotion":"caring","speak":True},{"text":"You have got this, {player_name}!","emotion":"loving","speak":True},{"text":"Study hard, {player_name}!","emotion":"determined","speak":True}]
WORK_QUOTES=[{"text":"One task at a time!","emotion":"determined","speak":False},{"text":"Prioritize what truly matters!","emotion":"watching","speak":False},{"text":"Great work deserves a great break!","emotion":"caring","speak":True},{"text":"Save your work!","emotion":"caring","speak":True},{"text":"Crush it, {player_name}!","emotion":"excited","speak":True}]
CREATIVE_QUOTES=[{"text":"Your creativity is flowing!","emotion":"excited","speak":False},{"text":"Drafts become masterpieces!","emotion":"proud","speak":False},{"text":"Trust the process!","emotion":"happy","speak":True},{"text":"Your vision is unique!","emotion":"proud","speak":True},{"text":"Save your project!","emotion":"caring","speak":True},{"text":"The world needs your art!","emotion":"loving","speak":True},{"text":"Create, {player_name}!","emotion":"excited","speak":True}]
BROWSING_QUOTES=[{"text":"Finding what you need?","emotion":"curious","speak":False},{"text":"Stay focused on your search!","emotion":"watching","speak":False},{"text":"Too many tabs open!","emotion":"playful","speak":False},{"text":"Stay on track!","emotion":"watching","speak":False}]
DISTRACTION_QUOTES=[{"text":"How long have you been scrolling?","emotion":"worried","speak":True},{"text":"Your goals are waiting for you!","emotion":"determined","speak":True},{"text":"Five more minutes then back to it!","emotion":"caring","speak":True},{"text":"Balance is the key!","emotion":"caring","speak":True},{"text":"Back to work, {player_name}!","emotion":"determined","speak":True},{"text":"Focus up, {player_name}!","emotion":"worried","speak":True}]
SOCIAL_QUOTES=[{"text":"Staying connected is important!","emotion":"happy","speak":False},{"text":"Good conversations make great days!","emotion":"happy","speak":False},{"text":"Friends matter a lot!","emotion":"loving","speak":False}]
MUSIC_QUOTES=[{"text":"Music makes everything better!","emotion":"happy","speak":False},{"text":"Good taste in music!","emotion":"happy","speak":False}]
NIGHT_QUOTES=[{"text":"Getting late, please rest soon!","emotion":"caring","speak":True},{"text":"Even legends need sleep!","emotion":"caring","speak":True},{"text":"Tomorrow awaits, rest now!","emotion":"caring","speak":True},{"text":"Your health comes above everything!","emotion":"loving","speak":True},{"text":"Sleep locks in your memories!","emotion":"caring","speak":True},{"text":"Past midnight is costly tomorrow!","emotion":"worried","speak":True},{"text":"Please rest now, {player_name}!","emotion":"caring","speak":True},{"text":"Rest up, {player_name}!","emotion":"loving","speak":True}]
MORNING_QUOTES=[{"text":"Morning! Fresh start today!","emotion":"excited","speak":True},{"text":"Rise and shine!","emotion":"happy","speak":True},{"text":"Let us make today count!","emotion":"proud","speak":True},{"text":"Had breakfast yet?","emotion":"caring","speak":True},{"text":"Today is going to be great!","emotion":"excited","speak":True},{"text":"Morning, {player_name}!","emotion":"happy","speak":True},{"text":"Rise up, {player_name}!","emotion":"excited","speak":True}]
WEEKEND_QUOTES=[{"text":"Weekend! Relax a little!","emotion":"happy","speak":True},{"text":"Take some time for yourself!","emotion":"caring","speak":True},{"text":"Weekends are for recharging!","emotion":"happy","speak":True},{"text":"Enjoy it, {player_name}!","emotion":"happy","speak":True}]
COMEBACK_QUOTES=[{"text":"Welcome back!","emotion":"happy","min_away":10,"speak":True},{"text":"Ready to go again?","emotion":"excited","min_away":10,"speak":True},{"text":"Hey, you are back!","emotion":"happy","min_away":15,"speak":True},{"text":"Everything okay?","emotion":"caring","min_away":30,"speak":True},{"text":"Good to have you back!","emotion":"happy","min_away":30,"speak":True},{"text":"Been a while! Welcome back!","emotion":"excited","min_away":60,"speak":True},{"text":"Hope you are doing well!","emotion":"loving","min_away":120,"speak":True},{"text":"Back, {player_name}!","emotion":"happy","min_away":10,"speak":True},{"text":"Missed you, {player_name}!","emotion":"loving","min_away":30,"speak":True}]
AFFIRMATION_QUOTES=[{"text":"You are never alone, I am here!","emotion":"loving","speak":True},{"text":"Your effort matters so much!","emotion":"proud","speak":True},{"text":"Tomorrow is always a fresh start!","emotion":"comfort","speak":True},{"text":"You deserve good things!","emotion":"loving","speak":True},{"text":"Always right here for you!","emotion":"comfort","speak":True},{"text":"The world needs you in it!","emotion":"loving","speak":True},{"text":"I am here, {player_name}!","emotion":"loving","speak":True},{"text":"So proud of you, {player_name}!","emotion":"proud","speak":True},{"text":"{player_name}, you matter!","emotion":"comfort","speak":True}]
SCREEN_TIME_WARNINGS=[{"minutes":60,"text":"One hour in — stretch now!","emotion":"caring","speak":True},{"minutes":90,"text":"Ninety minutes — rest your eyes!","emotion":"worried","speak":True},{"minutes":120,"text":"Two hours in — take a real break!","emotion":"worried","speak":True},{"minutes":150,"text":"Two and a half hours — your body needs rest!","emotion":"worried","speak":True},{"minutes":180,"text":"Three hours — take a break right now!","emotion":"worried","speak":True},{"minutes":240,"text":"Four hours — please stop and rest!","emotion":"angry","speak":True}]
DISTRACTION_WARNINGS=[{"minutes":15,"text":"Fifteen minutes scrolling already...","emotion":"watching","speak":True},{"minutes":30,"text":"Thirty minutes — maybe switch back now?","emotion":"worried","speak":True},{"minutes":45,"text":"Forty five minutes — time to refocus!","emotion":"worried","speak":True},{"minutes":60,"text":"One hour — get back on track!","emotion":"angry","speak":True}]
ACTIVITY_QUOTES_MAP={"coding":CODING_QUOTES,"gaming":GAMING_QUOTES,"learning":STUDY_QUOTES,"work":WORK_QUOTES,"creative":CREATIVE_QUOTES,"browsing":BROWSING_QUOTES,"distraction":DISTRACTION_QUOTES,"social":SOCIAL_QUOTES,"music":MUSIC_QUOTES,"ai":CODING_QUOTES,"shopping":BROWSING_QUOTES,"entertainment":BROWSING_QUOTES}
def load_learned_commands():
    try:
        if os.path.exists(LEARNED_COMMANDS_FILE):
            with open(LEARNED_COMMANDS_FILE,"r") as f:
                return json.load(f)
    except Exception:
        pass
    return {}
def save_learned_commands(commands):
    try:
        with open(LEARNED_COMMANDS_FILE,"w") as f:
            json.dump(commands,f,indent=2)
    except Exception:
        pass
def add_learned_command(name,cmd_type,target,response=None,aliases=None):
    commands=load_learned_commands()
    player_name=get_player_name()
    commands[name.lower()]={"type":cmd_type,"target":target,"response":response or f"Opened {name} for you, {player_name}!","learned_at":datetime.now().strftime("%Y-%m-%d %H:%M"),"aliases":aliases or [],"emotion":"happy"}
    save_learned_commands(commands)
    return True
def remove_learned_command(name):
    commands=load_learned_commands()
    name_lower=name.lower()
    if name_lower in commands:
        del commands[name_lower]
        save_learned_commands(commands)
        return True
    for key,data in list(commands.items()):
        if name_lower in [a.lower() for a in data.get("aliases",[])]:
            del commands[key]
            save_learned_commands(commands)
            return True
    return False
def get_learned_command(name):
    commands=load_learned_commands()
    name_lower=name.lower()
    if name_lower in commands:
        return commands[name_lower]
    for key,data in commands.items():
        if name_lower in [a.lower() for a in data.get("aliases",[])]:
            return data
    return None
def find_similar_commands(name,threshold=0.55):
    name_lower=name.lower().strip()
    all_commands=list(COMMAND_MAP.keys())+list(load_learned_commands().keys())
    all_targets=[k.replace("open ","").lower() for k in all_commands]
    matches=difflib.get_close_matches(name_lower,all_targets,n=3,cutoff=threshold)
    result=[]
    for m in matches:
        for k in COMMAND_MAP:
            if k.replace("open ","")==m:
                result.append(k)
                break
        learned=load_learned_commands()
        if m in learned:
            result.append(m)
    return result[:3]
def fuzzy_find_command(query,threshold=0.6):
    query_clean=query.lower().strip()
    for prefix in ["open ","launch ","start ","go to ","take me to ","navigate to ","visit "]:
        if query_clean.startswith(prefix):
            query_clean=query_clean[len(prefix):].strip()
            break
    all_keys=list(COMMAND_MAP.keys())+list(load_learned_commands().keys())
    all_targets=[k.replace("open ","") for k in all_keys]
    matches=difflib.get_close_matches(query_clean,all_targets,n=1,cutoff=threshold)
    if matches:
        matched_target=matches[0]
        for k in COMMAND_MAP:
            if k.replace("open ","")==matched_target:
                return COMMAND_MAP[k],None
        learned=load_learned_commands()
        if matched_target in learned:
            return learned[matched_target],None
    return None,None
def parse_chat_command(message):
    msg_lower=message.lower().strip()
    if len(msg_lower)<3:
        return None,None
    for cmd_key,cmd_data in COMMAND_MAP.items():
        if msg_lower==cmd_key or msg_lower.startswith(cmd_key+" "):
            return cmd_data,None
    learned=get_learned_command(msg_lower.replace("open ","").replace("launch ","").replace("start ",""))
    if learned:
        return learned,None
    clean=msg_lower
    for w in ["can you","please","could you","would you","open","launch","start","go to"]:
        clean=clean.replace(w," ")
    clean=" ".join(clean.split()).strip()
    if len(clean)<2:
        return None,None
    for abbr,full in ABBREVIATIONS.items():
        if clean==abbr:
            clean=full
            break
    for cmd_key,cmd_data in COMMAND_MAP.items():
        cmd_target=cmd_key.replace("open ","")
        if clean==cmd_target:
            return cmd_data,None
    learned=get_learned_command(clean)
    if learned:
        return learned,None
    fuzzy_cmd,_=fuzzy_find_command(clean)
    if fuzzy_cmd:
        return fuzzy_cmd,None
    if msg_lower.startswith(("open ","launch ","go to ","start ","take me to ","visit ")):
        target=msg_lower.split(" ",1)[1].strip()
        if len(target)>1:
            if "." in target and " " not in target:
                url=target if target.startswith("http") else "https://"+target
                return {"type":"web","target":url,"response":f"Opened {target} for you!","emotion":"happy"},None
            suggestions=find_similar_commands(target)
            return None,{"unknown_target":target,"suggestions":suggestions}
    return None,None
def open_folder(folder_name):
    user_profile=os.environ.get('USERPROFILE',os.path.expanduser('~'))
    folder_map={"documents":os.path.join(user_profile,"Documents"),"downloads":os.path.join(user_profile,"Downloads"),"desktop":os.path.join(user_profile,"Desktop"),"pictures":os.path.join(user_profile,"Pictures"),"music":os.path.join(user_profile,"Music"),"videos":os.path.join(user_profile,"Videos")}
    folder_path=folder_map.get(folder_name.lower())
    if not folder_path:
        folder_path=os.path.join(user_profile,folder_name)
    if not os.path.exists(folder_path):
        folder_path=user_profile
    try:
        os.startfile(folder_path)
        return True
    except Exception:
        pass
    try:
        subprocess.Popen(['explorer',folder_path])
        return True
    except Exception:
        pass
    return False
def execute_command(cmd_data):
    try:
        cmd_type=cmd_data.get("type","")
        target=cmd_data.get("target","")
        if cmd_type=="web":
            url=target if target.startswith("http") else f"https://{target}"
            webbrowser.open(url)
            return True
        elif cmd_type=="app":
            try:
                subprocess.Popen(target,shell=False)
                return True
            except Exception:
                pass
            try:
                os.startfile(target)
                return True
            except Exception:
                pass
            try:
                subprocess.Popen(f'start "" "{target}"',shell=True)
                return True
            except Exception:
                pass
            return False
        elif cmd_type=="system":
            try:
                os.startfile(target)
                return True
            except Exception:
                pass
            try:
                subprocess.Popen(f'start {target}',shell=True)
                return True
            except Exception:
                pass
            return False
        elif cmd_type=="folder":
            return open_folder(target)
        elif cmd_type=="type":
            if HAS_SCREENSHOT:
                pyautogui.typewrite(target,interval=0.03)
                return True
            return False
    except Exception:
        return False
def detect_message_emotion(text):
    ml=text.lower()
    negation_words=["not","don't","isn't","wasn't","never","no","neither","hardly"]
    def has_negation(text_str,keyword):
        idx=text_str.find(keyword)
        if idx<=0:
            return False
        words_before=text_str[:idx].split()
        last_3=words_before[-3:] if len(words_before)>=3 else words_before
        return any(neg in last_3 for neg in negation_words)
    sad_words=["sad","depressed","lonely","alone","miss you","hurt","cry","crying","pain","heartbreak","broken","lost","empty","hopeless","worthless","tired of","give up","can't do","failed","failure","miserable","unhappy","suffering","grief","despair","nobody cares","no one","invisible","forgotten","abandoned","i can't","i give up","what's the point","hate myself","not enough","feeling down","feel bad","feel low"]
    happy_words=["happy","great","awesome","love","wonderful","amazing","excited","yay","fantastic","perfect","beautiful","brilliant","excellent","incredible","joy","blessed","grateful","thankful","celebrate","good day","best day","having fun","so good","feeling good","can't stop smiling","life is good","woohoo","let's go","hell yeah","feeling great","so happy"]
    angry_words=["angry","frustrated","hate","annoyed","furious","mad","pissed","irritated","rage","sick of","fed up","done with","stupid","ridiculous","unfair","bullshit","wtf","ugh"]
    anxious_words=["worried","anxious","nervous","scared","stress","overwhelmed","panic","fear","terrified","deadline","exam","test tomorrow","presentation","interview","what if","freaking out","can't breathe","pressure","tension","dread"]
    proud_words=["proud","accomplished","achieved","won","success","passed","graduated","promoted","finished","completed","made it","did it","got accepted","nailed it","aced","first place","top score","built it","shipped it","launched","published","milestone"]
    love_words=["love you","appreciate you","thank you nova","you're the best","you're amazing","you're cute","you're beautiful","i love","you mean a lot","grateful for you","lucky to have you","you make me happy","you're special","adore you"]
    bored_words=["bored","boring","nothing to do","bored af","so bored","what should i do","entertain me","i'm bored"]
    tired_words=["tired","exhausted","sleepy","can't sleep","insomnia","drained","burned out","burnout","no energy","so tired","need sleep","want to sleep","fatigue"]
    flirty_words=["you're cute","you're pretty","kiss","hug me","date me","marry me","be mine","waifu","my girl","babe","flirt","blush","crush on you","you're hot"]
    greeting_words=["hi","hello","hey","good morning","good night","goodnight","good evening","sup","yo","hiya","howdy","what's up","wassup"]
    goodbye_words=["bye","goodbye","see you","cya","later","gotta go","leaving","going to sleep","heading out"]
    question_words=["how are you","what are you doing","are you there","you okay","what's your name","who are you","tell me about yourself"]
    joke_words=["tell me a joke","make me laugh","say something funny","joke please","i need a laugh"]
    help_words=["help me","i need help","can you help","assist me","support me"]
    confused_words=["confused","don't understand","what do you mean","huh","what","i don't get it","explain","clarify"]
    shocked_words=["wow","omg","oh my god","no way","seriously","what the","are you kidding","unbelievable","shocking","surprised"]
    for word in greeting_words:
        if ml==word or ml.startswith(word+" ") or ml.startswith(word+"!") or ml.startswith(word+","):
            return "happy"
    for word in goodbye_words:
        if word in ml:
            return "caring"
    for word in joke_words:
        if word in ml:
            return "playful"
    for word in question_words:
        if word in ml:
            return "curious"
    for word in flirty_words:
        if word in ml:
            return "shy"
    for word in shocked_words:
        if word in ml:
            return "shocked"
    for word in confused_words:
        if word in ml:
            return "confused"
    for word in sad_words:
        if word in ml and not has_negation(ml,word):
            return "comfort"
    for word in angry_words:
        if word in ml and not has_negation(ml,word):
            return "worried"
    for word in anxious_words:
        if word in ml:
            return "caring"
    for word in tired_words:
        if word in ml:
            return "sleepy"
    for word in proud_words:
        if word in ml:
            return "proud"
    for word in happy_words:
        if word in ml and not has_negation(ml,word):
            return "excited"
    for word in love_words:
        if word in ml:
            return "loving"
    for word in bored_words:
        if word in ml:
            return "playful"
    for word in help_words:
        if word in ml:
            return "determined"
    return "neutral"
def detect_response_emotion(text):
    ml=text.lower()
    if any(w in ml for w in ["sorry","i understand","that's tough","here for you","it's okay"]):
        return "comfort"
    if any(w in ml for w in ["amazing","fantastic","awesome","great job","well done","congratulations"]):
        return "excited"
    if any(w in ml for w in ["proud of you","impressive","you did it","excellent"]):
        return "proud"
    if any(w in ml for w in ["haha","lol","funny","joke","laugh"]):
        return "playful"
    if any(w in ml for w in ["careful","warning","watch out","be safe"]):
        return "worried"
    if any(w in ml for w in ["interesting","hmm","let me think","curious"]):
        return "curious"
    if any(w in ml for w in ["love","care about","always here","support"]):
        return "loving"
    if any(w in ml for w in ["rest","sleep","take care","relax"]):
        return "caring"
    if any(w in ml for w in ["let's do","ready","go for it","challenge"]):
        return "determined"
    if any(w in ml for w in ["wow","surprised","unexpected","shocking"]):
        return "shocked"
    if any(w in ml for w in ["thank","grateful","appreciate"]):
        return "grateful"
    if any(w in ml for w in ["blush","shy","embarrassed"]):
        return "shy"
    if any(w in ml for w in ["happy","glad","yay","nice"]):
        return "happy"
    return "happy"
class EdgeTTSWorker(QThread):
    audio_ready=pyqtSignal(str)
    tts_error=pyqtSignal(str)
    def __init__(self,text,emotion="neutral",volume=1.0):
        super().__init__()
        self.text=text
        self.emotion=emotion
        self.volume=volume
    def run(self):
        if not HAS_EDGE_TTS:
            self.tts_error.emit("Edge TTS not available")
            return
        try:
            voice_key=EMOTION_VOICE_MAP.get(self.emotion,"default")
            profile=VOICE_PROFILES.get(voice_key,VOICE_PROFILES["default"])
            clean_text=re.sub(r'[^\w\s.,!?\'"()-]','',self.text)
            clean_text=re.sub(r'\s+',' ',clean_text).strip()
            if not clean_text:
                return
            temp_file=os.path.join(tempfile.gettempdir(),f"nova_tts_{int(time.time()*1000)}_{random.randint(1000,9999)}.mp3")
            async def generate():
                communicate=edge_tts.Communicate(clean_text,voice=profile["name"],rate=profile["rate"],pitch=profile["pitch"])
                await communicate.save(temp_file)
            loop=asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(generate())
            finally:
                loop.close()
            if os.path.exists(temp_file) and os.path.getsize(temp_file)>0:
                self.audio_ready.emit(temp_file)
            else:
                self.tts_error.emit("Audio file empty or missing")
        except Exception as e:
            self.tts_error.emit(str(e)[:80])
def get_legacy_tts_engine():
    global tts_engine
    if tts_engine is None and HAS_TTS:
        try:
            tts_engine=pyttsx3.init()
            tts_engine.setProperty('rate',170)
            tts_engine.setProperty('volume',0.9)
            voices=tts_engine.getProperty('voices')
            for voice in voices:
                if 'zira' in voice.name.lower() or 'female' in voice.name.lower():
                    tts_engine.setProperty('voice',voice.id)
                    break
        except Exception:
            tts_engine=None
    return tts_engine
def speak_legacy(text,volume=1.0):
    if not HAS_TTS:
        return
    def _speak():
        with tts_lock:
            engine=get_legacy_tts_engine()
            if engine:
                try:
                    engine.setProperty('volume',min(1.0,max(0.0,volume)))
                    clean_text=re.sub(r'[^\w\s.,!?\'"()-]','',text)
                    clean_text=re.sub(r'\s+',' ',clean_text).strip()
                    if clean_text:
                        engine.say(clean_text)
                        engine.runAndWait()
                except Exception:
                    pass
    threading.Thread(target=_speak,daemon=True).start()
class ScreenAnalysisWorker(QThread):
    analysis_complete=pyqtSignal(str,str)
    def __init__(self,mode="general",question=""):
        super().__init__()
        self.mode=mode
        self.question=question
    def run(self):
        player_name=get_player_name()
        try:
            if not HAS_SCREENSHOT:
                self.analysis_complete.emit("I need pyautogui and Pillow to see your screen! Install them first.","worried")
                return
            screenshot=capture_screen()
            if screenshot is None:
                self.analysis_complete.emit("I could not capture your screen. Make sure pyautogui and Pillow are installed!","worried")
                return
            client=get_gemini_client()
            if not client:
                self.analysis_complete.emit("I need an API key to analyze your screen!","worried")
                return
            if self.mode=="code":
                prompt=f"You are Nova, a helpful AI companion for {player_name}. Analyze this screenshot focusing on any code visible. Explain what the code does, identify any bugs or improvements, and be helpful and concise. Respond naturally like a caring friend who is also a great developer."
            elif self.mode=="help":
                prompt=f"You are Nova, a helpful AI companion for {player_name}. The user needs help with what is on their screen. Analyze it and provide helpful guidance. Question: {self.question}"
            else:
                prompt=f"You are Nova, a helpful AI companion for {player_name}. Describe what you see on screen and provide helpful observations. Be friendly, concise, and natural. If you see code, briefly explain it. If you see a game, comment on it positively."
            import PIL.Image
            img_bytes=io.BytesIO()
            screenshot.save(img_bytes,format='PNG')
            img_bytes.seek(0)
            pil_image=PIL.Image.open(img_bytes)
            for model in ["gemini-2.5-flash","gemini-2.0-flash-exp","gemini-2.0-flash","gemini-1.5-flash"]:
                try:
                    response=client.models.generate_content(model=model,contents=[prompt,pil_image])
                    if response and response.text:
                        result=response.text.strip()
                        emotion=detect_response_emotion(result)
                        self.analysis_complete.emit(result,emotion)
                        return
                except Exception:
                    continue
            self.analysis_complete.emit("I had trouble analyzing the screen. Please try again!","worried")
        except Exception as e:
            self.analysis_complete.emit(f"Screen analysis error: {str(e)[:100]}","worried")
class AIWorker(QThread):
    response_received=pyqtSignal(str)
    voice_ready=pyqtSignal(str,str)
    action_detected=pyqtSignal(dict)
    error_occurred=pyqtSignal(str,str)
    def __init__(self,message,user_emotion="neutral"):
        super().__init__()
        self.message=message
        self.user_emotion=user_emotion
    def run(self):
        try:
            player_name=get_player_name()
            emotion_guidance=""
            if self.user_emotion=="comfort":
                emotion_guidance="The user seems sad. Be warm, empathetic, and comforting."
            elif self.user_emotion=="playful":
                emotion_guidance="The user wants fun. Be playful and tell a complete funny joke with setup and punchline!"
            elif self.user_emotion=="excited":
                emotion_guidance="The user is happy! Match their positive energy!"
            elif self.user_emotion=="proud":
                emotion_guidance="The user achieved something great! Celebrate them warmly!"
            elif self.user_emotion=="worried":
                emotion_guidance="The user seems frustrated. Be calm and reassuring."
            elif self.user_emotion=="caring":
                emotion_guidance="The user seems stressed. Be gentle and reassuring."
            context=(
                f"You are Nova, a gentle, caring, and playful AI companion. "
                f"You are {player_name}'s closest friend and supportive partner. "
                f"PERSONALITY: Warm, gentle, sometimes playful, always supportive. "
                f"Speak casually like a real caring friend, not a corporate AI. "
                f"Use short natural sentences. Use emoji sparingly and only when it feels right. "
                f"IMPORTANT: If asked for a joke, tell a COMPLETE funny joke with a real setup and punchline. "
                f"Never just say hehe or laugh without delivering the full joke. Be creative and genuinely funny. "
                f"If the answer needs code, provide full working code in ```python...``` blocks. "
                f"You are deeply caring and supportive. "
                f"{emotion_guidance} "
                f"To open apps or websites use these tags: [CMD:web:url] [CMD:open:app] [CMD:folder:name]"
            )
            try:
                client=get_gemini_client()
            except Exception as e:
                self.error_occurred.emit("Client Error",f"Failed to create API client: {str(e)[:100]}")
                return
            if not client:
                self.error_occurred.emit("No API Key","I need an API key! Type /reset to configure.")
                return
            models_to_try=["gemini-2.5-flash","gemini-2.0-flash","gemini-1.5-flash","gemini-pro"]
            last_error="Unknown error"
            for model in models_to_try:
                try:
                    response=client.models.generate_content(model=model,contents=context+"\n\nUser: "+self.message)
                    if response:
                        if hasattr(response,'text') and response.text:
                            raw=response.text.strip()
                            if raw:
                                commands=re.findall(r'\[CMD:([^\]]+)\]',raw)
                                display=re.sub(r'\s*\[CMD:[^\]]+\]\s*','',raw).strip()
                                response_emotion=detect_response_emotion(display)
                                voice_text=generate_smart_voice_text(display,player_name)
                                for cmd in commands:
                                    parts=cmd.split(":",1)
                                    if len(parts)>=2:
                                        self.action_detected.emit({"type":parts[0],"target":parts[1]})
                                self.response_received.emit(display)
                                self.voice_ready.emit(voice_text,response_emotion)
                                return
                            else:
                                last_error="Empty response text"
                        else:
                            last_error="No text in response"
                    else:
                        last_error="No response object returned"
                except Exception as e:
                    last_error=str(e)
                    error_lower=last_error.lower()
                    if "quota" in error_lower or "exhausted" in error_lower or "429" in last_error:
                        self.error_occurred.emit("Quota Exhausted",f"API limit reached!\n\n1. Wait 24 hours\n2. Get a new key at aistudio.google.com\n3. Type /reset\n\n{last_error[:100]}")
                        return
                    elif "api_key" in error_lower or "invalid" in error_lower or "403" in last_error:
                        self.error_occurred.emit("Invalid API Key",f"Your key is not working!\n\nType /reset to fix it.\n\n{last_error[:100]}")
                        return
                    elif "rate" in error_lower or "limit" in error_lower:
                        self.error_occurred.emit("Rate Limited",f"Too many requests! Wait a minute.\n\n{last_error[:100]}")
                        return
                    elif "network" in error_lower or "connection" in error_lower:
                        self.error_occurred.emit("Network Error",f"No internet connection?\n\n{last_error[:100]}")
                        return
                    elif "blocked" in error_lower or "safety" in error_lower:
                        self.error_occurred.emit("Content Blocked",f"Content was filtered.\n\n{last_error[:100]}")
                        return
                    continue
            self.error_occurred.emit("All Models Failed",f"Tried all available models.\n\nLast error: {last_error[:150]}\n\nType /reset or check your internet connection.")
        except Exception as e:
            self.error_occurred.emit("Critical Error",f"Worker crashed: {str(e)[:150]}")
class VoiceWorker(QThread):
    voice_result=pyqtSignal(str)
    voice_error=pyqtSignal(str)
    voice_status=pyqtSignal(str)
    def __init__(self,continuous=False):
        super().__init__()
        self.continuous=continuous
        self._running=True
    def stop(self):
        self._running=False
    def run(self):
        if not HAS_SPEECH:
            self.voice_error.emit("Speech recognition is not available!")
            return
        try:
            r=sr.Recognizer()
            r.energy_threshold=300
            r.dynamic_energy_threshold=True
            r.pause_threshold=1.0
            while self._running:
                try:
                    self.voice_status.emit("Listening... speak now!")
                    with sr.Microphone() as source:
                        r.adjust_for_ambient_noise(source,duration=0.5)
                        audio=r.listen(source,timeout=8,phrase_time_limit=15)
                    self.voice_status.emit("Processing your speech...")
                    text=r.recognize_google(audio)
                    if text and text.strip():
                        self.voice_result.emit(text.strip())
                    if not self.continuous:
                        break
                except sr.WaitTimeoutError:
                    if not self.continuous:
                        self.voice_error.emit("No speech detected. Try again!")
                        break
                except sr.UnknownValueError:
                    if not self.continuous:
                        self.voice_error.emit("Could not understand. Please speak clearly!")
                        break
                except sr.RequestError as e:
                    self.voice_error.emit(f"Speech service error: {str(e)[:40]}")
                    break
        except Exception as e:
            self.voice_error.emit(f"Microphone error: {str(e)[:40]}")
class SetupWindow(QDialog):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nova — Setup")
        self.setFixedSize(600,540)
        self.setWindowFlags(Qt.FramelessWindowHint|Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.api_key=""
        self._drag_pos=None
        self._build_ui()
    def _build_ui(self):
        outer=QVBoxLayout()
        outer.setContentsMargins(0,0,0,0)
        self.container=QFrame()
        self.container.setObjectName("setupContainer")
        self.container.setStyleSheet(f"""
            QFrame#setupContainer {{
                background-color: {PALETTE['bg_secondary']};
                border: 1px solid {PALETTE['border']};
                border-radius: 22px;
            }}
        """)
        shadow=QGraphicsDropShadowEffect()
        shadow.setBlurRadius(50)
        shadow.setColor(QColor(0,0,0,180))
        shadow.setOffset(0,8)
        self.container.setGraphicsEffect(shadow)
        layout=QVBoxLayout(self.container)
        layout.setContentsMargins(48,48,48,48)
        layout.setSpacing(24)
        title_row=QHBoxLayout()
        title=QLabel("Nova")
        title.setStyleSheet(f"color: {PALETTE['text_primary']}; font-family: 'Segoe UI'; font-weight: 700; font-size: {FONT_SIZES['title']}px; border: none; background: transparent;")
        badge=QLabel("Setup")
        badge.setStyleSheet(f"color: {PALETTE['accent_soft']}; background: {PALETTE['accent_dim']}; border: 1px solid {PALETTE['accent_border']}; border-radius: 10px; font-size: {FONT_SIZES['badge']}px; font-family: 'Segoe UI'; font-weight: 600; padding: 5px 14px;")
        title_row.addWidget(title)
        title_row.addWidget(badge)
        title_row.addStretch()
        subtitle=QLabel("Connect your Gemini API key to activate Nova.")
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet(f"color: {PALETTE['text_secondary']}; font-family: 'Segoe UI'; font-size: {FONT_SIZES['subtitle']}px; border: none; background: transparent;")
        divider=QFrame()
        divider.setFixedHeight(1)
        divider.setStyleSheet(f"background: {PALETTE['border_subtle']}; border: none;")
        key_label=QLabel("Gemini API Key")
        key_label.setStyleSheet(f"color: {PALETTE['text_secondary']}; font-family: 'Segoe UI'; font-size: {FONT_SIZES['label']}px; font-weight: 600; border: none; background: transparent;")
        self.key_input=QLineEdit()
        self.key_input.setPlaceholderText("Paste your API key here...")
        self.key_input.setEchoMode(QLineEdit.Password)
        self.key_input.setFixedHeight(60)
        self.key_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {PALETTE['bg_input']};
                border: 1px solid {PALETTE['border']};
                border-radius: 14px;
                color: {PALETTE['text_primary']};
                padding: 0px 22px;
                font-family: 'Consolas';
                font-size: {FONT_SIZES['input']}px;
            }}
            QLineEdit:focus {{
                border: 1px solid {PALETTE['accent_border']};
                background-color: {PALETTE['bg_card']};
            }}
        """)
        name_label=QLabel("Your Name")
        name_label.setStyleSheet(f"color: {PALETTE['text_secondary']}; font-family: 'Segoe UI'; font-size: {FONT_SIZES['label']}px; font-weight: 600; border: none; background: transparent;")
        self.name_input=QLineEdit()
        self.name_input.setPlaceholderText("What should Nova call you?")
        self.name_input.setFixedHeight(60)
        self.name_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {PALETTE['bg_input']};
                border: 1px solid {PALETTE['border']};
                border-radius: 14px;
                color: {PALETTE['text_primary']};
                padding: 0px 22px;
                font-family: 'Segoe UI';
                font-size: {FONT_SIZES['input']}px;
            }}
            QLineEdit:focus {{
                border: 1px solid {PALETTE['accent_border']};
                background-color: {PALETTE['bg_card']};
            }}
        """)
        link_label=QLabel(f'<a href="https://aistudio.google.com/app/apikey" style="color: {PALETTE["accent_soft"]}; text-decoration: none; font-size: {FONT_SIZES["body_small"]}px;">Get your free Gemini API key →</a>')
        link_label.setOpenExternalLinks(True)
        link_label.setStyleSheet("background: transparent; border: none;")
        self.status_label=QLabel("")
        self.status_label.setFixedHeight(28)
        self.status_label.setStyleSheet(f"color: {PALETTE['danger']}; font-family: 'Segoe UI'; font-size: {FONT_SIZES['body_small']}px; background: transparent; border: none;")
        start_btn=QPushButton("Activate Nova")
        start_btn.setFixedHeight(62)
        start_btn.setCursor(Qt.PointingHandCursor)
        start_btn.setStyleSheet(f"""
            QPushButton {{
                background: {PALETTE['accent']};
                border: none;
                border-radius: 16px;
                color: #FFFFFF;
                font-family: 'Segoe UI';
                font-size: {FONT_SIZES['button']}px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background: {PALETTE['accent_soft']};
            }}
            QPushButton:pressed {{
                background: {PALETTE['accent']};
            }}
        """)
        start_btn.clicked.connect(self._validate_and_save)
        self.key_input.returnPressed.connect(self._validate_and_save)
        layout.addLayout(title_row)
        layout.addWidget(subtitle)
        layout.addWidget(divider)
        layout.addWidget(key_label)
        layout.addWidget(self.key_input)
        layout.addWidget(name_label)
        layout.addWidget(self.name_input)
        layout.addWidget(link_label)
        layout.addStretch()
        layout.addWidget(self.status_label)
        layout.addWidget(start_btn)
        outer.addWidget(self.container)
        self.setLayout(outer)
    def _validate_and_save(self):
        key=self.key_input.text().strip()
        name=self.name_input.text().strip() or "Friend"
        if not key:
            self.status_label.setText("Please enter your API key.")
            self.status_label.setStyleSheet(f"color: {PALETTE['danger']}; font-family: 'Segoe UI'; font-size: 13px; background: transparent; border: none;")
            return
        if len(key)<20:
            self.status_label.setText("That key looks too short. Please double-check it.")
            self.status_label.setStyleSheet(f"color: {PALETTE['danger']}; font-family: 'Segoe UI'; font-size: 13px; background: transparent; border: none;")
            return
        self.status_label.setText("Validating your key...")
        self.status_label.setStyleSheet(f"color: {PALETTE['accent_soft']}; font-family: 'Segoe UI'; font-size: 13px; background: transparent; border: none;")
        QApplication.processEvents()
        models_to_try=["gemini-2.5-flash","gemini-2.0-flash-exp","gemini-2.0-flash","gemini-1.5-flash","gemini-pro"]
        for model in models_to_try:
            try:
                test_client=genai.Client(api_key=key)
                response=test_client.models.generate_content(model=model,contents="Hi")
                if response and response.text:
                    config=load_config()
                    config["api_key"]=key
                    config["player_name"]=name
                    config["preferred_model"]=model
                    save_config(config)
                    self.api_key=key
                    self.accept()
                    return
            except Exception as e:
                error_str=str(e).lower()
                if "quota" in error_str or "exhausted" in error_str or "rate" in error_str:
                    config=load_config()
                    config["api_key"]=key
                    config["player_name"]=name
                    save_config(config)
                    self.api_key=key
                    self.accept()
                    return
                continue
        self.status_label.setText("Could not validate. Saving anyway — check your key later.")
        self.status_label.setStyleSheet(f"color: {PALETTE['warning']}; font-family: 'Segoe UI'; font-size: 13px; background: transparent; border: none;")
        config=load_config()
        config["api_key"]=key
        config["player_name"]=name
        save_config(config)
        self.api_key=key
        QTimer.singleShot(1800,self.accept)
    def mousePressEvent(self,event):
        if event.button()==Qt.LeftButton:
            self._drag_pos=event.globalPos()-self.frameGeometry().topLeft()
    def mouseMoveEvent(self,event):
        if self._drag_pos and event.buttons()==Qt.LeftButton:
            self.move(event.globalPos()-self._drag_pos)
    def mouseReleaseEvent(self,event):
        self._drag_pos=None
class HydrationTracker:
    def __init__(self,companion_ref):
        self.companion=companion_ref
        self.glasses=0
        self.goal=8
        self.last_reminder=time.time()
        self.reminder_timer=QTimer()
        self.reminder_timer.timeout.connect(self._remind)
        self.reminder_timer.start(2700000)
    def log(self):
        self.glasses+=1
        self.last_reminder=time.time()
        player_name=get_player_name()
        if self.glasses>=self.goal:
            msg=f"Glass {self.glasses} of {self.goal} done! Hydration goal reached today, {player_name}!"
            self.companion.set_emotion_with_status("excited",msg,duration=6000)
        else:
            msg=f"Glass {self.glasses} of {self.goal} logged! Keep it up, {player_name}!"
            self.companion.set_emotion_with_status("happy",msg,duration=5000)
        return msg
    def _remind(self):
        if time.time()-self.last_reminder>2700:
            player_name=get_player_name()
            msg=f"Hey {player_name}! Time for some water!"
            self.companion.set_emotion_with_status("caring",msg,duration=6000)
            self.companion.chat_bubble._speak_now(msg,"caring")
    def get_status(self):
        return f"{self.glasses} of {self.goal} glasses today"
class ScreenTimeTracker:
    def __init__(self,companion_ref):
        self.companion=companion_ref
        self.session_start=time.time()
        self.last_warning_level=0
        self.distraction_start=None
        self.current_distraction=None
        self.distraction_warning_level=0
        self._last_idle_notify=0
        self.check_timer=QTimer()
        self.check_timer.timeout.connect(self._check)
        self.check_timer.start(60000)
    def _check(self):
        elapsed=(time.time()-self.session_start)/60
        for i,warning in enumerate(SCREEN_TIME_WARNINGS):
            if elapsed>=warning["minutes"] and self.last_warning_level<=i:
                self.last_warning_level=i+1
                self.companion.set_emotion_with_status(warning["emotion"],warning["text"],duration=15000)
                if warning.get("speak",True):
                    if time.time()-getattr(self,'_last_warn_speak',0)>300:
                        self._last_warn_speak=time.time()
                        self.companion.chat_bubble._speak_now(warning["text"],warning["emotion"])
                break
    def check_distraction(self,app_key):
        if app_key in DISTRACTION_APPS:
            if self.current_distraction!=app_key:
                self.current_distraction=app_key
                self.distraction_start=time.time()
                self.distraction_warning_level=0
            else:
                elapsed=(time.time()-self.distraction_start)/60
                for i,warning in enumerate(DISTRACTION_WARNINGS):
                    if elapsed>=warning["minutes"] and self.distraction_warning_level<=i:
                        self.distraction_warning_level=i+1
                        self.companion.set_emotion_with_status(warning["emotion"],warning["text"],duration=12000)
                        if warning.get("speak",True):
                            if time.time()-getattr(self,'_last_distract_speak',0)>300:
                                self._last_distract_speak=time.time()
                                self.companion.chat_bubble._speak_now(warning["text"],warning["emotion"])
                        break
        else:
            self.current_distraction=None
            self.distraction_start=None
            self.distraction_warning_level=0
    def take_break(self):
        self.session_start=time.time()
        self.last_warning_level=0
        self.distraction_start=None
        self.current_distraction=None
        self.distraction_warning_level=0
    def get_session_time(self):
        elapsed=int((time.time()-self.session_start)/60)
        hours=elapsed//60
        mins=elapsed%60
        if hours>0:
            return f"{hours}h {mins}m this session"
        return f"{mins}m this session"
class PomodoroWindow(QWidget):
    def __init__(self,companion_ref=None,parent=None):
        super().__init__(parent)
        self.companion_ref=companion_ref
        self.setWindowFlags(Qt.FramelessWindowHint|Qt.Tool|Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(360,290)
        self._drag_pos=None
        self.remaining=0
        self.running=False
        self.default_minutes=25
        self.tick_timer=QTimer()
        self.tick_timer.timeout.connect(self._tick)
        self._build_ui()
        screen=QApplication.primaryScreen().geometry()
        self.move(int(screen.width()/2-180),60)
    def _build_ui(self):
        main_lay=QVBoxLayout()
        main_lay.setContentsMargins(0,0,0,0)
        self.container=QFrame()
        self.container.setObjectName("pomContainer")
        self.container.setStyleSheet(f"""
            QFrame#pomContainer {{
                background-color: {PALETTE['bg_secondary']};
                border: 1px solid {PALETTE['border']};
                border-radius: 18px;
            }}
        """)
        shadow=QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setColor(QColor(0,0,0,160))
        shadow.setOffset(0,6)
        self.container.setGraphicsEffect(shadow)
        inner=QVBoxLayout(self.container)
        inner.setContentsMargins(28,22,28,24)
        inner.setSpacing(14)
        header=QHBoxLayout()
        title=QLabel("Pomodoro")
        title.setStyleSheet(f"color: {PALETTE['text_primary']}; font-family: 'Segoe UI'; font-weight: 700; font-size: 18px; border: none; background: transparent;")
        close_btn=QPushButton("✕")
        close_btn.setFixedSize(30,30)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                color: {PALETTE['text_muted']};
                border: none;
                background: transparent;
                font-size: 16px;
                font-weight: bold;
                border-radius: 15px;
            }}
            QPushButton:hover {{
                color: {PALETTE['danger']};
                background: rgba(248,113,113,0.1);
            }}
        """)
        close_btn.clicked.connect(self.close_timer)
        header.addWidget(title)
        header.addStretch()
        header.addWidget(close_btn)
        self.time_label=QLabel("25:00")
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setStyleSheet(f"color: {PALETTE['text_primary']}; font-family: 'Segoe UI'; font-size: 58px; font-weight: 300; background: transparent; border: none; letter-spacing: 3px;")
        self.status_label=QLabel("Ready to focus")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet(f"color: {PALETTE['text_muted']}; font-family: 'Segoe UI'; font-size: 14px; background: transparent; border: none;")
        btn_row=QHBoxLayout()
        btn_row.setSpacing(10)
        self.start_btn=QPushButton("Start")
        self.start_btn.setFixedHeight(42)
        self.start_btn.setCursor(Qt.PointingHandCursor)
        self.start_btn.setStyleSheet(f"""
            QPushButton {{
                background: {PALETTE['accent']};
                border: none;
                border-radius: 10px;
                color: #FFFFFF;
                font-family: 'Segoe UI';
                font-size: 15px;
                font-weight: 600;
                padding: 0px 20px;
            }}
            QPushButton:hover {{
                background: {PALETTE['accent_soft']};
            }}
        """)
        self.start_btn.clicked.connect(self.start_timer)
        self.stop_btn=QPushButton("Pause")
        self.stop_btn.setFixedHeight(42)
        self.stop_btn.setCursor(Qt.PointingHandCursor)
        self.stop_btn.setStyleSheet(f"""
            QPushButton {{
                background: {PALETTE['bg_card']};
                border: 1px solid {PALETTE['border']};
                border-radius: 10px;
                color: {PALETTE['text_secondary']};
                font-family: 'Segoe UI';
                font-size: 15px;
                font-weight: 600;
                padding: 0px 20px;
            }}
            QPushButton:hover {{
                border-color: {PALETTE['warning']};
                color: {PALETTE['warning']};
            }}
        """)
        self.stop_btn.clicked.connect(self.stop_timer)
        self.stop_btn.hide()
        self.reset_btn=QPushButton("Reset")
        self.reset_btn.setFixedHeight(42)
        self.reset_btn.setCursor(Qt.PointingHandCursor)
        self.reset_btn.setStyleSheet(f"""
            QPushButton {{
                background: {PALETTE['bg_card']};
                border: 1px solid {PALETTE['border']};
                border-radius: 10px;
                color: {PALETTE['text_secondary']};
                font-family: 'Segoe UI';
                font-size: 15px;
                font-weight: 600;
                padding: 0px 20px;
            }}
            QPushButton:hover {{
                border-color: {PALETTE['text_muted']};
                color: {PALETTE['text_primary']};
            }}
        """)
        self.reset_btn.clicked.connect(self.reset_timer)
        btn_row.addWidget(self.start_btn)
        btn_row.addWidget(self.stop_btn)
        btn_row.addWidget(self.reset_btn)
        inner.addLayout(header)
        inner.addWidget(self.time_label)
        inner.addWidget(self.status_label)
        inner.addLayout(btn_row)
        main_lay.addWidget(self.container)
        self.setLayout(main_lay)
    def start_timer(self):
        if self.remaining<=0:
            self.remaining=self.default_minutes*60
        self.running=True
        self.tick_timer.start(1000)
        self.start_btn.hide()
        self.stop_btn.show()
        self.status_label.setText("Focusing...")
        self.status_label.setStyleSheet(f"color: {PALETTE['accent_soft']}; font-family: 'Segoe UI'; font-size: 14px; background: transparent; border: none;")
        self._update_display()
        if self.companion_ref:
            player_name=get_player_name()
            self.companion_ref.set_emotion_with_status("determined",f"{self.default_minutes} minute focus started!",duration=0)
    def stop_timer(self):
        self.running=False
        self.tick_timer.stop()
        self.stop_btn.hide()
        self.start_btn.show()
        self.start_btn.setText("Resume")
        self.status_label.setText("Paused")
        self.status_label.setStyleSheet(f"color: {PALETTE['text_muted']}; font-family: 'Segoe UI'; font-size: 14px; background: transparent; border: none;")
        if self.companion_ref:
            self.companion_ref.set_emotion_with_status("watching","Timer paused",duration=5000)
    def reset_timer(self):
        self.running=False
        self.tick_timer.stop()
        self.remaining=self.default_minutes*60
        self.stop_btn.hide()
        self.start_btn.show()
        self.start_btn.setText("Start")
        self.status_label.setText("Ready to focus")
        self.status_label.setStyleSheet(f"color: {PALETTE['text_muted']}; font-family: 'Segoe UI'; font-size: 14px; background: transparent; border: none;")
        self._update_display()
    def close_timer(self):
        self.stop_timer()
        self.hide()
    def _tick(self):
        self.remaining-=1
        self._update_display()
        if self.remaining<=0:
            self.tick_timer.stop()
            self.running=False
            self.time_label.setText("00:00")
            self.status_label.setText("Done! Take a break.")
            self.status_label.setStyleSheet(f"color: {PALETTE['success']}; font-family: 'Segoe UI'; font-size: 14px; background: transparent; border: none;")
            self.container.setStyleSheet(f"""
                QFrame#pomContainer {{
                    background-color: {PALETTE['bg_secondary']};
                    border: 1px solid rgba(74,222,128,0.35);
                    border-radius: 18px;
                }}
            """)
            self.stop_btn.hide()
            self.start_btn.show()
            self.start_btn.setText("Start")
            if self.companion_ref:
                player_name=get_player_name()
                msg=f"Timer done! You earned a break, {player_name}!"
                self.companion_ref.set_emotion_with_status("excited",msg,duration=10000)
                self.companion_ref.chat_bubble._speak_now(msg,"excited")
            try:
                import winsound
                winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
            except Exception:
                pass
        elif self.remaining%300==0:
            if self.companion_ref:
                self.companion_ref.update_floating_status("determined",f"{self.remaining//60} min left")
    def _update_display(self):
        self.time_label.setText(f"{self.remaining//60:02d}:{self.remaining%60:02d}")
    def show_timer(self):
        self.container.setStyleSheet(f"""
            QFrame#pomContainer {{
                background-color: {PALETTE['bg_secondary']};
                border: 1px solid {PALETTE['border']};
                border-radius: 18px;
            }}
        """)
        if not self.running and self.remaining<=0:
            self.remaining=self.default_minutes*60
            self._update_display()
            self.status_label.setText("Ready to focus")
            self.status_label.setStyleSheet(f"color: {PALETTE['text_muted']}; font-family: 'Segoe UI'; font-size: 14px; background: transparent; border: none;")
            self.start_btn.setText("Start")
        self.show()
        self.raise_()
    def mousePressEvent(self,event):
        if event.button()==Qt.LeftButton:
            self._drag_pos=event.globalPos()-self.frameGeometry().topLeft()
    def mouseMoveEvent(self,event):
        if self._drag_pos and event.buttons()==Qt.LeftButton:
            self.move(event.globalPos()-self._drag_pos)
    def mouseReleaseEvent(self,event):
        self._drag_pos=None
class CodePanel(QWidget):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint|Qt.Tool|Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedWidth(540)
        self._drag_pos=None
        self._all_code=""
        self._build_ui()
    def _build_ui(self):
        main_lay=QVBoxLayout()
        main_lay.setContentsMargins(0,0,0,0)
        self.container=QFrame()
        self.container.setObjectName("codeContainer")
        self.container.setStyleSheet(f"""
            QFrame#codeContainer {{
                background-color: {PALETTE['bg_secondary']};
                border: 1px solid {PALETTE['border']};
                border-radius: 18px;
            }}
        """)
        shadow=QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setColor(QColor(0,0,0,160))
        shadow.setOffset(0,6)
        self.container.setGraphicsEffect(shadow)
        inner=QVBoxLayout(self.container)
        inner.setContentsMargins(20,18,20,20)
        inner.setSpacing(14)
        header=QHBoxLayout()
        title=QLabel("Code Output")
        title.setStyleSheet(f"color: {PALETTE['text_primary']}; font-family: 'Segoe UI'; font-weight: 700; font-size: 16px; background: transparent; border: none;")
        close_btn=QPushButton("✕")
        close_btn.setFixedSize(30,30)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                color: {PALETTE['text_muted']};
                border: none;
                background: transparent;
                font-size: 16px;
                font-weight: bold;
                border-radius: 15px;
            }}
            QPushButton:hover {{
                color: {PALETTE['danger']};
                background: rgba(248,113,113,0.1);
            }}
        """)
        close_btn.clicked.connect(self.hide)
        header.addWidget(title)
        header.addStretch()
        header.addWidget(close_btn)
        self.code_browser=QTextBrowser()
        self.code_browser.setFont(QFont("Consolas",15))
        self.code_browser.setStyleSheet(f"""
            QTextBrowser {{
                background-color: {PALETTE['bg_primary']};
                border: 1px solid {PALETTE['border_subtle']};
                border-radius: 12px;
                color: {PALETTE['text_primary']};
                font-family: Consolas;
                font-size: 15px;
                padding: 14px;
            }}
            QScrollBar:vertical {{
                background: transparent;
                width: 6px;
                border-radius: 3px;
            }}
            QScrollBar::handle:vertical {{
                background: {PALETTE['border']};
                border-radius: 3px;
                min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {PALETTE['text_muted']};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0;
            }}
        """)
        self.copy_btn=QPushButton("Copy All Code")
        self.copy_btn.setFixedHeight(44)
        self.copy_btn.setCursor(Qt.PointingHandCursor)
        self.copy_btn.setStyleSheet(f"""
            QPushButton {{
                background: {PALETTE['bg_card']};
                border: 1px solid {PALETTE['border']};
                border-radius: 10px;
                color: {PALETTE['text_secondary']};
                font-family: 'Segoe UI';
                font-size: 14px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                border-color: {PALETTE['accent_border']};
                color: {PALETTE['accent_soft']};
            }}
        """)
        self.copy_btn.clicked.connect(self._copy_all)
        inner.addLayout(header)
        inner.addWidget(self.code_browser)
        inner.addWidget(self.copy_btn)
        main_lay.addWidget(self.container)
        self.setLayout(main_lay)
    def show_code(self,code_blocks,chat_x,chat_y,chat_height):
        self._all_code="\n\n".join(code for _,code in code_blocks)
        html=""
        for lang,code in code_blocks:
            escaped=code.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
            highlighted=self._syntax_highlight(escaped)
            html+=(
                f"<div style='background:{PALETTE['bg_primary']}; border:1px solid {PALETTE['border_subtle']}; border-radius:10px; margin:8px 0;'>"
                f"<div style='background:{PALETTE['bg_card']}; padding:10px 16px; border-bottom:1px solid {PALETTE['border_subtle']}; border-radius:10px 10px 0 0;'>"
                f"<span style='color:{PALETTE['accent_soft']}; font-size:13px; font-weight:600; font-family:Consolas;'>{lang or 'code'}</span></div>"
                f"<pre style='padding:16px; margin:0; white-space:pre-wrap; word-wrap:break-word; line-height:1.7; font-family:Consolas; font-size:15px; color:{PALETTE['text_primary']};'>{highlighted}</pre></div>"
            )
        self.code_browser.setHtml(html)
        screen=QApplication.primaryScreen().geometry()
        target_y=chat_y+chat_height+10
        if target_y+350>screen.height():
            target_y=chat_y-350-10
        self.move(chat_x,target_y)
        total_lines=sum(code.count('\n')+1 for _,code in code_blocks)
        height=min(560,max(260,180+total_lines*26))
        self.setFixedHeight(height)
        self.show()
        self.raise_()
    def _syntax_highlight(self,code):
        code=re.sub(r'(#[^&].*?)(?=\n|$)',r"<span style='color:#6A9955;'>\1</span>",code,flags=re.MULTILINE)
        code=re.sub(r'("(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\')',r"<span style='color:#CE9178;'>\1</span>",code)
        code=re.sub(r'\b(\d+\.?\d*)\b',r"<span style='color:#B5CEA8;'>\1</span>",code)
        keywords=["def","class","import","from","return","if","elif","else","for","while","try","except","finally","with","as","lambda","pass","break","continue","and","or","not","in","is","True","False","None","self","async","await","raise","yield","global","nonlocal","del","assert","print"]
        for kw in keywords:
            code=re.sub(rf'(?<![a-zA-Z0-9_])({kw})(?![a-zA-Z0-9_])',rf"<span style='color:#569CD6;font-weight:600;'>\1</span>",code)
        code=re.sub(r'(@\w+)',r"<span style='color:#DCDCAA;'>\1</span>",code)
        return code
    def _copy_all(self):
        QApplication.clipboard().setText(self._all_code)
        self.copy_btn.setText("Copied!")
        self.copy_btn.setStyleSheet(f"""
            QPushButton {{
                background: rgba(74,222,128,0.1);
                border: 1px solid rgba(74,222,128,0.3);
                border-radius: 10px;
                color: {PALETTE['success']};
                font-family: 'Segoe UI';
                font-size: 14px;
                font-weight: 600;
            }}
        """)
        QTimer.singleShot(2000,lambda:self.copy_btn.setText("Copy All Code"))
        QTimer.singleShot(2000,lambda:self.copy_btn.setStyleSheet(f"""
            QPushButton {{
                background: {PALETTE['bg_card']};
                border: 1px solid {PALETTE['border']};
                border-radius: 10px;
                color: {PALETTE['text_secondary']};
                font-family: 'Segoe UI';
                font-size: 14px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                border-color: {PALETTE['accent_border']};
                color: {PALETTE['accent_soft']};
            }}
        """))
    def mousePressEvent(self,event):
        if event.button()==Qt.LeftButton:
            self._drag_pos=event.globalPos()-self.frameGeometry().topLeft()
    def mouseMoveEvent(self,event):
        if self._drag_pos and event.buttons()==Qt.LeftButton:
            self.move(event.globalPos()-self._drag_pos)
    def mouseReleaseEvent(self,event):
        self._drag_pos=None
class ChatBubble(QWidget):
    def __init__(self,companion_ref=None,parent=None):
        super().__init__(parent)
        self.companion_ref=companion_ref
        self.setWindowFlags(Qt.FramelessWindowHint|Qt.Tool|Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMinimumSize(500,420)
        self.setMaximumSize(1600,1100)
        self.resize(640,700)
        self._active_workers=[]
        self._drag_pos=None
        self._resize_edge=None
        self._resize_margin=8
        self._start_geo=None
        self._sound_enabled=True
        self._tts_enabled=True
        self._tts_volume=0.8
        self._current_message=""
        self._current_emotion="neutral"
        self._is_waiting_ai=False
        self._code_history=[]
        self._chat_messages=[]
        self._base_font_size=FONT_SIZES['chat_base']
        self._tts_workers=[]
        self._pending_voice_text=""
        self._pending_voice_emotion=""
        self._pending_text=""
        self._pending_emotion="neutral"
        self._learning_mode=False
        self._learning_target=""
        self._learning_stage=""
        self._learning_type=""
        self.code_panel=CodePanel()
        self.media_player=QMediaPlayer()
        self.media_player.setVolume(80)
        self.fade_in_anim=QPropertyAnimation(self,b"windowOpacity")
        self.fade_in_anim.setDuration(350)
        self.fade_in_anim.setStartValue(0.0)
        self.fade_in_anim.setEndValue(1.0)
        self.fade_in_anim.setEasingCurve(QEasingCurve.OutCubic)
        self._typing_timer=QTimer()
        self._typing_timer.timeout.connect(self._animate_typing)
        self._typing_dots=0
        self._voice_worker=None
        self._build_ui()
    def _get_scaled_font_size(self):
        w=self.width()
        if w<=560:
            return max(20,self._base_font_size-2)
        elif w<=720:
            return self._base_font_size
        elif w<=920:
            return self._base_font_size+1
        elif w<=1100:
            return self._base_font_size+2
        else:
            return self._base_font_size+3
    def set_font_size(self,size):
        self._base_font_size=max(13,min(28,size))
        self._refresh_chat_fonts()
    def _refresh_chat_fonts(self):
        font_size=self._get_scaled_font_size()
        for i in range(self.chat_layout.count()):
            item=self.chat_layout.itemAt(i)
            if item and item.widget():
                frame=item.widget()
                for label in frame.findChildren(QLabel):
                    if label.wordWrap():
                        current=label.styleSheet()
                        updated=re.sub(r'font-size:\s*\d+px',f'font-size: {font_size}px',current)
                        label.setStyleSheet(updated)
    def _build_ui(self):
        main_lay=QVBoxLayout()
        main_lay.setContentsMargins(6,6,6,6)
        self.container=QFrame()
        self.container.setObjectName("chatContainer")
        self.container.setStyleSheet(f"""
            QFrame#chatContainer {{
                background-color: {PALETTE['bg_secondary']};
                border: 1px solid {PALETTE['border']};
                border-radius: 20px;
            }}
        """)
        shadow=QGraphicsDropShadowEffect()
        shadow.setBlurRadius(50)
        shadow.setColor(QColor(0,0,0,200))
        shadow.setOffset(0,8)
        self.container.setGraphicsEffect(shadow)
        inner=QVBoxLayout(self.container)
        inner.setContentsMargins(0,0,0,0)
        inner.setSpacing(0)
        header_frame=QFrame()
        header_frame.setFixedHeight(64)
        header_frame.setStyleSheet(f"""
            QFrame {{
                background: {PALETTE['bg_primary']};
                border-top-left-radius: 20px;
                border-top-right-radius: 20px;
                border-bottom: 1px solid {PALETTE['border_subtle']};
            }}
        """)
        header=QHBoxLayout(header_frame)
        header.setContentsMargins(22,0,16,0)
        header.setSpacing(12)
        self.status_dot=QLabel("●")
        self.status_dot.setStyleSheet(f"color: {PALETTE['success']}; font-size: 14px; background: transparent; border: none;")
        header.addWidget(self.status_dot)
        self.name_label=QLabel("Nova")
        self.name_label.setStyleSheet(f"color: {PALETTE['text_primary']}; font-family: 'Segoe UI'; font-weight: 600; font-size: {FONT_SIZES['heading']}px; background: transparent; border: none;")
        header.addWidget(self.name_label)
        header.addStretch()
        tool_btn_style=f"""
            QPushButton {{
                background: transparent;
                border: 1px solid {PALETTE['border_subtle']};
                font-size: 19px;
                border-radius: 10px;
                color: {PALETTE['text_muted']};
                padding: 0px;
            }}
            QPushButton:hover {{
                background: {PALETTE['bg_card']};
                border-color: {PALETTE['border']};
                color: {PALETTE['text_secondary']};
            }}
        """
        icon_data=[("🎙","Voice Input",self._toggle_mic),("👁","Analyze Screen",lambda:self._analyze_screen("general")),("💻","Analyze Code",lambda:self._analyze_screen("code")),("⏱","Pomodoro Timer",self._show_timer),("💧","Log Water",self._log_water),("🧘","Posture Check",self._posture_check)]
        for text,tip,handler in icon_data:
            btn=QPushButton(text)
            btn.setFixedSize(44,40)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setToolTip(tip)
            btn.setStyleSheet(tool_btn_style)
            btn.clicked.connect(handler)
            header.addWidget(btn)
        self.tts_btn=QPushButton("🔊")
        self.tts_btn.setFixedSize(44,40)
        self.tts_btn.setCursor(Qt.PointingHandCursor)
        self.tts_btn.setToolTip("Toggle Voice Output")
        self._update_tts_btn_style()
        self.tts_btn.clicked.connect(self._toggle_tts)
        header.addWidget(self.tts_btn)
        font_up_btn=QPushButton("A+")
        font_up_btn.setFixedSize(40,40)
        font_up_btn.setCursor(Qt.PointingHandCursor)
        font_up_btn.setToolTip("Increase font size")
        font_up_btn.setStyleSheet(tool_btn_style+"QPushButton { font-size: 15px; font-weight: 700; }")
        font_up_btn.clicked.connect(lambda:self.set_font_size(self._base_font_size+1))
        header.addWidget(font_up_btn)
        font_down_btn=QPushButton("A-")
        font_down_btn.setFixedSize(40,40)
        font_down_btn.setCursor(Qt.PointingHandCursor)
        font_down_btn.setToolTip("Decrease font size")
        font_down_btn.setStyleSheet(tool_btn_style+"QPushButton { font-size: 15px; font-weight: 700; }")
        font_down_btn.clicked.connect(lambda:self.set_font_size(self._base_font_size-1))
        header.addWidget(font_down_btn)
        minimize_btn=QPushButton("—")
        minimize_btn.setFixedSize(36,36)
        minimize_btn.setCursor(Qt.PointingHandCursor)
        minimize_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: none;
                color: {PALETTE['text_muted']};
                font-size: 20px;
                font-weight: bold;
                border-radius: 18px;
            }}
            QPushButton:hover {{
                background: {PALETTE['bg_card']};
                color: {PALETTE['text_secondary']};
            }}
        """)
        minimize_btn.clicked.connect(self._minimize_size)
        header.addWidget(minimize_btn)
        close_btn=QPushButton("✕")
        close_btn.setFixedSize(36,36)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: none;
                color: {PALETTE['text_muted']};
                font-size: 18px;
                font-weight: bold;
                border-radius: 18px;
            }}
            QPushButton:hover {{
                background: rgba(248,113,113,0.12);
                color: {PALETTE['danger']};
            }}
        """)
        close_btn.clicked.connect(self.hide)
        header.addWidget(close_btn)
        self.scroll_area=QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setStyleSheet(f"""
            QScrollArea {{
                background: transparent;
                border: none;
            }}
            QScrollBar:vertical {{
                background: transparent;
                width: 6px;
                border-radius: 3px;
                margin: 4px;
            }}
            QScrollBar::handle:vertical {{
                background: {PALETTE['border']};
                border-radius: 3px;
                min-height: 40px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {PALETTE['text_muted']};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """)
        self.chat_widget=QWidget()
        self.chat_widget.setStyleSheet("background: transparent;")
        self.chat_layout=QVBoxLayout(self.chat_widget)
        self.chat_layout.setContentsMargins(22,22,22,22)
        self.chat_layout.setSpacing(14)
        self.chat_layout.addStretch()
        self.scroll_area.setWidget(self.chat_widget)
        self.typing_label=QLabel("")
        self.typing_label.setStyleSheet(f"color: {PALETTE['text_muted']}; font-family: 'Segoe UI'; font-size: {FONT_SIZES['body_small']}px; background: transparent; border: none; padding: 6px 22px;")
        self.typing_label.setFixedHeight(32)
        self.typing_label.hide()
        input_frame=QFrame()
        input_frame.setStyleSheet(f"""
            QFrame {{
                background: {PALETTE['bg_primary']};
                border-bottom-left-radius: 20px;
                border-bottom-right-radius: 20px;
                border-top: 1px solid {PALETTE['border_subtle']};
            }}
        """)
        input_row=QHBoxLayout(input_frame)
        input_row.setContentsMargins(18,16,18,16)
        input_row.setSpacing(14)
        self.input_field=QLineEdit()
        self.input_field.setPlaceholderText("Message Nova...  (/help for commands)")
        self.input_field.setFixedHeight(56)
        self.input_field.setStyleSheet(f"""
            QLineEdit {{
                background-color: {PALETTE['bg_input']};
                border: 1px solid {PALETTE['border']};
                border-radius: 16px;
                color: {PALETTE['text_primary']};
                padding: 0px 22px;
                font-family: 'Segoe UI';
                font-size: {FONT_SIZES['input']}px;
            }}
            QLineEdit:focus {{
                border: 1px solid {PALETTE['accent_border']};
                background-color: {PALETTE['bg_card']};
            }}
        """)
        self.input_field.returnPressed.connect(self.send_message)
        send_btn=QPushButton("↑")
        send_btn.setFixedSize(56,56)
        send_btn.setCursor(Qt.PointingHandCursor)
        send_btn.setStyleSheet(f"""
            QPushButton {{
                background: {PALETTE['accent']};
                border-radius: 16px;
                color: white;
                font-weight: bold;
                font-size: 24px;
                border: none;
            }}
            QPushButton:hover {{
                background: {PALETTE['accent_soft']};
            }}
            QPushButton:pressed {{
                background: {PALETTE['accent']};
            }}
        """)
        send_btn.clicked.connect(self.send_message)
        input_row.addWidget(self.input_field)
        input_row.addWidget(send_btn)
        inner.addWidget(header_frame)
        inner.addWidget(self.scroll_area,1)
        inner.addWidget(self.typing_label)
        inner.addWidget(input_frame)
        main_lay.addWidget(self.container)
        self.setLayout(main_lay)
        self.input_field.setFocus()
    def _update_tts_btn_style(self):
        if self._tts_enabled:
            self.tts_btn.setStyleSheet(f"""
                QPushButton {{
                    background: rgba(124,109,250,0.12);
                    border: 1px solid {PALETTE['accent_border']};
                    font-size: 15px;
                    border-radius: 8px;
                    color: {PALETTE['accent_soft']};
                    padding: 0px;
                }}
                QPushButton:hover {{
                    background: rgba(124,109,250,0.22);
                }}
            """)
        else:
            self.tts_btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    border: 1px solid {PALETTE['border_subtle']};
                    font-size: 15px;
                    border-radius: 8px;
                    color: {PALETTE['text_muted']};
                    padding: 0px;
                }}
                QPushButton:hover {{
                    background: {PALETTE['bg_card']};
                    color: {PALETTE['text_secondary']};
                }}
            """)
    def _toggle_tts(self):
        self._tts_enabled=not self._tts_enabled
        self._update_tts_btn_style()
        if self._tts_enabled:
            self.show_message("Voice output enabled!","happy")
            self._speak_now("Voice output enabled!","happy")
        else:
            self.show_message("Voice output disabled.","neutral")
    def _speak_now(self,text,emotion="neutral"):
        if not self._tts_enabled or not text or not text.strip():
            return
        clean=re.sub(r'[^\w\s.,!?\'"()-]','',text).strip()
        if not clean:
            return
        if HAS_EDGE_TTS:
            worker=EdgeTTSWorker(clean,emotion,self._tts_volume)
            worker.audio_ready.connect(self._play_audio)
            worker.tts_error.connect(self._on_tts_error)
            self._tts_workers.append(worker)
            worker.finished.connect(lambda w=worker:self._cleanup_tts_worker(w))
            worker.start()
        else:
            speak_legacy(clean,self._tts_volume)
    def _play_audio(self,file_path):
     try:
        if not os.path.exists(file_path):
            return
        if sys.platform=="win32":
            import threading
            def _play():
                try:
                    import subprocess
                    subprocess.Popen(
                        ["powershell","-c",
                         f"(New-Object Media.SoundPlayer).PlaySync() ; "
                         f"$player = New-Object System.Media.SoundPlayer ; "
                         f"Add-Type -AssemblyName presentationCore ; "
                         f"$mp = New-Object System.Windows.Media.MediaPlayer ; "
                         f"$mp.Open([uri]'{file_path}') ; "
                         f"$mp.Play() ; "
                         f"Start-Sleep -s 10"],
                        shell=False,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                except Exception:
                    pass
            threading.Thread(target=_play,daemon=True).start()
        else:
            url=QUrl.fromLocalFile(os.path.abspath(file_path))
            self.media_player.setMedia(QMediaContent(url))
            self.media_player.setVolume(int(min(1.0,self._tts_volume)*100))
            self.media_player.play()
        QTimer.singleShot(35000,lambda:self._cleanup_audio(file_path))
     except Exception:
        pass
    def _cleanup_audio(self,file_path):
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception:
            pass
    def _on_tts_error(self,error):
        if self._current_message and HAS_TTS:
            speak_legacy(self._current_message,self._tts_volume)
    def _cleanup_tts_worker(self,w):
        try:
            self._tts_workers.remove(w)
        except ValueError:
            pass
    def _add_chat_bubble(self,text,is_user=False,emotion="neutral"):
        bubble_frame=QFrame()
        bubble_frame.setStyleSheet("background: transparent; border: none;")
        bubble_layout=QHBoxLayout(bubble_frame)
        bubble_layout.setContentsMargins(0,5,0,5)
        bubble_layout.setSpacing(0)
        code_blocks=self._extract_code_blocks(text)
        clean_text=self._remove_code_blocks(text) if code_blocks else text
        msg_widget=QFrame()
        msg_layout=QVBoxLayout(msg_widget)
        msg_layout.setContentsMargins(24,18,24,18)
        msg_layout.setSpacing(10)
        font_size=self._get_scaled_font_size()
        max_w=int(self.width()*0.78)
        if is_user:
            bubble_layout.addStretch()
            msg_widget.setStyleSheet(f"""
                QFrame {{
                    background: {PALETTE['accent_dim']};
                    border: 1px solid {PALETTE['accent_border']};
                    border-radius: 20px;
                    border-bottom-right-radius: 6px;
                }}
            """)
            msg_widget.setMaximumWidth(max_w)
        else:
            msg_widget.setMaximumWidth(int(self.width()*0.88))
            color=EMOTION_STATUS_COLORS.get(emotion,PALETTE['text_secondary'])
            msg_widget.setStyleSheet(f"""
                QFrame {{
                    background: {PALETTE['bg_card']};
                    border: 1px solid {PALETTE['border_subtle']};
                    border-radius: 20px;
                    border-bottom-left-radius: 6px;
                }}
            """)
            emotion_display=EMOTION_DISPLAY_NAMES.get(emotion,"Neutral")
            sender=QLabel(f"Nova  ·  {emotion_display}")
            sender.setStyleSheet(f"color: {color}; font-family: 'Segoe UI'; font-weight: 600; font-size: {max(16,font_size-2)}px; background: transparent; border: none; padding: 0;")
            msg_layout.addWidget(sender)
        if clean_text.strip():
            text_label=QLabel(clean_text)
            text_label.setWordWrap(True)
            text_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
            text_label.setStyleSheet(f"color: {PALETTE['text_primary']}; font-family: 'Segoe UI'; font-size: {font_size}px; background: transparent; border: none; line-height: 1.7; padding: 4px 0;")
            msg_layout.addWidget(text_label)
        if code_blocks and not is_user:
            for lang,code in code_blocks:
                code_container=self._create_code_block(lang,code)
                msg_layout.addWidget(code_container)
        bubble_layout.addWidget(msg_widget)
        if not is_user:
            bubble_layout.addStretch()
        count=self.chat_layout.count()
        self.chat_layout.insertWidget(count-1,bubble_frame)
        self._chat_messages.append({"text":text,"is_user":is_user,"emotion":emotion,"time":datetime.now().strftime("%H:%M")})
        QTimer.singleShot(50,self._scroll_to_bottom)
    def _create_code_block(self,lang,code):
        container=QFrame()
        container.setStyleSheet(f"""
            QFrame {{
                background: {PALETTE['bg_primary']};
                border: 1px solid {PALETTE['border_subtle']};
                border-radius: 12px;
            }}
        """)
        lay=QVBoxLayout(container)
        lay.setContentsMargins(0,0,0,0)
        lay.setSpacing(0)
        code_header=QFrame()
        code_header.setStyleSheet(f"""
            QFrame {{
                background: {PALETTE['bg_card']};
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
                border-bottom: 1px solid {PALETTE['border_subtle']};
            }}
        """)
        header_lay=QHBoxLayout(code_header)
        header_lay.setContentsMargins(14,7,10,7)
        lang_label=QLabel(lang.upper() if lang else "CODE")
        lang_label.setStyleSheet(f"color: {PALETTE['text_muted']}; font-family: 'Consolas'; font-size: 12px; font-weight: 700; background: transparent; border: none;")
        header_lay.addWidget(lang_label)
        header_lay.addStretch()
        copy_btn=QPushButton("Copy")
        copy_btn.setFixedHeight(26)
        copy_btn.setCursor(Qt.PointingHandCursor)
        copy_btn.setStyleSheet(f"""
            QPushButton {{
                background: {PALETTE['bg_input']};
                border: 1px solid {PALETTE['border']};
                border-radius: 7px;
                color: {PALETTE['text_secondary']};
                font-size: 12px;
                padding: 0px 10px;
                font-weight: 600;
                font-family: 'Segoe UI';
            }}
            QPushButton:hover {{
                border-color: {PALETTE['accent_border']};
                color: {PALETTE['accent_soft']};
            }}
        """)
        copy_btn.clicked.connect(lambda checked,c=code:self._copy_code(c,copy_btn))
        header_lay.addWidget(copy_btn)
        lay.addWidget(code_header)
        code_label=QLabel(code)
        code_label.setWordWrap(True)
        code_label.setTextInteractionFlags(Qt.TextSelectableByMouse|Qt.TextSelectableByKeyboard)
        code_label.setStyleSheet(f"""
            QLabel {{
                background: {PALETTE['bg_primary']};
                color: {PALETTE['text_primary']};
                font-family: 'Consolas', monospace;
                font-size: 14px;
                border: none;
                padding: 14px 16px;
                border-bottom-left-radius: 12px;
                border-bottom-right-radius: 12px;
                line-height: 1.6;
            }}
        """)
        lay.addWidget(code_label)
        return container
    def _copy_code(self,code,btn):
        QApplication.clipboard().setText(code)
        original_text=btn.text()
        btn.setText("Copied!")
        btn.setStyleSheet(f"""
            QPushButton {{
                background: rgba(74,222,128,0.1);
                border: 1px solid rgba(74,222,128,0.3);
                border-radius: 7px;
                color: {PALETTE['success']};
                font-size: 12px;
                padding: 0px 10px;
                font-weight: 600;
                font-family: 'Segoe UI';
            }}
        """)
        QTimer.singleShot(2000,lambda:self._reset_copy_btn(btn,original_text))
    def _reset_copy_btn(self,btn,original_text):
        try:
            btn.setText(original_text)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {PALETTE['bg_input']};
                    border: 1px solid {PALETTE['border']};
                    border-radius: 7px;
                    color: {PALETTE['text_secondary']};
                    font-size: 12px;
                    padding: 0px 10px;
                    font-weight: 600;
                    font-family: 'Segoe UI';
                }}
                QPushButton:hover {{
                    border-color: {PALETTE['accent_border']};
                    color: {PALETTE['accent_soft']};
                }}
            """)
        except RuntimeError:
            pass
    def _scroll_to_bottom(self):
        sb=self.scroll_area.verticalScrollBar()
        sb.setValue(sb.maximum())
    def _minimize_size(self):
        if self.height()>500:
            self.resize(self.width(),400)
        else:
            self.resize(self.width(),700)
    def show_chat(self):
        if self.companion_ref:
            geo=self.companion_ref.frameGeometry()
            screen=QApplication.primaryScreen().geometry()
            bx=geo.left()-self.width()-16
            if bx<10:
                bx=geo.right()+16
            if bx+self.width()>screen.width():
                bx=screen.width()-self.width()-10
            by=geo.top()-40
            if by+self.height()>screen.height():
                by=screen.height()-self.height()-20
            if by<10:
                by=10
            self.move(bx,by)
        self.setWindowOpacity(0.0)
        self.show()
        self.raise_()
        self.fade_in_anim.start()
        self.input_field.setFocus()
    def show_message(self,text,emotion="neutral"):
        self._current_message=text
        self._current_emotion=emotion
        code_blocks=self._extract_code_blocks(text)
        if code_blocks:
            self._store_code(code_blocks)
        self._add_chat_bubble(text,is_user=False,emotion=emotion)
        color=EMOTION_STATUS_COLORS.get(emotion,PALETTE['text_secondary'])
        self.name_label.setStyleSheet(f"color: {color}; font-family: 'Segoe UI'; font-weight: 600; font-size: 16px; background: transparent; border: none;")
    def show_message_and_speak(self,text,voice_text,emotion="neutral"):
        self.show_message(text,emotion)
        if voice_text:
            self._speak_now(voice_text,emotion)
    def _store_code(self,code_blocks):
        self._code_history.append({"time":datetime.now().strftime("%H:%M"),"blocks":code_blocks})
        if len(self._code_history)>10:
            self._code_history=self._code_history[-10:]
    def get_code_history(self):
        return self._code_history
    def show_history_code(self,index):
        if 0<=index<len(self._code_history):
            if not self.isVisible():
                self.show_chat()
            blocks=self._code_history[index]["blocks"]
            code_text="\n\n".join([f"```{lang}\n{code}\n```" for lang,code in blocks])
            self._add_chat_bubble(f"Code from {self._code_history[index]['time']}:\n{code_text}",is_user=False,emotion="happy")
    def _extract_code_blocks(self,text):
        return [(lang.strip(),code.strip()) for lang,code in re.findall(r'```(\w*)\n?(.*?)```',text,re.DOTALL) if code.strip()]
    def _remove_code_blocks(self,text):
        return re.sub(r'```\w*\n?.*?```','',text,flags=re.DOTALL).strip()
    def _show_typing(self):
        self.typing_label.setText("  Nova is thinking...")
        self.typing_label.show()
        self._typing_dots=0
        self._typing_timer.start(400)
        self._is_waiting_ai=True
        if self.companion_ref:
            self.companion_ref.update_floating_status("curious","Thinking...")
    def _animate_typing(self):
        self._typing_dots=(self._typing_dots%3)+1
        self.typing_label.setText("  Nova is thinking"+"."*self._typing_dots)
    def _remove_typing(self):
        self._typing_timer.stop()
        self.typing_label.hide()
        self._is_waiting_ai=False
    def _toggle_mic(self):
        if self.companion_ref:
            self.companion_ref.toggle_voice_listen()
    def _show_timer(self):
        if self.companion_ref and hasattr(self.companion_ref,'pom_window'):
            self.companion_ref.pom_window.show_timer()
    def _log_water(self):
        if self.companion_ref and hasattr(self.companion_ref,'hydration'):
            msg=self.companion_ref.hydration.log()
            self.show_message(msg,"happy")
            self._speak_now(msg,"happy")
    def _posture_check(self):
        player_name=get_player_name()
        msgs=[f"Hey {player_name}! Sit up straight — your back will thank you!",f"Posture check, {player_name}! Shoulders back, chin up!",f"Time to straighten up, {player_name}! Stand tall!",f"Roll those shoulders, {player_name}! Stay strong and healthy!"]
        msg=random.choice(msgs)
        self.show_message(msg,"caring")
        self._speak_now(msg,"caring")
        if self.companion_ref:
            self.companion_ref.set_emotion_with_status("caring",msg,duration=6000)
    def _analyze_screen(self,mode):
        self._add_chat_bubble("Analyze my screen",is_user=True)
        self._show_typing()
        worker=ScreenAnalysisWorker(mode)
        worker.analysis_complete.connect(self._on_screen_result)
        self._active_workers.append(worker)
        worker.finished.connect(lambda w=worker:self._cleanup_worker(w))
        worker.start()
    def _on_screen_result(self,text,emotion):
        self._remove_typing()
        player_name=get_player_name()
        self._pending_text=text
        self._pending_emotion=emotion
        voice_text=generate_smart_voice_text(text,player_name)
        if self._tts_enabled and voice_text:
            self._start_voice_then_text(voice_text,emotion)
        else:
            self._show_text_now()
        if self.companion_ref:
            self.companion_ref.set_emotion_with_status(emotion,"Analysis complete!",duration=6000)
    def _cleanup_worker(self,w):
        try:
            self._active_workers.remove(w)
        except ValueError:
            pass
    def _start_learning_flow(self,target_name):
        self._learning_mode=True
        self._learning_target=target_name
        self._learning_stage="awaiting_type"
        self._learning_type=""
        player_name=get_player_name()
        msg=(f"Hmm, I do not know '{target_name}' yet, {player_name}! "
             f"Let me learn it from you right now.\n\n"
             f"Is it a website, an app, or a folder?\n"
             f"Just type: website, app, or folder")
        self.show_message(msg,"curious")
        self._speak_now(f"I do not know {target_name} yet, {player_name}. Is it a website, an app, or a folder?","curious")
        if self.companion_ref:
            self.companion_ref.set_emotion_with_status("curious","Learning new command!",duration=0)
        self.input_field.setPlaceholderText("Type: website, app, or folder...")
    def _handle_learning_input(self,msg):
        ml=msg.lower().strip()
        player_name=get_player_name()
        if ml in ["cancel","skip","nevermind","never mind","stop","quit","no"]:
            self._learning_mode=False
            self._learning_target=""
            self._learning_stage=""
            self._learning_type=""
            self.input_field.setPlaceholderText("Message Nova...  (/help for commands)")
            self.show_message("No problem! Just ask me anything else.","happy")
            self._speak_now("No problem! Just ask me anything else.","happy")
            if self.companion_ref:
                self.companion_ref.set_emotion_with_status("happy","Ready!",duration=5000)
            return
        if self._learning_stage=="awaiting_type":
            if any(w in ml for w in ["web","site","website","url","link","http"]):
                self._learning_type="web"
                self._learning_stage="awaiting_value"
                msg_out=(f"Got it! What is the URL for '{self._learning_target}'?\n"
                         f"For example: https://www.example.com or just example.com")
                self.show_message(msg_out,"happy")
                self._speak_now(f"What is the URL for {self._learning_target}?","happy")
                self.input_field.setPlaceholderText("Type the URL here...")
            elif any(w in ml for w in ["app","application","program","exe","software"]):
                self._learning_type="app"
                self._learning_stage="awaiting_value"
                msg_out=(f"Got it! What is the executable name or full path for '{self._learning_target}'?\n"
                         f"For example: notepad.exe or C:\\Program Files\\App\\app.exe")
                self.show_message(msg_out,"happy")
                self._speak_now(f"What is the executable for {self._learning_target}?","happy")
                self.input_field.setPlaceholderText("Type the .exe name or full path...")
            elif any(w in ml for w in ["folder","directory","dir","path"]):
                self._learning_type="folder"
                self._learning_stage="awaiting_value"
                msg_out=(f"Got it! What folder should I open for '{self._learning_target}'?\n"
                         f"For example: Documents, Downloads, or C:\\MyFolder")
                self.show_message(msg_out,"happy")
                self._speak_now(f"What folder should I open for {self._learning_target}?","happy")
                self.input_field.setPlaceholderText("Type the folder name or path...")
            else:
                self.show_message("I did not catch that. Please type: website, app, or folder","confused")
                self._speak_now("Please type website, app, or folder","confused")
            return
        if self._learning_stage=="awaiting_value":
            value=msg.strip()
            cmd_type=self._learning_type
            target_name=self._learning_target
            if cmd_type=="web":
                if not (value.startswith("http://") or value.startswith("https://")):
                    value="https://"+value
            add_learned_command(target_name,cmd_type,value)
            self._learning_mode=False
            self._learning_target=""
            self._learning_stage=""
            self._learning_type=""
            self.input_field.setPlaceholderText("Message Nova...  (/help for commands)")
            success_msg=(f"Done! I have learned that '{target_name}' opens {value}. "
                         f"Next time just say 'open {target_name}' and I will handle it, {player_name}!")
            self.show_message(success_msg,"excited")
            self._speak_now(f"Done! I learned {target_name}. I will remember it from now on, {player_name}!","excited")
            if self.companion_ref:
                self.companion_ref.set_emotion_with_status("excited",f"Learned: {target_name}!",duration=6000)
            cmd_data={"type":cmd_type,"target":value,"response":f"Opening {target_name}!","emotion":"happy"}
            execute_command(cmd_data)
            return
    def _handle_shortcut(self,msg):
        ml=msg.lower().strip()
        player_name=get_player_name()
        if ml=="/help":
            help_text=(
                "Commands:\n"
                "/timer <min>     Start a Pomodoro timer\n"
                "/water           Log a glass of water\n"
                "/water status    Check hydration progress\n"
                "/screentime      Check session duration\n"
                "/break           Reset screen time tracker\n"
                "/posture         Posture reminder\n"
                "/clear           Clear chat history\n"
                "/fontsize <num>  Set font size (13 to 28)\n"
                "/voice off|on    Toggle voice output\n"
                "/name <name>     Change your name\n"
                "/learned         Show learned commands\n"
                "/forget <name>   Remove a learned command\n"
                "/reset           Reset Nova completely\n\n"
                "Shortcuts:\n"
                "Ctrl+Space       Open or close chat\n"
                "Ctrl+1           Toggle voice input\n"
                "Ctrl+2           Analyze screen\n"
                "Ctrl+3           Analyze code on screen\n"
                "Ctrl+4           Open Pomodoro timer\n"
                "Ctrl+5           Log water\n"
                "Ctrl+6           Toggle voice output"
            )
            self.show_message(help_text,"happy")
            self._speak_now(f"Here are all the commands and shortcuts you can use, {player_name}!","happy")
            return True
        if ml=="/reset":
            self.show_message("Resetting Nova now. All data will be cleared and the app will restart.","worried")
            self._speak_now(f"Resetting Nova. See you soon, {player_name}!","caring")
            QTimer.singleShot(2000,self._do_reset)
            return True
        if ml.startswith("/name"):
            parts=ml.split(maxsplit=1)
            if len(parts)>=2:
                new_name=parts[1].strip()
                config=load_config()
                config["player_name"]=new_name
                save_config(config)
                resp=f"Got it! I will call you {new_name} from now on!"
                self.show_message(resp,"happy")
                self._speak_now(resp,"happy")
            else:
                self.show_message(f"Currently calling you: {get_player_name()}","happy")
            return True
        if ml.startswith("/forget"):
            parts=ml.split(maxsplit=1)
            if len(parts)>=2:
                name=parts[1].strip()
                if remove_learned_command(name):
                    resp=f"Done! I have forgotten '{name}' completely."
                    self.show_message(resp,"happy")
                    self._speak_now(resp,"happy")
                else:
                    self.show_message(f"I do not have '{name}' in my memory!","confused")
            else:
                self.show_message("Usage: /forget <command name>","confused")
            return True
        if ml=="/learned":
            learned=load_learned_commands()
            if learned:
                lines=[]
                for name,data in learned.items():
                    learned_at=data.get("learned_at","unknown")
                    lines.append(f"• {name}  ({data['type']})  →  {data['target']}  [{learned_at}]")
                text="Learned Commands:\n"+"\n".join(lines)
                self.show_message(text,"proud")
                self._speak_now(f"You have {len(learned)} learned commands, {player_name}!","proud")
            else:
                self.show_message("No learned commands yet! Just say 'open something' and I will learn it.","happy")
                self._speak_now(f"No learned commands yet, {player_name}!","happy")
            return True
        if ml.startswith("/fontsize"):
            parts=ml.split()
            if len(parts)>=2:
                try:
                    size=int(parts[1])
                    self.set_font_size(size)
                    self.show_message(f"Font size set to {self._base_font_size}!","happy")
                except ValueError:
                    self.show_message("Usage: /fontsize <13-28>","confused")
            else:
                self.show_message(f"Current font size: {self._base_font_size}","happy")
            return True
        if ml.startswith("/timer"):
            parts=ml.split()
            if len(parts)>=2:
                if parts[1]=="stop":
                    if self.companion_ref and hasattr(self.companion_ref,'pom_window'):
                        self.companion_ref.pom_window.stop_timer()
                        self.show_message("Timer stopped!","watching")
                        self._speak_now("Timer stopped!","watching")
                else:
                    try:
                        mins=int(parts[1])
                        if self.companion_ref and hasattr(self.companion_ref,'pom_window'):
                            self.companion_ref.pom_window.default_minutes=mins
                            self.companion_ref.pom_window.remaining=mins*60
                            self.companion_ref.pom_window._update_display()
                            self.companion_ref.pom_window.show_timer()
                            self.companion_ref.pom_window.start_timer()
                            resp=f"{mins} minute timer started! Let us focus, {player_name}!"
                            self.show_message(resp,"excited")
                            self._speak_now(resp,"excited")
                    except ValueError:
                        self.show_message("Usage: /timer <minutes>","confused")
            else:
                self._show_timer()
                self.show_message("Pomodoro timer opened!","happy")
            return True
        if ml.startswith("/water"):
            parts=ml.split()
            if len(parts)>=2 and parts[1]=="status":
                if self.companion_ref and hasattr(self.companion_ref,'hydration'):
                    msg=self.companion_ref.hydration.get_status()
                    self.show_message(msg,"happy")
                    self._speak_now(msg,"happy")
            else:
                self._log_water()
            return True
        if ml=="/posture":
            self._posture_check()
            return True
        if ml=="/screentime":
            if self.companion_ref and hasattr(self.companion_ref,'screen_time'):
                msg=self.companion_ref.screen_time.get_session_time()
                self.show_message(msg,"watching")
                self._speak_now(msg,"watching")
            return True
        if ml=="/break":
            if self.companion_ref and hasattr(self.companion_ref,'screen_time'):
                self.companion_ref.screen_time.take_break()
                resp=f"Break logged! Timer reset. Take care of yourself, {player_name}!"
                self.show_message(resp,"happy")
                self._speak_now(resp,"happy")
                self.companion_ref.set_emotion_with_status("happy","Break taken!",duration=6000)
            return True
        if ml=="/clear":
            while self.chat_layout.count()>1:
                item=self.chat_layout.takeAt(0)
                if item:
                    w=item.widget()
                    if w:
                        w.deleteLater()
            self._chat_messages.clear()
            self.show_message(f"Chat cleared! Fresh start, {player_name}!","happy")
            self._speak_now(f"Chat cleared! Fresh start, {player_name}!","happy")
            return True
        if ml.startswith("/voice"):
            parts=ml.split()
            if len(parts)>=2 and parts[1]=="off":
                self._tts_enabled=False
                self._update_tts_btn_style()
                self.show_message("Voice output disabled.","neutral")
            else:
                self._tts_enabled=True
                self._update_tts_btn_style()
                self.show_message("Voice output enabled!","happy")
                self._speak_now("Voice output enabled!","happy")
            return True
        return False
    def _do_reset(self):
        reset_all_data()
        restart_application()
    def _execute_action(self,action):
        try:
            if action["type"]=="web":
                t=action["target"]
                webbrowser.open(t if t.startswith("http") else f"https://{t}")
            elif action["type"]=="open":
                try:
                    subprocess.Popen(action["target"],shell=False)
                except Exception:
                    try:
                        os.startfile(action["target"])
                    except Exception:
                        subprocess.Popen(f'start "" "{action["target"]}"',shell=True)
            elif action["type"]=="folder":
                open_folder(action["target"])
        except Exception:
            pass
    def send_message(self):
        msg=self.input_field.text().strip()
        if not msg:
            return
        if self._learning_mode:
            self.input_field.clear()
            self._add_chat_bubble(msg,is_user=True)
            self._handle_learning_input(msg)
            return
        if self._is_waiting_ai:
            return
        self.input_field.clear()
        QApplication.processEvents()
        if self.companion_ref:
            self.companion_ref.last_interaction_time=time.time()
        self._add_chat_bubble(msg,is_user=True)
        if msg.startswith("/") and self._handle_shortcut(msg):
            return
        ml=msg.lower()
        screen_general_triggers=["what's on my screen","read screen","analyze screen","analyse screen","what do you see","look at my screen","check my screen","scan my screen","see my screen","what am i looking at","what's on screen","whats on my screen","screen analysis","analyse my screen","analyze my screen","what is on my screen","look at screen","read my screen","capture screen","take a screenshot","screenshot"]
        screen_code_triggers=["explain code","analyze code","analyse code","review code","check code","debug this","look at my code","read my code","check my code","what does this code do","explain this code","analyse my code","analyze my code","debug my code","review my code"]
        if any(ml==x or ml.startswith(x) for x in screen_general_triggers):
            self._analyze_screen("general")
            return
        if any(ml==x or ml.startswith(x) for x in screen_code_triggers):
            self._analyze_screen("code")
            return
        cmd,learn_info=parse_chat_command(msg)
        if cmd:
            success=execute_command(cmd)
            cmd_emotion=cmd.get("emotion","happy")
            player_name=get_player_name()
            if success:
                resp=cmd.get('response',f"Done, {player_name}!")
                cmd_type=cmd.get("type","app")
                app_name=cmd.get("target","")
                voice_resp=generate_command_response_voice(app_name,cmd_type,player_name)
            else:
                resp=f"Hmm, I had trouble with that, {player_name}. Try doing it manually!"
                voice_resp=resp
                cmd_emotion="worried"
            self.show_message(resp,cmd_emotion)
            self._speak_now(voice_resp,cmd_emotion)
            if self.companion_ref:
                self.companion_ref.set_emotion_with_status(cmd_emotion,resp[:50],duration=5000)
            return
        if learn_info:
            target_name=learn_info["unknown_target"]
            suggestions=learn_info.get("suggestions",[])
            player_name=get_player_name()
            if suggestions:
                sugg_text=", ".join(suggestions)
                hint=f"Did you mean: {sugg_text}?\n\nOr I can learn '{target_name}' right now, {player_name}!"
                self.show_message(hint,"curious")
                self._speak_now(f"Did you mean {suggestions[0]}? Or I can learn {target_name} right now!","curious")
                if self.companion_ref:
                    self.companion_ref.set_emotion_with_status("curious","Suggesting...",duration=4000)
            self._start_learning_flow(target_name)
            return
        user_emotion=detect_message_emotion(msg)
        if self.companion_ref:
            self.companion_ref.set_emotion(user_emotion)
        self._show_typing()
        worker=AIWorker(msg,user_emotion)
        worker.response_received.connect(self._on_ai_response)
        worker.voice_ready.connect(self._on_voice_ready)
        worker.action_detected.connect(self._on_action)
        worker.error_occurred.connect(self._on_ai_error)
        self._active_workers.append(worker)
        worker.finished.connect(lambda w=worker:self._cleanup_worker(w))
        worker.start()
    def _on_ai_response(self,text):
        self._remove_typing()
        clean=self._extract_and_execute_commands(text)
        response_emotion=detect_response_emotion(clean)
        self._pending_text=clean
        self._pending_emotion=response_emotion
        if self.companion_ref:
            self.companion_ref.set_emotion_with_status(response_emotion,"Responding...",duration=0)
    def _on_ai_error(self,title,message):
        self._remove_typing()
        self._is_waiting_ai=False
        player_name=get_player_name()
        error_text=f"{title}\n\n{message}"
        self.show_message(error_text,"worried")
        self._speak_now(f"Sorry {player_name}, I ran into an issue. {title}.","worried")
        if self.companion_ref:
            self.companion_ref.set_emotion_with_status("worried",title,duration=10000)
    def _on_voice_ready(self,voice_text,emotion):
        if voice_text and self._tts_enabled:
            self._pending_voice_text=voice_text
            self._pending_voice_emotion=emotion
            self._start_voice_then_text(voice_text,emotion)
        else:
            self._show_text_now()
    def _start_voice_then_text(self,voice_text,emotion):
        if HAS_EDGE_TTS:
            worker=EdgeTTSWorker(voice_text,emotion,self._tts_volume)
            worker.audio_ready.connect(self._play_audio_then_text)
            worker.tts_error.connect(self._on_tts_error_show_text)
            self._tts_workers.append(worker)
            worker.finished.connect(lambda w=worker:self._cleanup_tts_worker(w))
            worker.start()
        else:
            self._show_text_now()
            speak_legacy(voice_text,self._tts_volume)
    def _play_audio_then_text(self,file_path):
        try:
            if not os.path.exists(file_path):
                self._show_text_now()
                return
            url=QUrl.fromLocalFile(os.path.abspath(file_path))
            self.media_player.setMedia(QMediaContent(url))
            self.media_player.setVolume(int(min(1.0,self._tts_volume)*100))
            self.media_player.play()
            QTimer.singleShot(120,self._show_text_now)
            QTimer.singleShot(35000,lambda:self._cleanup_audio(file_path))
        except Exception:
            self._show_text_now()
    def _on_tts_error_show_text(self,error):
        self._show_text_now()
        if self._pending_text and HAS_TTS:
            speak_legacy(self._pending_voice_text,self._tts_volume)
    def _show_text_now(self):
        if self._pending_text:
            text=self._pending_text
            emotion=self._pending_emotion
            self.show_message(text,emotion)
            if self.companion_ref:
                self.companion_ref.set_emotion_with_status(emotion,text[:50],duration=6000)
            self._pending_text=""
            self._pending_emotion="neutral"
            if self._sound_enabled:
                try:
                    import winsound
                    winsound.MessageBeep(winsound.MB_OK)
                except Exception:
                    pass
    def _on_action(self,action):
        try:
            if action["type"]=="web":
                t=action["target"]
                webbrowser.open(t if t.startswith("http") else f"https://{t}")
            elif action["type"]=="open":
                try:
                    subprocess.Popen(action["target"],shell=False)
                except Exception:
                    try:
                        os.startfile(action["target"])
                    except Exception:
                        subprocess.Popen(f'start "" "{action["target"]}"',shell=True)
            elif action["type"]=="folder":
                open_folder(action["target"])
            elif action["type"]=="type":
                if HAS_SCREENSHOT:
                    pyautogui.typewrite(action["target"],interval=0.03)
        except Exception:
            pass
    def _extract_and_execute_commands(self,response):
        commands=re.findall(r'\[CMD:([^\]]+)\]',response)
        clean=re.sub(r'\s*\[CMD:[^\]]+\]\s*','',response).strip()
        for cmd in commands:
            parts=cmd.split(":",1)
            action=parts[0].strip().lower() if parts else ""
            params=parts[1].strip() if len(parts)>1 else ""
            if action=="web":
                webbrowser.open(params if params.startswith("http") else f"https://{params}")
            elif action=="open":
                try:
                    subprocess.Popen(params,shell=False)
                except Exception:
                    try:
                        os.startfile(params)
                    except Exception:
                        try:
                            subprocess.Popen(f'start "" "{params}"',shell=True)
                        except Exception:
                            pass
            elif action=="folder":
                open_folder(params)
            elif action=="type":
                if HAS_SCREENSHOT:
                    try:
                        pyautogui.typewrite(params,interval=0.03)
                    except Exception:
                        pass
        return clean or response
    def _get_resize_edge(self,pos):
        rect=self.rect()
        m=self._resize_margin
        edges=None
        if pos.x()<=m:
            edges="left"
        elif pos.x()>=rect.width()-m:
            edges="right"
        if pos.y()<=m:
            edges=("top" if not edges else edges+"-top")
        elif pos.y()>=rect.height()-m:
            edges=("bottom" if not edges else edges+"-bottom")
        if pos.x()<=m and pos.y()<=m:
            edges="top-left"
        elif pos.x()>=rect.width()-m and pos.y()<=m:
            edges="top-right"
        elif pos.x()<=m and pos.y()>=rect.height()-m:
            edges="bottom-left"
        elif pos.x()>=rect.width()-m and pos.y()>=rect.height()-m:
            edges="bottom-right"
        return edges
    def mousePressEvent(self,event):
        if event.button()==Qt.LeftButton:
            edge=self._get_resize_edge(event.pos())
            if edge:
                self._resize_edge=edge
                self._drag_pos=event.globalPos()
                self._start_geo=self.geometry()
            else:
                self._resize_edge=None
                self._start_geo=None
                self._drag_pos=event.globalPos()-self.frameGeometry().topLeft()
    def mouseMoveEvent(self,event):
        if not (event.buttons()&Qt.LeftButton):
            edge=self._get_resize_edge(event.pos())
            cursors={"left":Qt.SizeHorCursor,"right":Qt.SizeHorCursor,"top":Qt.SizeVerCursor,"bottom":Qt.SizeVerCursor,"top-left":Qt.SizeFDiagCursor,"bottom-right":Qt.SizeFDiagCursor,"top-right":Qt.SizeBDiagCursor,"bottom-left":Qt.SizeBDiagCursor}
            self.setCursor(cursors.get(edge,Qt.ArrowCursor))
            return
        if self._resize_edge and self._drag_pos and self._start_geo:
            diff=event.globalPos()-self._drag_pos
            geo=QRect(self._start_geo)
            if "right" in self._resize_edge:
                geo.setWidth(max(self.minimumWidth(),self._start_geo.width()+diff.x()))
            if "bottom" in self._resize_edge:
                geo.setHeight(max(self.minimumHeight(),self._start_geo.height()+diff.y()))
            if "left" in self._resize_edge:
                new_w=max(self.minimumWidth(),self._start_geo.width()-diff.x())
                geo.setLeft(self._start_geo.right()-new_w)
            if "top" in self._resize_edge:
                new_h=max(self.minimumHeight(),self._start_geo.height()-diff.y())
                geo.setTop(self._start_geo.bottom()-new_h)
            self.setGeometry(geo)
        elif self._drag_pos and not self._resize_edge:
            self.move(event.globalPos()-self._drag_pos)
    def mouseReleaseEvent(self,event):
        self._drag_pos=None
        self._resize_edge=None
        self._start_geo=None
        self.setCursor(Qt.ArrowCursor)
    def resizeEvent(self,event):
        super().resizeEvent(event)
        self._refresh_chat_fonts()
class TransparentWebPage(QWebEnginePage):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.setBackgroundColor(QColor(0,0,0,0))
class OverlayWidget(QWidget):
    def __init__(self,parent):
        super().__init__(parent)
        self.companion=parent
        self.setAttribute(Qt.WA_TranslucentBackground,True)
        self.setStyleSheet("background: transparent;")
        self.drag_position=None
    def mousePressEvent(self,event):
        if event.button()==Qt.LeftButton and self.companion.movable_mode:
            self.drag_position=event.globalPos()-self.companion.frameGeometry().topLeft()
            self.companion.setCursor(Qt.ClosedHandCursor)
            event.accept()
        else:
            event.ignore()
    def mouseMoveEvent(self,event):
        if self.drag_position and event.buttons()==Qt.LeftButton and self.companion.movable_mode:
            self.companion.move(event.globalPos()-self.drag_position)
            event.accept()
        else:
            event.ignore()
    def mouseReleaseEvent(self,event):
        if self.companion.movable_mode and self.drag_position:
            self.drag_position=None
            self.companion.setCursor(Qt.OpenHandCursor)
            event.accept()
        else:
            self.drag_position=None
            event.accept()
    def mouseDoubleClickEvent(self,event):
        self.companion.toggle_chat()
        event.accept()
    def contextMenuEvent(self,event):
        self.companion.show_context_menu(event.globalPos())
        event.accept()
class NovaCompanion(QWidget):
    def __init__(self):
        super().__init__()
        self.current_emotion="neutral"
        self.last_timestamp=0
        self.model_loaded=False
        self._last_floating_text=""
        self._last_floating_color=""
        self.revert_timer=None
        self.last_activity_time=time.time()
        self.last_interaction_time=time.time()
        self.app_start_time=time.time()
        self.listening=False
        self.movable_mode=False
        self.last_matched_app_key=""
        self.last_matched_app_type=""
        self.last_quote_time=time.time()
        self.next_quote_delay=random.randint(900,1200)
        self.last_activity_quote_time=time.time()
        self.last_hour_check=-1
        self.greeted_today=False
        self.used_quotes=[]
        self._status_locked_until=0
        self._current_watching_text=""
        self._persistent_app_status=""
        self._persistent_app_emotion=""
        self.drag_position=None
        self._was_idle=False
        self._idle_start=0
        self._cached_window_title=""
        self._cached_process_name=""
        self._title_check_counter=0
        self._voice_worker=None
        self._continuous_listening=False
        self._last_spoken_time=0
        self._min_speak_gap=180
        self._last_idle_notify=0
        self._last_app_speak_time=0
        self.settings=load_settings()
        self.init_ui()
        self.chat_bubble=ChatBubble(companion_ref=self)
        self.chat_bubble._tts_enabled=self.settings.get("tts_enabled",True)
        self.chat_bubble._tts_volume=self.settings.get("tts_volume",0.8)
        self.chat_bubble._base_font_size=self.settings.get("chat_font_size",16)
        self.chat_bubble._update_tts_btn_style()
        self.pom_window=PomodoroWindow(companion_ref=self)
        self.hydration=HydrationTracker(self)
        self.screen_time=ScreenTimeTracker(self)
        self.setup_system_tray()
        self.setup_global_hotkey()
        self.start_emotion_polling()
        self.start_idle_check()
        self.start_activity_monitor()
        self.start_mouse_tracker()
        self.start_quote_timer()
        self.start_time_awareness()
        self.start_activity_quote_timer()
        threading.Thread(target=self._warmup_client,daemon=True).start()
    def _warmup_client(self):
        try:
            get_gemini_client()
        except Exception:
            pass
    def init_ui(self):
        self.setWindowFlags(Qt.FramelessWindowHint|Qt.WindowStaysOnTopHint|Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground,True)
        self.setFixedSize(350,550)
        screen=QApplication.primaryScreen().geometry()
        self.move(screen.width()-380,screen.height()-600)
        layout=QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        self.browser=QWebEngineView()
        page=TransparentWebPage(self.browser)
        self.browser.setPage(page)
        s=self.browser.settings()
        s.setAttribute(QWebEngineSettings.WebGLEnabled,True)
        s.setAttribute(QWebEngineSettings.Accelerated2dCanvasEnabled,True)
        s.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls,True)
        self.browser.setStyleSheet("background: transparent; border: none;")
        self.browser.page().setBackgroundColor(QColor(0,0,0,0))
        self.browser.loadFinished.connect(self.on_load_finished)
        self.browser.setContextMenuPolicy(Qt.NoContextMenu)
        layout.addWidget(self.browser)
        self.setLayout(layout)
        self.overlay=OverlayWidget(self)
        self.overlay.setGeometry(0,0,350,550)
        self.overlay.raise_()
        html_path=os.path.join(BASE_DIR,"nova_live2d.html")
        self.create_live2d_html(html_path)
        self.browser.setUrl(QUrl.fromLocalFile(html_path))
    def forward_click_to_browser(self,pos):
        self.browser.page().runJavaScript(
            f"(function(){{"
            f"var e=new MouseEvent('click',{{bubbles:true,clientX:{pos.x()},clientY:{pos.y()}}});"
            f"var c=document.querySelector('canvas');"
            f"if(c)c.dispatchEvent(e);"
            f"}})();"
        )
    def setup_system_tray(self):
        self.tray_icon=QSystemTrayIcon(self)
        pix=QPixmap(32,32)
        pix.fill(QColor(124,109,250))
        self.tray_icon.setIcon(QIcon(pix))
        m=QMenu()
        menu_style=f"""
            QMenu {{
                background: {PALETTE['bg_secondary']};
                border: 1px solid {PALETTE['border']};
                color: {PALETTE['text_primary']};
                padding: 10px;
                font-family: 'Segoe UI';
                font-size: {FONT_SIZES['menu']}px;
                border-radius: 14px;
            }}
            QMenu::item {{
                padding: 14px 32px;
                border-radius: 8px;
                font-size: {FONT_SIZES['menu']}px;
            }}
            QMenu::item:selected {{
                background: {PALETTE['bg_card']};
                color: {PALETTE['accent_soft']};
            }}
            QMenu::item:disabled {{
                color: {PALETTE['text_muted']};
            }}
            QMenu::separator {{
                height: 1px;
                background: {PALETTE['border_subtle']};
                margin: 8px 14px;
            }}
        """
        m.setStyleSheet(menu_style)
        for text,handler in [("Show Nova",self.show),("Chat   Ctrl+Space",self.toggle_chat),("Analyze Screen   Ctrl+2",lambda:self._open_chat_and("general")),("Voice Input   Ctrl+1",self.toggle_voice_listen)]:
            a=QAction(text,self)
            a.setFont(QFont("Segoe UI",13))
            a.triggered.connect(handler)
            m.addAction(a)
        m.addSeparator()
        for text,handler in [("Pomodoro   Ctrl+4",lambda:self.pom_window.show_timer()),("Log Water   Ctrl+5",lambda:self.chat_bubble._log_water()),("Posture Check",lambda:self.chat_bubble._posture_check()),("Screen Time",self._show_screen_time)]:
            a=QAction(text,self)
            a.setFont(QFont("Segoe UI",13))
            a.triggered.connect(handler)
            m.addAction(a)
        m.addSeparator()
        codes_menu=m.addMenu("Recent Codes")
        codes_menu.setStyleSheet(menu_style)
        codes_menu.aboutToShow.connect(lambda:self._populate_code_menu(codes_menu))
        m.addSeparator()
        for text,handler in [("Take Break",self._take_break),("Move Nova",self.toggle_movable)]:
            a=QAction(text,self)
            a.setFont(QFont("Segoe UI",13))
            a.triggered.connect(handler)
            m.addAction(a)
        m.addSeparator()
        a=QAction("Reset Nova",self)
        a.setFont(QFont("Segoe UI",13))
        a.triggered.connect(self._reset_nova)
        m.addAction(a)
        m.addSeparator()
        a=QAction("Quit",self)
        a.setFont(QFont("Segoe UI",13))
        a.triggered.connect(QApplication.quit)
        m.addAction(a)
        self.tray_icon.setContextMenu(m)
        self.tray_icon.show()
        self.tray_icon.activated.connect(lambda r:self.toggle_chat() if r==QSystemTrayIcon.DoubleClick else None)
    def setup_global_hotkey(self):
        if not HAS_KEYBOARD:
            return
        hotkeys=[
            ('ctrl+space',self.toggle_chat),
            ('ctrl+1',self.toggle_voice_listen),
            ('ctrl+2',lambda:self._open_chat_and("general")),
            ('ctrl+3',lambda:self._open_chat_and("code")),
            ('ctrl+4',lambda:self.pom_window.show_timer()),
            ('ctrl+5',lambda:self.chat_bubble._log_water()),
            ('ctrl+6',self._toggle_speaker),
        ]
        for hotkey,handler in hotkeys:
            try:
                captured=handler
                keyboard.add_hotkey(
                    hotkey,
                    lambda h=captured:QTimer.singleShot(0,h),
                    suppress=False
                )
            except Exception:
                pass
    def _toggle_speaker(self):
        if not self.chat_bubble.isVisible():
            self.chat_bubble.show_chat()
        self.chat_bubble._toggle_tts()
    def toggle_chat(self):
        if self.chat_bubble.isVisible():
            self.chat_bubble.hide()
            if hasattr(self.chat_bubble,'code_panel'):
                self.chat_bubble.code_panel.hide()
        else:
            self.chat_bubble.show_chat()
    def show_context_menu(self,pos):
        menu=QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{
                background: {PALETTE['bg_secondary']};
                border: 1px solid {PALETTE['border']};
                color: {PALETTE['text_primary']};
                padding: 10px;
                font-family: 'Segoe UI';
                font-size: {FONT_SIZES['menu']}px;
                border-radius: 14px;
            }}
            QMenu::item {{
                padding: 14px 32px;
                border-radius: 8px;
                font-size: {FONT_SIZES['menu']}px;
            }}
            QMenu::item:selected {{
                background: {PALETTE['bg_card']};
                color: {PALETTE['accent_soft']};
            }}
            QMenu::item:disabled {{
                color: {PALETTE['text_muted']};
            }}
            QMenu::separator {{
                height: 1px;
                background: {PALETTE['border_subtle']};
                margin: 8px 14px;
            }}
        """)
        for text,handler in [("Chat",self.toggle_chat),("Analyze Screen",lambda:self._open_chat_and("general")),("Voice Input",self.toggle_voice_listen)]:
            a=QAction(text,self)
            a.setFont(QFont("Segoe UI",13))
            a.triggered.connect(handler)
            menu.addAction(a)
        menu.addSeparator()
        for text,handler in [("Pomodoro Timer",lambda:self.pom_window.show_timer()),("Log Water",lambda:self.chat_bubble._log_water()),("Posture Check",lambda:self.chat_bubble._posture_check()),("Screen Time",self._show_screen_time)]:
            a=QAction(text,self)
            a.setFont(QFont("Segoe UI",13))
            a.triggered.connect(handler)
            menu.addAction(a)
        menu.addSeparator()
        codes_menu=menu.addMenu("Recent Codes")
        codes_menu.setStyleSheet(menu.styleSheet())
        self._populate_code_menu(codes_menu)
        menu.addSeparator()
        for text,handler in [("Take Break",self._take_break),("Move Nova",self.toggle_movable)]:
            a=QAction(text,self)
            a.setFont(QFont("Segoe UI",13))
            a.triggered.connect(handler)
            menu.addAction(a)
        menu.addSeparator()
        a=QAction("Reset Nova",self)
        a.setFont(QFont("Segoe UI",13))
        a.triggered.connect(self._reset_nova)
        menu.addAction(a)
        menu.addSeparator()
        a=QAction("Exit",self)
        a.setFont(QFont("Segoe UI",13))
        a.triggered.connect(QApplication.quit)
        menu.addAction(a)
        menu.exec_(pos)
    def toggle_movable(self):
        self.movable_mode=not self.movable_mode
        player_name=get_player_name()
        if self.movable_mode:
            self.set_emotion_with_status("excited","Drag me anywhere!",duration=0)
            self.setCursor(Qt.OpenHandCursor)
        else:
            self.set_emotion_with_status("happy","Locked in place!",duration=5000)
            self.setCursor(Qt.ArrowCursor)
    def on_load_finished(self,ok):
        if ok:
            QTimer.singleShot(4000,self.mark_model_loaded)
    def mark_model_loaded(self):
        self.model_loaded=True
        self._show_startup_greeting()
        self.browser.page().runJavaScript("if(typeof playStartupAnimation !== 'undefined'){ playStartupAnimation(); }")
    def _show_startup_greeting(self):
        hour=time.localtime().tm_hour
        player_name=get_player_name()
        if 5<=hour<8:
            greetings=[
                f"Wow, early start! Good morning, {player_name}! The world is yours today.",
                f"Rise and shine, {player_name}! You are already ahead of most people.",
            ]
            emotion="excited"
        elif 8<=hour<12:
            greetings=[
                f"Good morning, {player_name}! Let's make today count!",
                f"Hey {player_name}! Nova is online and ready. What are we working on?",
            ]
            emotion="happy"
        elif 12<=hour<14:
            greetings=[
                f"Good afternoon, {player_name}! Hope you have had lunch. Let's keep going!",
                f"Hey {player_name}! Midday check in. How is everything going?",
            ]
            emotion="caring"
        elif 14<=hour<18:
            greetings=[
                f"Good afternoon, {player_name}! You are doing great. Keep that energy up!",
                f"Hey {player_name}! Nova is here. Let's finish the day strong!",
            ]
            emotion="proud"
        elif 18<=hour<19:
            greetings=[
                f"Good evening, {player_name}! How was your day? I am all ears.",
                f"Evening, {player_name}! Time to wind down or keep building. Your call!",
            ]
            emotion="happy"
        elif 19<=hour<23:
            greetings=[
                f"Hey {player_name}! Getting late. Don't overwork yourself tonight.",
                f"Night time, {player_name}! Nova is here if you need anything.",
                f"Hey {player_name}! Winding down? Take it easy tonight.",
            ]
            emotion="caring"
        else:
            greetings=[
                f"{player_name}! It is past midnight. Please get some rest soon.",
                f"Hey {player_name}, burning the midnight oil? I am here but please rest soon.",
            ]
            emotion="worried"
        greeting=random.choice(greetings)
        self._status_locked_until=time.time()+12
        self.set_emotion(emotion,duration=12000)
        self.update_floating_status(emotion,greeting)
        self.chat_bubble._speak_now(greeting,emotion)
    def _reset_nova(self):
        self.set_emotion_with_status("worried","Resetting...",duration=3000)
        player_name=get_player_name()
        self.chat_bubble._speak_now(f"Resetting Nova. See you soon, {player_name}!","caring")
        QTimer.singleShot(2000,self._do_reset)
    def _do_reset(self):
        reset_all_data()
        restart_application()
    def _populate_code_menu(self,menu):
        menu.clear()
        history=self.chat_bubble.get_code_history()
        if not history:
            a=QAction("No recent codes",self)
            a.setEnabled(False)
            menu.addAction(a)
            return
        for i,entry in enumerate(reversed(history[-5:])):
            idx=len(history)-1-i
            lang=entry["blocks"][0][0] if entry["blocks"] else "code"
            label=f"[{entry['time']}]  {lang}"
            a=QAction(label,self)
            a.triggered.connect(lambda checked,x=idx:self.chat_bubble.show_history_code(x))
            menu.addAction(a)
    def _show_screen_time(self):
        if not self.chat_bubble.isVisible():
            self.chat_bubble.show_chat()
        msg=self.screen_time.get_session_time()
        self.chat_bubble.show_message(msg,"watching")
        self.chat_bubble._speak_now(msg,"watching")
    def _take_break(self):
        self.screen_time.take_break()
        player_name=get_player_name()
        resp=f"Break taken! Timer reset. You deserve it, {player_name}!"
        self.set_emotion_with_status("happy",resp,duration=8000)
        self.chat_bubble.show_message(resp,"happy")
        self.chat_bubble._speak_now(resp,"happy")
    def _open_chat_and(self,mode):
        if not self.chat_bubble.isVisible():
            self.chat_bubble.show_chat()
        self.chat_bubble._analyze_screen(mode)
    def start_emotion_polling(self):
        self.poll_timer=QTimer()
        self.poll_timer.timeout.connect(self.check_emotion)
        self.poll_timer.start(500)
    def start_idle_check(self):
        self.idle_checker=QTimer()
        self.idle_checker.timeout.connect(self.check_idle_and_fatigue)
        self.idle_checker.start(60000)
    def start_activity_monitor(self):
        self.activity_timer=QTimer()
        self.activity_timer.timeout.connect(self.check_user_activity)
        self.activity_timer.start(3000)
    def start_mouse_tracker(self):
        self.mouse_timer=QTimer()
        self.mouse_timer.timeout.connect(self.track_mouse)
        self.mouse_timer.start(33)
    def start_quote_timer(self):
        self.quote_timer=QTimer()
        self.quote_timer.timeout.connect(self.auto_show_quote)
        self.quote_timer.start(60000)
    def start_time_awareness(self):
        self.time_timer=QTimer()
        self.time_timer.timeout.connect(self.check_time_events)
        self.time_timer.start(60000)
    def start_activity_quote_timer(self):
        self.activity_quote_timer=QTimer()
        self.activity_quote_timer.timeout.connect(self.show_activity_specific_quote)
        self.activity_quote_timer.start(1200000)
    def show_activity_specific_quote(self):
        if not self.model_loaded or self.listening or self.chat_bubble._is_waiting_ai:
            return
        if not self.last_matched_app_type:
            return
        player_name=get_player_name()
        quote_pool=ACTIVITY_QUOTES_MAP.get(self.last_matched_app_type,RANDOM_QUOTES)
        available=[q for q in quote_pool if q["text"] not in self.used_quotes]
        if not available:
            available=quote_pool
        if not available:
            return
        q=random.choice(available)
        text=q["text"].replace("{player_name}",player_name)
        self.used_quotes.append(q["text"])
        if len(self.used_quotes)>50:
            self.used_quotes=self.used_quotes[-25:]
        self._status_locked_until=time.time()+30
        self.set_emotion(q["emotion"],duration=30000)
        self.update_floating_status(q["emotion"],text)
        should_speak=q.get("speak",False)
        if should_speak and time.time()-self._last_spoken_time>self._min_speak_gap:
            self._last_spoken_time=time.time()
            self.chat_bubble._speak_now(text,q["emotion"])
    def check_user_activity(self):
        if not self.model_loaded or self.listening or self.chat_bubble._is_waiting_ai:
            return
        self._title_check_counter+=1
        if self._title_check_counter%2==0:
            self._cached_window_title=get_active_window_title()
            self._cached_process_name=get_active_process_name()
        title=self._cached_window_title
        process=self._cached_process_name
        combined=(title+" "+process).strip()
        if not combined or len(combined)<2:
            return
        if self._was_idle:
            idle_duration=(time.time()-self._idle_start)/60
            self._was_idle=False
            self._check_comeback(idle_duration)
        self.last_activity_time=time.time()
        matched=False
        for key,data in APP_WATCH_MAP.items():
            if key in title or key in process:
                matched=True
                self.screen_time.check_distraction(key)
                if key!=self.last_matched_app_key:
                    self.last_matched_app_key=key
                    self.last_matched_app_type=data.get("type","")
                    self._current_watching_text=data["text"]
                    self._persistent_app_status=data["text"]
                    self._persistent_app_emotion=data["emotion"]
                    self._status_locked_until=0
                    self.set_emotion(data["emotion"],duration=0)
                    self.update_floating_status(data["emotion"],data["text"])
                    should_speak=data.get("speak",False)
                    if should_speak and time.time()-self._last_app_speak_time>300:
                        self._last_app_speak_time=time.time()
                        player_name=get_player_name()
                        speak_text=data["text"].replace("{player_name}",player_name)
                        self.chat_bubble._speak_now(speak_text,data["emotion"])
                else:
                    if time.time()>=self._status_locked_until and self._persistent_app_status:
                        self.update_floating_status(self._persistent_app_emotion,self._persistent_app_status)
                break
        if not matched:
            self.screen_time.check_distraction("")
            if self.last_matched_app_key:
                self.last_matched_app_key=""
                self.last_matched_app_type=""
                self._current_watching_text=""
                self._persistent_app_status=""
                self._persistent_app_emotion=""
                if time.time()>=self._status_locked_until:
                    self.revert_to_neutral()
    def _check_comeback(self,minutes_away):
        player_name=get_player_name()
        for quote in reversed(COMEBACK_QUOTES):
            if minutes_away>=quote["min_away"]:
                text=quote["text"].replace("{player_name}",player_name)
                self._status_locked_until=time.time()+10
                self.set_emotion_with_status(quote["emotion"],text,duration=10000)
                if quote.get("speak",True):
                    self.chat_bubble._speak_now(text,quote["emotion"])
                break
    def show_contextual_quote(self):
        now=time.localtime()
        hour=now.tm_hour
        weekday=now.tm_wday
        player_name=get_player_name()
        if 22<=hour or hour<5:
            pool=NIGHT_QUOTES+AFFIRMATION_QUOTES
        elif 5<=hour<10:
            pool=MORNING_QUOTES+RANDOM_QUOTES
        elif weekday>=5:
            pool=WEEKEND_QUOTES+RANDOM_QUOTES
        else:
            pool=RANDOM_QUOTES+AFFIRMATION_QUOTES
        available=[q for q in pool if q["text"] not in self.used_quotes]
        if not available:
            self.used_quotes.clear()
            available=pool
        if not available:
            return
        q=random.choice(available)
        text=q["text"].replace("{player_name}",player_name)
        self.used_quotes.append(q["text"])
        if len(self.used_quotes)>50:
            self.used_quotes=self.used_quotes[-25:]
        self._status_locked_until=time.time()+15
        self.set_emotion(q["emotion"],duration=15000)
        self.update_floating_status(q["emotion"],text)
        should_speak=q.get("speak",False)
        if should_speak and time.time()-self._last_spoken_time>self._min_speak_gap:
            self._last_spoken_time=time.time()
            self.chat_bubble._speak_now(text,q["emotion"])
    def auto_show_quote(self):
        if not self.model_loaded or self.listening or self.chat_bubble._is_waiting_ai:
            return
        if time.time()<self._status_locked_until:
            return
        if self._persistent_app_status:
            return
        if time.time()-self.last_quote_time>self.next_quote_delay:
            self.last_quote_time=time.time()
            self.next_quote_delay=random.randint(1200,1800)
            self.show_contextual_quote()
    def check_time_events(self):
        if not self.model_loaded or time.time()<self._status_locked_until or self.chat_bubble._is_waiting_ai:
            return
        now=time.localtime()
        hour=now.tm_hour
        player_name=get_player_name()
        if hour!=self.last_hour_check:
            self.last_hour_check=hour
            if 6<=hour<=9 and not self.greeted_today:
                self.greeted_today=True
                q=random.choice(MORNING_QUOTES)
                text=q["text"].replace("{player_name}",player_name)
                self._status_locked_until=time.time()+15
                self.set_emotion(q["emotion"],duration=15000)
                self.update_floating_status(q["emotion"],text)
                if q.get("speak",True):
                    self.chat_bubble._speak_now(text,q["emotion"])
            elif hour==23:
                q=random.choice(NIGHT_QUOTES)
                text=q["text"].replace("{player_name}",player_name)
                self._status_locked_until=time.time()+15
                self.set_emotion(q["emotion"],duration=15000)
                self.update_floating_status(q["emotion"],text)
                if q.get("speak",True):
                    self.chat_bubble._speak_now(text,q["emotion"])
            elif hour==0:
                self.greeted_today=False
                msg=f"New day begins. Rest up, {player_name}!"
                self._status_locked_until=time.time()+15
                self.set_emotion("caring",duration=15000)
                self.update_floating_status("caring",msg)
                self.chat_bubble._speak_now(msg,"caring")
            elif hour==3:
                msg=f"It is 3 AM, {player_name}! Please go to sleep!"
                self._status_locked_until=time.time()+15
                self.set_emotion("worried",duration=15000)
                self.update_floating_status("worried",f"3 AM! Please sleep, {player_name}!")
                self.chat_bubble._speak_now(msg,"worried")
    def check_idle_and_fatigue(self):
        if not self.model_loaded or self.chat_bubble._is_waiting_ai:
            return
        idle_duration=time.time()-self.last_activity_time
        if idle_duration>600 and not self._was_idle:
            self._was_idle=True
            self._idle_start=self.last_activity_time
        if idle_duration>3600:
            if time.time()-self._last_idle_notify>3600:
                self._last_idle_notify=time.time()
                player_name=get_player_name()
                msg=f"Hey {player_name}, it has been a while! Is everything okay?"
                self._status_locked_until=time.time()+15
                self.set_emotion("lonely",duration=15000)
                self.update_floating_status("lonely","Been a while! Everything okay?")
                self.chat_bubble._speak_now(msg,"caring")
        elif idle_duration>1800:
            if time.time()-self._last_idle_notify>1800:
                self._last_idle_notify=time.time()
                self._status_locked_until=time.time()+12
                self.set_emotion("watching",duration=12000)
                self.update_floating_status("watching","Still around? I am here!")
    def track_mouse(self):
        if not self.model_loaded:
            return
        try:
            cursor_pos=QCursor.pos()
            screen=QApplication.primaryScreen().geometry()
            nova_cx=self.x()+175
            nova_cy=self.y()+200
            dx=max(-1.0,min(1.0,(cursor_pos.x()-nova_cx)/max(screen.width()*0.5,1)))
            dy=max(-1.0,min(1.0,(cursor_pos.y()-nova_cy)/max(screen.height()*0.5,1)))
            self.browser.page().runJavaScript(
                f"if(typeof updateMouseTracking!=='undefined'){{updateMouseTracking({dx:.4f},{dy:.4f});}}"
            )
        except Exception:
            pass
    def check_emotion(self):
        if not self.model_loaded or time.time()<self._status_locked_until:
            return
        data=read_emotion()
        if data["timestamp"]>self.last_timestamp:
            self.last_timestamp=data["timestamp"]
            self.set_emotion(data["emotion"],data["duration"])
    def update_floating_status(self,emotion,text,color=None):
        color=color or EMOTION_STATUS_COLORS.get(emotion,PALETTE['text_secondary'])
        emotion_display=EMOTION_DISPLAY_NAMES.get(emotion,"Neutral")
        display_text=f"{emotion_display}  {text}"
        if display_text==self._last_floating_text and color==self._last_floating_color:
            return
        self._last_floating_text=display_text
        self._last_floating_color=color
        safe=display_text.replace("\\","\\\\").replace("'","\\'").replace('"','\\"').replace('\n',' ')
        self.browser.page().runJavaScript(
            f"if(typeof updateFloatingStatus!=='undefined'){{updateFloatingStatus('{safe}','{color}');}}"
        )
    def set_emotion_with_status(self,emotion,status_text,duration=0):
        self.set_emotion(emotion,duration)
        self.update_floating_status(emotion,status_text)
        if duration>0:
            self._status_locked_until=time.time()+(duration/1000.0)
    def set_emotion(self,emotion,duration=0):
        if self.revert_timer:
            self.revert_timer.stop()
            self.revert_timer=None
        self.current_emotion=emotion
        emotion_map={"happy":"happy","excited":"excited","worried":"worried","proud":"proud","tired":"tired","caring":"happy","loving":"happy","playful":"excited","curious":"watching","jealous":"watching","smug":"proud","sleepy":"tired","determined":"excited","grateful":"touched","shocked":"shocked","watching":"watching","touched":"touched","headpat":"headpat","poke":"poke","neutral":"neutral","shy":"happy","comfort":"comfort","confused":"confused","nostalgic":"nostalgic","angry":"angry","lonely":"lonely","relieved":"relieved"}
        js_emotion=emotion_map.get(emotion,"neutral")
        self.browser.page().runJavaScript(
            f"if(typeof setEmotion!=='undefined'){{setEmotion('{js_emotion}');}}"
        )
        if duration>0:
            self.revert_timer=QTimer()
            self.revert_timer.setSingleShot(True)
            self.revert_timer.timeout.connect(self._on_revert_timer)
            self.revert_timer.start(duration)
    def _on_revert_timer(self):
        if self._persistent_app_status and self.last_matched_app_key:
            self.set_emotion(self._persistent_app_emotion,duration=0)
            self.update_floating_status(self._persistent_app_emotion,self._persistent_app_status)
        else:
            self.revert_to_neutral()
    def revert_to_neutral(self):
        self.current_emotion="neutral"
        self._current_watching_text=""
        self._last_floating_text=""
        self._last_floating_color=""
        self.browser.page().runJavaScript(
            "if(typeof setEmotion!=='undefined'){setEmotion('neutral');}"
        )
        self.update_floating_status("neutral","Nova is here")
    def toggle_voice_listen(self):
        if not HAS_SPEECH:
            self.set_emotion_with_status("worried","No speech module!",duration=6000)
            if self.chat_bubble.isVisible():
                self.chat_bubble.show_message("Voice input requires SpeechRecognition and PyAudio.\nInstall with: pip install SpeechRecognition PyAudio","worried")
            return
        player_name=get_player_name()
        if self.listening:
            self.listening=False
            self._continuous_listening=False
            if self._voice_worker:
                self._voice_worker.stop()
                self._voice_worker=None
            msg=f"Voice input stopped, {player_name}!"
            self.set_emotion_with_status("happy",msg,duration=5000)
            if self.chat_bubble.isVisible():
                self.chat_bubble.show_message(msg,"happy")
                self.chat_bubble._speak_now(msg,"happy")
            return
        self.listening=True
        self._continuous_listening=True
        self.set_emotion_with_status("excited","Listening... speak now!",duration=0)
        if not self.chat_bubble.isVisible():
            self.chat_bubble.show_chat()
        self.chat_bubble._add_chat_bubble(f"Continuous listening ON — click mic or press Ctrl+1 to stop",is_user=True)
        self._start_voice_worker()
    def _start_voice_worker(self):
        if not self._continuous_listening:
            return
        self._voice_worker=VoiceWorker(continuous=True)
        self._voice_worker.voice_result.connect(self._on_voice_result)
        self._voice_worker.voice_error.connect(self._on_voice_error)
        self._voice_worker.voice_status.connect(self._on_voice_status)
        self._voice_worker.start()
    def _on_voice_status(self,status):
        self.set_emotion_with_status("excited",status,duration=0)
    def _on_voice_result(self,text):
        player_name=get_player_name()
        self.set_emotion_with_status("happy",f"Heard: {text[:40]}",duration=3000)
        if not self.chat_bubble.isVisible():
            self.chat_bubble.show_chat()
        self.chat_bubble.input_field.setText(text)
        QTimer.singleShot(100,self.chat_bubble.send_message)
    def _on_voice_error(self,error):
        if not self._continuous_listening:
            self.listening=False
            self.set_emotion_with_status("worried",error,duration=5000)
            if self.chat_bubble.isVisible():
                self.chat_bubble.show_message(f"Voice Error: {error}","worried")
    def mousePressEvent(self,event):
        if event.button()==Qt.LeftButton and self.movable_mode:
            self.drag_position=event.globalPos()-self.frameGeometry().topLeft()
            self.setCursor(Qt.ClosedHandCursor)
    def mouseMoveEvent(self,event):
        if self.drag_position and event.buttons()==Qt.LeftButton and self.movable_mode:
            self.move(event.globalPos()-self.drag_position)
    def mouseReleaseEvent(self,event):
        self.drag_position=None
        if self.movable_mode:
            self.setCursor(Qt.OpenHandCursor)
        else:
            self.setCursor(Qt.ArrowCursor)
    def create_live2d_html(self, path):
        html = r'''<!DOCTYPE html>
<html>
<head>
<style>
* { margin: 0; padding: 0; }
html, body { overflow: hidden; background: rgba(0,0,0,0) !important; width: 350px; height: 550px; }
canvas { background: transparent !important; }
#floating-status {
    position: fixed; bottom: 14px; left: 50%; transform: translateX(-50%);
    color: #4FC3F7; font-family: 'Cascadia Code', 'Fira Code', 'Consolas', sans-serif; font-size: 14px; font-weight: 600;
    background: rgba(2,6,14,0.92); padding: 12px 22px; border-radius: 18px;
    border: 1px solid rgba(0,150,255,0.25); z-index: 9999; pointer-events: none;
    white-space: nowrap; transition: color 0.3s ease, border-color 0.3s ease;
    max-width: 340px; text-overflow: ellipsis; overflow: hidden;
    backdrop-filter: blur(24px); -webkit-backdrop-filter: blur(24px);
    box-shadow: 0 6px 30px rgba(0,60,160,0.25);
}
#floating-status.pop { animation: popAnim 0.4s ease; }
@keyframes popAnim {
    0% { transform: translateX(-50%) scale(0.85); opacity: 0.4; }
    50% { transform: translateX(-50%) scale(1.08); opacity: 1; }
    100% { transform: translateX(-50%) scale(1.0); opacity: 1; }
}
#loading-overlay {
    position: fixed; top: 0; left: 0; width: 100%; height: 100%;
    background: rgba(1,3,8,0.97); display: flex; flex-direction: column;
    align-items: center; justify-content: center; z-index: 20000;
    transition: opacity 0.8s ease;
}
#loading-overlay.hidden { opacity: 0; pointer-events: none; }
.loading-spinner {
    width: 52px; height: 52px; border: 3px solid rgba(0,150,255,0.12);
    border-top: 3px solid #00BFFF; border-radius: 50%;
    animation: spin 1s linear infinite; margin-bottom: 22px;
}
@keyframes spin { 0%{transform:rotate(0deg)} 100%{transform:rotate(360deg)} }
.loading-text { color: #00BFFF; font-family: 'Cascadia Code', 'Fira Code', 'Consolas', sans-serif; font-size: 15px; font-weight: 600; }
</style>
</head>
<body>
<div id="loading-overlay">
    <div class="loading-spinner"></div>
    <div class="loading-text">Loading Nova...</div>
</div>
<div id="floating-status">Loading...</div>
<script>
var cubismCoreMirrors=["https://cubism.live2d.com/sdk-web/cubismcore/live2dcubismcore.min.js","https://cdn.jsdelivr.net/gh/nicx-next/live2d-cubism-core@master/live2dcubismcore.min.js"];
var pixiMirrors=["https://cdnjs.cloudflare.com/ajax/libs/pixi.js/6.5.10/browser/pixi.min.js","https://cdn.jsdelivr.net/npm/pixi.js@6.5.10/dist/browser/pixi.min.js"];
var live2dPluginMirrors=["https://cdn.jsdelivr.net/npm/pixi-live2d-display@0.4.0/dist/cubism4.min.js","https://unpkg.com/pixi-live2d-display@0.4.0/dist/cubism4.min.js"];
function loadScriptWithFallback(u,i,cb){if(i>=u.length){cb(false);return;}var s=document.createElement("script");s.src=u[i];s.onload=function(){cb(true);};s.onerror=function(){document.head.removeChild(s);loadScriptWithFallback(u,i+1,cb);};document.head.appendChild(s);}
function updateLoadingText(t){var e=document.querySelector(".loading-text");if(e)e.textContent=t;}
function hideLoading(){var o=document.getElementById("loading-overlay");if(o){o.classList.add("hidden");setTimeout(function(){o.style.display="none";},900);}}
var currentModel=null,currentEmotion="neutral",emotionTransition=null;
var idleTime=0,blinkTimer=0,isBlinking=false,modelReady=false;
var paramMap={},frozenParams={};
var touchReactTimer=null,touchCount=0;
var trackMouseNX=0,trackMouseNY=0,smoothMouseX=0,smoothMouseY=0;
var lastStatusText="";
var EMOTIONS={
neutral:{params:{ParamAngleX:0,ParamAngleY:0,ParamAngleZ:0,ParamEyeLOpen:1,ParamEyeROpen:1,ParamEyeLSmile:0,ParamEyeRSmile:0,ParamMouthForm:0.2,ParamMouthOpenY:0,ParamCheek:0,ParamBodyAngleX:0,ParamBodyAngleY:0,ParamBodyAngleZ:0}},
happy:{params:{ParamAngleX:-18,ParamAngleY:8,ParamAngleZ:-22,ParamEyeLOpen:0,ParamEyeROpen:0,ParamEyeLSmile:1,ParamEyeRSmile:1,ParamMouthForm:0.65,ParamMouthOpenY:0,ParamCheek:1,ParamBodyAngleX:-12,ParamBodyAngleY:4,ParamBodyAngleZ:-16}},
excited:{params:{ParamAngleX:-8,ParamAngleY:15,ParamAngleZ:-18,ParamEyeLOpen:1.3,ParamEyeROpen:1.3,ParamEyeLSmile:0.35,ParamEyeRSmile:0.35,ParamMouthForm:1,ParamMouthOpenY:0,ParamCheek:0.85,ParamBodyAngleX:-8,ParamBodyAngleY:8,ParamBodyAngleZ:10}},
worried:{params:{ParamAngleX:-10,ParamAngleY:-8,ParamAngleZ:12,ParamEyeLOpen:0.55,ParamEyeROpen:0.5,ParamEyeLSmile:0,ParamEyeRSmile:0,ParamMouthForm:-0.85,ParamMouthOpenY:0,ParamCheek:0,ParamBodyAngleX:-5,ParamBodyAngleY:-5,ParamBodyAngleZ:8}},
proud:{params:{ParamAngleX:15,ParamAngleY:20,ParamAngleZ:-12,ParamEyeLOpen:0,ParamEyeROpen:1.2,ParamEyeLSmile:1,ParamEyeRSmile:0,ParamMouthForm:0.85,ParamMouthOpenY:0,ParamCheek:0.65,ParamBodyAngleX:12,ParamBodyAngleY:14,ParamBodyAngleZ:-10}},
tired:{params:{ParamAngleX:12,ParamAngleY:-15,ParamAngleZ:20,ParamEyeLOpen:0.18,ParamEyeROpen:0.12,ParamEyeLSmile:0,ParamEyeRSmile:0,ParamMouthForm:-0.25,ParamMouthOpenY:0,ParamCheek:0,ParamBodyAngleX:10,ParamBodyAngleY:-12,ParamBodyAngleZ:15}},
shocked:{params:{ParamAngleX:0,ParamAngleY:-8,ParamAngleZ:-5,ParamEyeLOpen:1.5,ParamEyeROpen:1.5,ParamEyeLSmile:0,ParamEyeRSmile:0,ParamMouthForm:-0.85,ParamMouthOpenY:1,ParamCheek:0,ParamBodyAngleX:0,ParamBodyAngleY:-5,ParamBodyAngleZ:-8}},
watching:{params:{ParamAngleX:5,ParamAngleY:-5,ParamAngleZ:8,ParamEyeLOpen:0.82,ParamEyeROpen:0.82,ParamEyeLSmile:0,ParamEyeRSmile:0,ParamMouthForm:0.38,ParamMouthOpenY:0,ParamCheek:0.32,ParamBodyAngleX:5,ParamBodyAngleY:-3,ParamBodyAngleZ:6}},
touched:{params:{ParamAngleX:0,ParamAngleY:5,ParamAngleZ:-12,ParamEyeLOpen:1.3,ParamEyeROpen:1.3,ParamEyeLSmile:0.45,ParamEyeRSmile:0.45,ParamMouthForm:0.92,ParamMouthOpenY:0,ParamCheek:1,ParamBodyAngleX:0,ParamBodyAngleY:3,ParamBodyAngleZ:-5}},
headpat:{params:{ParamAngleX:0,ParamAngleY:-16,ParamAngleZ:-6,ParamEyeLOpen:0,ParamEyeROpen:0,ParamEyeLSmile:1,ParamEyeRSmile:1,ParamMouthForm:1,ParamMouthOpenY:0,ParamCheek:1,ParamBodyAngleX:0,ParamBodyAngleY:-9,ParamBodyAngleZ:-3}},
poke:{params:{ParamAngleX:-22,ParamAngleY:12,ParamAngleZ:10,ParamEyeLOpen:1.4,ParamEyeROpen:0.35,ParamEyeLSmile:0,ParamEyeRSmile:0,ParamMouthForm:-0.55,ParamMouthOpenY:0,ParamCheek:0,ParamBodyAngleX:-11,ParamBodyAngleY:6,ParamBodyAngleZ:5}},
shy:{params:{ParamAngleX:-28,ParamAngleY:-12,ParamAngleZ:16,ParamEyeLOpen:0.35,ParamEyeROpen:0.45,ParamEyeLSmile:0.35,ParamEyeRSmile:0.35,ParamMouthForm:0.35,ParamMouthOpenY:0,ParamCheek:1,ParamBodyAngleX:-16,ParamBodyAngleY:-9,ParamBodyAngleZ:13}},
comfort:{params:{ParamAngleX:6,ParamAngleY:-6,ParamAngleZ:-9,ParamEyeLOpen:0.72,ParamEyeROpen:0.72,ParamEyeLSmile:0.55,ParamEyeRSmile:0.55,ParamMouthForm:0.45,ParamMouthOpenY:0,ParamCheek:0.65,ParamBodyAngleX:4,ParamBodyAngleY:-4,ParamBodyAngleZ:-6}},
loving:{params:{ParamAngleX:-11,ParamAngleY:6,ParamAngleZ:-16,ParamEyeLOpen:0,ParamEyeROpen:0,ParamEyeLSmile:1,ParamEyeRSmile:1,ParamMouthForm:0.75,ParamMouthOpenY:0,ParamCheek:1,ParamBodyAngleX:-9,ParamBodyAngleY:4,ParamBodyAngleZ:-11}},
confused:{params:{ParamAngleX:16,ParamAngleY:11,ParamAngleZ:13,ParamEyeLOpen:1.12,ParamEyeROpen:0.68,ParamEyeLSmile:0,ParamEyeRSmile:0,ParamMouthForm:-0.35,ParamMouthOpenY:0,ParamCheek:0,ParamBodyAngleX:9,ParamBodyAngleY:6,ParamBodyAngleZ:9}},
nostalgic:{params:{ParamAngleX:11,ParamAngleY:-11,ParamAngleZ:6,ParamEyeLOpen:0.58,ParamEyeROpen:0.58,ParamEyeLSmile:0.25,ParamEyeRSmile:0.25,ParamMouthForm:0.22,ParamMouthOpenY:0,ParamCheek:0.32,ParamBodyAngleX:6,ParamBodyAngleY:-6,ParamBodyAngleZ:4}},
angry:{params:{ParamAngleX:0,ParamAngleY:16,ParamAngleZ:-6,ParamEyeLOpen:0.88,ParamEyeROpen:0.88,ParamEyeLSmile:0,ParamEyeRSmile:0,ParamMouthForm:-1,ParamMouthOpenY:0,ParamCheek:0,ParamBodyAngleX:0,ParamBodyAngleY:11,ParamBodyAngleZ:-4}},
lonely:{params:{ParamAngleX:22,ParamAngleY:-22,ParamAngleZ:16,ParamEyeLOpen:0.48,ParamEyeROpen:0.48,ParamEyeLSmile:0,ParamEyeRSmile:0,ParamMouthForm:-0.55,ParamMouthOpenY:0,ParamCheek:0,ParamBodyAngleX:13,ParamBodyAngleY:-16,ParamBodyAngleZ:11}},
relieved:{params:{ParamAngleX:-6,ParamAngleY:-6,ParamAngleZ:-11,ParamEyeLOpen:0,ParamEyeROpen:0,ParamEyeLSmile:0.82,ParamEyeRSmile:0.82,ParamMouthForm:0.55,ParamMouthOpenY:0,ParamCheek:0.55,ParamBodyAngleX:-4,ParamBodyAngleY:-4,ParamBodyAngleZ:-9}}
};
function updateMouseTracking(nx,ny){trackMouseNX=nx;trackMouseNY=ny;}
function updateFloatingStatus(text,color){var el=document.getElementById("floating-status");if(!el)return;var changed=(lastStatusText!==text);lastStatusText=text;el.textContent=text;el.style.color=color;el.style.borderColor=color;if(changed){el.classList.remove("pop");void el.offsetWidth;el.classList.add("pop");}}
function playStartupAnimation(){if(!modelReady)return;setEmotion("excited");setTimeout(function(){setEmotion("happy");setTimeout(function(){setEmotion("watching");setTimeout(function(){if(currentEmotion==="watching")setEmotion("neutral");},2800);},1600);},1300);}
var modelUrls=["https://cdn.jsdelivr.net/gh/Live2D/CubismWebSamples@develop/Samples/Resources/Haru/Haru.model3.json"];
async function tryLoadModel(urls,index){if(index>=urls.length)throw new Error("All model URLs failed");try{return await PIXI.live2d.Live2DModel.from(urls[index]);}catch(e){return await tryLoadModel(urls,index+1);}}
async function initLive2D(){var app=new PIXI.Application({transparent:true,backgroundAlpha:0,width:350,height:550,resolution:1,autoDensity:true,antialias:true});app.renderer.backgroundAlpha=0;document.body.appendChild(app.view);app.view.style.cssText="position:fixed;top:0;left:0;z-index:1;";try{updateLoadingText("Loading Nova model...");var model=await tryLoadModel(modelUrls,0);currentModel=model;app.stage.addChild(model);var scale=Math.min(app.screen.width/model.width,app.screen.height/model.height)*0.9;model.scale.set(scale);model.anchor.set(0.5,0.0);model.x=app.screen.width/2;model.y=10;var ids=Array.from(currentModel.internalModel.coreModel._parameterIds);ids.forEach(function(id,idx){paramMap[id]=idx;});frozenParams={};for(var p in EMOTIONS.neutral.params){frozenParams[p]=EMOTIONS.neutral.params[p];}if(currentModel.internalModel.motionManager){currentModel.internalModel.motionManager.stopAllMotions();var origUpdate=currentModel.internalModel.motionManager.update.bind(currentModel.internalModel.motionManager);currentModel.internalModel.motionManager.update=function(m,now){origUpdate(m,now);applyFrozenParams();};}modelReady=true;hideLoading();updateFloatingStatus("[Neutral] Nova is here!","#4FC3F7");app.ticker.add(function(){if(!modelReady)return;idleTime+=0.016;blinkTimer+=0.016;smoothMouseX+=(trackMouseNX-smoothMouseX)*0.18;smoothMouseY+=(trackMouseNY-smoothMouseY)*0.18;applyFrozenParams();applyIdle();applyBlink();});}catch(e){updateLoadingText("Error: "+e.message);}}
function handleTouch(areas){if(!modelReady)return;touchCount++;if(touchReactTimer)clearTimeout(touchReactTimer);if(touchCount>=3){setEmotion("headpat");touchCount=0;}else if(touchCount===2){setEmotion("touched");}else{setEmotion("poke");}touchReactTimer=setTimeout(function(){touchCount=0;setEmotion("happy");setTimeout(function(){if(currentEmotion==="happy")setEmotion("neutral");},3500);},4500);}
function setP(name,value){if(!currentModel||!modelReady)return;var idx=paramMap[name];if(idx!==undefined)currentModel.internalModel.coreModel.setParameterValueByIndex(idx,value);}
function applyFrozenParams(){if(!currentModel||!modelReady)return;for(var p in frozenParams)setP(p,frozenParams[p]);}
function applyIdle(){var breath=0.5+Math.sin(idleTime*2)*0.5;setP("ParamBreath",breath);var ep=EMOTIONS[currentEmotion]?EMOTIONS[currentEmotion].params:EMOTIONS.neutral.params;var bAX=ep.ParamAngleX||0,bAY=ep.ParamAngleY||0,bAZ=ep.ParamAngleZ||0;var bBX=ep.ParamBodyAngleX||0,bBY=ep.ParamBodyAngleY||0,bBZ=ep.ParamBodyAngleZ||0;var mhx=smoothMouseX*35,mhy=-smoothMouseY*28;var mbx=smoothMouseX*12,mby=-smoothMouseY*8;frozenParams.ParamAngleX=bAX+Math.sin(idleTime*0.55)*1.2+mhx;
frozenParams.ParamAngleY=bAY+Math.cos(idleTime*0.42)*0.9+mhy;
frozenParams.ParamAngleZ=bAZ+Math.sin(idleTime*0.35)*1.1;
frozenParams.ParamBodyAngleX=bBX+Math.sin(idleTime*0.28)*0.8+mbx;
frozenParams.ParamBodyAngleY=bBY+mby;
frozenParams.ParamBodyAngleZ=bBZ+Math.sin(idleTime*0.32)*0.7;setP("ParamHairFront",Math.sin(idleTime*1.2)*0.55);
setP("ParamHairSide",Math.sin(idleTime*0.95)*0.4);
setP("ParamHairBack",Math.sin(idleTime*0.85)*0.45);var eyesClosed=(currentEmotion==="happy"||currentEmotion==="headpat"||currentEmotion==="tired"||currentEmotion==="proud"||currentEmotion==="loving"||currentEmotion==="relieved"||currentEmotion==="shy");if(!eyesClosed){frozenParams.ParamEyeBallX=smoothMouseX*1.0;frozenParams.ParamEyeBallY=-smoothMouseY*0.85;}}
function applyBlink(){var eyesClosed=(currentEmotion==="happy"||currentEmotion==="headpat"||currentEmotion==="tired"||currentEmotion==="loving"||currentEmotion==="relieved"||currentEmotion==="shy");if(eyesClosed||isBlinking)return;if(blinkTimer>3.2+Math.random()*4.2){isBlinking=true;blinkTimer=0;var oL=frozenParams.ParamEyeLOpen!==undefined?frozenParams.ParamEyeLOpen:1;var oR=frozenParams.ParamEyeROpen!==undefined?frozenParams.ParamEyeROpen:1;frozenParams.ParamEyeLOpen=0;frozenParams.ParamEyeROpen=0;setTimeout(function(){frozenParams.ParamEyeLOpen=oL;frozenParams.ParamEyeROpen=oR;isBlinking=false;},105);}}
function setEmotion(emotionName){if(!currentModel||!modelReady)return;var emotion=EMOTIONS[emotionName];if(!emotion){emotion=EMOTIONS.neutral;emotionName="neutral";}currentEmotion=emotionName;if(emotionTransition){clearInterval(emotionTransition);emotionTransition=null;}var startParams={};for(var p in emotion.params){startParams[p]=frozenParams[p]!==undefined?frozenParams[p]:0;}var targetParams=emotion.params;var progress=0;emotionTransition=setInterval(function(){progress+=0.02;if(progress>=1){progress=1;clearInterval(emotionTransition);emotionTransition=null;}var t=1-Math.pow(1-progress,3);for(var param in targetParams){var sv=startParams[param]!==undefined?startParams[param]:0;frozenParams[param]=sv+(targetParams[param]-sv)*t;}},16);}
window.setEmotion=setEmotion;window.updateMouseTracking=updateMouseTracking;window.updateFloatingStatus=updateFloatingStatus;window.handleTouch=handleTouch;window.playStartupAnimation=playStartupAnimation;
function startLoading(){updateLoadingText("Loading Cubism Core...");loadScriptWithFallback(cubismCoreMirrors,0,function(ok1){if(!ok1){updateLoadingText("Failed: Cubism Core");return;}updateLoadingText("Loading PixiJS...");loadScriptWithFallback(pixiMirrors,0,function(ok2){if(!ok2){updateLoadingText("Failed: PixiJS");return;}updateLoadingText("Loading Live2D Plugin...");loadScriptWithFallback(live2dPluginMirrors,0,function(ok3){if(!ok3){updateLoadingText("Failed: Live2D Plugin");return;}updateLoadingText("Initializing Nova...");setTimeout(initLive2D,500);});});});}
startLoading();
</script>
</body>
</html>'''
        with open(path, 'w', encoding='utf-8') as f:
            f.write(html)
def main():
    app=QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setApplicationName("Nova AI Companion")
    app.setApplicationVersion("2.0")
    app.setStyle("Fusion")
    palette=app.palette()
    palette.setColor(palette.Window,QColor(PALETTE['bg_primary']))
    palette.setColor(palette.WindowText,QColor(PALETTE['text_primary']))
    palette.setColor(palette.Base,QColor(PALETTE['bg_secondary']))
    palette.setColor(palette.AlternateBase,QColor(PALETTE['bg_card']))
    palette.setColor(palette.Text,QColor(PALETTE['text_primary']))
    palette.setColor(palette.Button,QColor(PALETTE['bg_card']))
    palette.setColor(palette.ButtonText,QColor(PALETTE['text_primary']))
    palette.setColor(palette.Highlight,QColor(PALETTE['accent']))
    palette.setColor(palette.HighlightedText,QColor('#FFFFFF'))
    app.setPalette(palette)
    font=QFont("Segoe UI",10)
    font.setHintingPreference(QFont.PreferFullHinting)
    app.setFont(font)
    app.setStyleSheet(f"""
        QToolTip {{
            background-color: {PALETTE['bg_card']};
            color: {PALETTE['text_primary']};
            border: 1px solid {PALETTE['border']};
            border-radius: 8px;
            padding: 8px 14px;
            font-family: 'Segoe UI';
            font-size: {FONT_SIZES['tooltip']}px;
        }}
        QMenu {{
            background-color: {PALETTE['bg_secondary']};
            color: {PALETTE['text_primary']};
            border: 1px solid {PALETTE['border']};
            border-radius: 14px;
            padding: 10px;
            font-family: 'Segoe UI';
            font-size: {FONT_SIZES['menu']}px;
        }}
        QMenu::item {{
            padding: 14px 32px;
            border-radius: 8px;
            font-size: {FONT_SIZES['menu']}px;
        }}
        QMenu::item:selected {{
            background: {PALETTE['bg_card']};
            color: {PALETTE['accent_soft']};
        }}
        QMenu::separator {{
            height: 1px;
            background: {PALETTE['border_subtle']};
            margin: 8px 14px;
        }}
        QScrollBar:vertical {{
            background: transparent;
            width: 6px;
            border-radius: 3px;
            margin: 0px;
        }}
        QScrollBar::handle:vertical {{
            background: {PALETTE['border']};
            border-radius: 3px;
            min-height: 30px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: {PALETTE['text_muted']};
        }}
        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        QScrollBar:horizontal {{
            height: 0px;
        }}
    """)
    config=load_config()
    if not config.get("api_key"):
        setup=SetupWindow()
        result=setup.exec_()
        if result!=QDialog.Accepted:
            sys.exit(0)
        global gemini_client
        gemini_client=None
    companion=NovaCompanion()
    companion.show()
    sys.exit(app.exec_())
if __name__=="__main__":
    main()                        
