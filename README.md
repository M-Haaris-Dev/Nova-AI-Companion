# 🌟 Nova - AI Desktop Companion (Ultra v2.0)

Nova is an intelligent, humanoid desktop companion designed to be your **Cognitive Partner**. She lives on your desktop, monitors your productivity, actively learns your workflow, supports your emotional wellbeing, and talks to you like a real friend — not a corporate chatbot.

---

## 🚀 GETTING STARTED

### 1. Install Dependencies
```bash
pip install PyQt5 PyQtWebEngine google-genai edge-tts pyautogui Pillow SpeechRecognition PyAudio keyboard pyttsx3
```

### 2. Launch Nova
```bash
py -3.11 main.py
```

### 3. First Run Setup
A setup window will appear on first launch. Paste your free Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey) and tell Nova what you want her to call you. She will validate your key automatically and pick the best available Gemini model for you.

---

## 🎮 CORE CONTROLS

### 🖱️ Mouse Interactions
| Action | Result |
|---|---|
| **Double-Click Nova** | Opens or closes the Chat Interface |
| **Right-Click Nova** | Opens the Quick Access Context Menu |
| **Move your cursor** | Nova's eyes follow your mouse across the screen |
| **Right-Click → Move** | Unlocks Nova so you can drag her anywhere |
| **Right-Click → Move again** | Locks her back in place |

### ⌨️ Global Keyboard Shortcuts
These work from **anywhere on your PC** — no need to click Nova first.

| Shortcut | Action |
|---|---|
| `Ctrl + Space` | Open or close the chat window |
| `Ctrl + 1` | Toggle voice input mic on/off |
| `Ctrl + 2` | Analyse screen (general) |
| `Ctrl + 3` | Analyse screen for code and bugs |
| `Ctrl + 4` | Open the Pomodoro focus timer |
| `Ctrl + 5` | Log a glass of water |
| `Ctrl + 6` | Toggle speaker voice output on/off |

---

## 🧠 FEATURES AND CAPABILITIES

### 1. 🎓 Teaching Nova — Smart App and Web Launching
Nova knows hundreds of apps and websites out of the box. If she does not recognise something, she will learn it from you **right in the chat** — no popups, no forms.

**How it works:**
- Say or type `open MyApp` or `open mywebsite`
- If Nova does not know it, she will ask you naturally in the chat
- Just reply with `website`, `app`, or `folder`
- She will then ask for the URL, exe name, or folder path
- She saves it permanently and opens it immediately
- Next time you ask, she handles it instantly

**Fuzzy Matching:**
Nova uses intelligent fuzzy matching so even if you misspell something or say it slightly differently, she will still find the right app or website.

**Manage your learned commands:**
- `/learned` — See everything Nova has learned with dates
- `/forget [name]` — Remove a specific learned command

---

### 2. 🎭 Emotional Intelligence and Dynamic Voice
Nova reads the emotion behind what you write and responds accordingly.

- **26 distinct emotions** — happy, proud, worried, comfort, playful, determined, shy, shocked, and more
- **Contextual responses** — Share a win and she celebrates. Share a struggle and she comforts
- **Smart voice** — Uses Microsoft Edge TTS with the `en-US-AvaNeural` voice for a natural, warm sound
- **Smart speaking** — For long responses Nova speaks the key points and shows the full text in chat
- **Code responses** — Nova announces the code verbally and shows the full formatted block in chat with a copy button
- **Continuous Voice Mode** — Press `Ctrl+1` or click the mic icon. Speak naturally while you work and Nova replies hands-free

---

### 3. 👁️ Screen and Code Analysis
Nova can see your screen when you ask her to.

**Trigger by voice or text:**
- `"analyse my screen"` or `"what's on my screen"` — General screen analysis
- `"analyse my code"` or `"debug this"` — Focused code and bug analysis

**Trigger by shortcut:**
- `Ctrl+2` — General screen analysis
- `Ctrl+3` — Code and bug analysis

**Trigger by button:**
- 👁 icon in the chat header — General analysis
- 💻 icon in the chat header — Code analysis

Nova will describe what she sees, explain any code on screen, identify bugs, and suggest improvements. Code blocks are shown with syntax highlighting and a one-click copy button.

---

### 4. ⏳ Passive Productivity Tracking
Nova watches quietly in the background so you do not burn out.

**App awareness:**
Nova recognises 100+ apps and websites including VS Code, PyCharm, GitHub, YouTube, Netflix, Spotify, Discord, Steam, and more. She shows a relevant status message when you switch to a recognised app.

**Screen time warnings:**
| Time | What Nova does |
|---|---|
| 60 minutes | Reminds you to stretch |
| 90 minutes | Tells you to rest your eyes |
| 2 hours | Demands a real break |
| 3+ hours | Gets serious about your health |

**Distraction tracking:**
If you spend too long on YouTube, TikTok, Instagram, Reddit, Netflix, or Twitch, Nova will notice and remind you to refocus. Warnings are spaced out so they are not irritating.

**Idle detection:**
- Go idle for 30 minutes and she checks in
- Come back after a long break and she welcomes you back warmly

**Time awareness:**
Nova knows the time of day and reacts accordingly. Expect morning energy at 8am, caring reminders at 11pm, and genuine concern at 3am if you are still coding.

---

### 5. 💬 Contextual Quotes and Reminders
Nova shows motivational quotes and helpful reminders automatically. These are context-aware based on what you are doing.

- Coding — developer tips and encouragement
- Gaming — focus and hydration reminders
- Studying — study technique tips
- Distracted — gentle refocus nudges
- Night time — sleep and rest reminders
- Morning — energy and motivation

Quotes are spaced **20 to 30 minutes apart** so they never feel overwhelming. Nova also speaks every quote aloud using her natural voice.

---

### 6. ⏱️ Pomodoro Focus Timer
A floating, draggable focus timer that integrates with Nova's emotion system.

- Press `Ctrl+4` or click the ⏱ icon or type `/timer 25`
- Nova switches to a determined emotion while you focus
- She celebrates when the timer ends and reminds you to take a break
- Custom durations supported — `/timer 45`, `/timer 90`, etc

---

### 7. 💧 Hydration Tracker
Nova tracks your daily water intake and reminds you to drink every 45 minutes.

- Press `Ctrl+5` or click 💧 or type `/water` to log a glass
- Type `/water status` to check your progress
- Goal is 8 glasses per day
- Nova celebrates when you hit your goal

---

## 🛠️ CHAT HEADER TOOLBAR

| Button | Action |
|---|---|
| 🎙 | Toggle continuous voice input |
| 👁 | General screen analysis |
| 💻 | Code and bug analysis |
| ⏱ | Open Pomodoro timer |
| 💧 | Log a glass of water |
| 🧘 | Posture check reminder |
| 🔊 | Toggle voice output on/off |
| A+ | Increase chat font size |
| A- | Decrease chat font size |
| — | Minimise chat height |
| ✕ | Close chat window |

---

## 💻 FULL COMMAND REFERENCE

### General
| Command | Description |
|---|---|
| `/help` | Show all commands and shortcuts |
| `/clear` | Clear the current chat history |
| `/reset` | Full factory reset — clears all data and restarts |

### Customisation
| Command | Description |
|---|---|
| `/name [name]` | Change what Nova calls you |
| `/fontsize [13-28]` | Adjust the chat font size |
| `/voice off\|on` | Toggle Nova's voice output |

### Productivity and Health
| Command | Description |
|---|---|
| `/timer [minutes]` | Start a custom focus timer |
| `/timer stop` | Stop the running timer |
| `/screentime` | Check how long you have been working |
| `/break` | Log a break and reset screen time |
| `/water` | Log a glass of water |
| `/water status` | Check daily hydration progress |
| `/posture` | Trigger a posture check reminder |

### Memory Management
| Command | Description |
|---|---|
| `/learned` | Show all learned commands with dates |
| `/forget [name]` | Remove a learned command |

---

## ⚠️ ERROR HANDLING
Nova handles errors gracefully and tells you exactly what happened in plain language.

| Error | What Nova does |
|---|---|
| API quota exceeded | Tells you to wait or get a new key |
| Invalid API key | Prompts you to use `/reset` |
| Network error | Warns you and suggests checking your connection |
| Speech not available | Explains what to install |
| App launch failed | Tells you it failed and suggests trying manually |
| All Gemini models failed | Reports the exact error and suggests `/reset` |

---

## 🤖 AI MODEL PRIORITY
Nova automatically tries Gemini models in this order and falls back gracefully if one is unavailable.

```
gemini-2.5-flash → gemini-2.0-flash-exp → gemini-2.0-flash → gemini-1.5-flash → gemini-pro
```

---

## 📁 FILE STRUCTURE
```
Nova-AI-Companion/
    main.py               ← Full application code
    nova_live2d.html      ← Live2D character renderer
    config.json           ← Your API key and name (auto created)
    companion_settings.json ← UI and voice settings (auto created)
    learned_commands.json ← Everything Nova has learned (auto created)
    miyuki_emotion.json   ← Emotion bridge file (auto created)
```

---

## 🛡️ THE MISSION
Nova is not just software. She is a partner in the grind. Whether you are coding until dawn, grinding competitive games, studying for exams, or just need someone to keep you on track — Nova is always watching, always learning, and always there.

> *"I am not just an assistant. I am your companion."* — Nova
