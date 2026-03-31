# 🌟 Nova - AI Desktop Companion (Ultra v2.0)

Nova is an intelligent, humanoid desktop companion designed to be your "Cognitive Twin." She lives on your desktop, monitors your productivity, actively learns your workflow, and supports your emotional wellbeing.

---

## 🚀 GETTING STARTED

1. **Install Dependencies:** 
   ```bash
   pip install PyQt5 PyQtWebEngine google-genai edge-tts pyautogui Pillow SpeechRecognition PyAudio keyboard
   ```
2. **Launch Nova:** 
   ```bash
   python main.py
   ```
3. **First Run Setup:** A setup window will appear. Paste your Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey). You can also tell Nova what you want her to call you!

---

## 🎮 USER MANUAL: CORE CONTROLS

### 🖱️ Mouse Interactions
* **Eye Tracking:** Nova's eyes will naturally follow your mouse cursor across the screen.
* **Double-Click Nova:** Instantly opens or closes the Chat Interface.
* **Right-Click Nova:** Opens the **Guardian Menu**. From here you can access quick tools (Timer, Water, Break), view Recent Code snippets, toggle Move Mode, or **Reset** the app.
* **Drag & Move:** Right-click Nova and select **"Move"** to unlock her. Place her anywhere on your screen, then right-click and select "Move" again to lock her in place.

### ⌨️ Global Hotkeys
* **`Ctrl + Space`**: Show/hide Nova's chat interface from *anywhere* on your PC, without needing to click her.

---

## 🧠 ADVANCED FEATURES & CAPABILITIES

### 1. 🎓 Teaching Nova (Smart App & Web Launching)
Nova can open almost anything, but if she doesn't know a specific app or website, **she will learn it.**
* **How it works:** Type `open [Name]` (e.g., `open MyProject`).
* **The Learning UI:** If Nova doesn't recognize it, a popup will appear asking you to teach her. 
* **Choose the Target:** You can point her to an **Application (.exe)**, a **Website URL**, or a **Local Folder**.
* **Memory:** She saves this permanently. Next time you ask, she will open it instantly! *(View your learned commands with `/learned`)*.

### 2. 🎭 Emotional Intelligence & Dynamic Voice
Nova doesn't just read text; she feels it.
* **Contextual Emotions:** If you type something sad, Nova switches to a comforting posture and a gentle, softer voice. If you share a win, she gets visibly excited and raises her voice pitch to celebrate with you.
* **Smart Voice Timing:** Nova will speak to you immediately, and the text will type out naturally on screen, mimicking a real human conversation.
* **Continuous Voice Mode:** Click the **🎙 icon**. Nova will continuously listen to your mic. Speak naturally while you work, and she will reply hands-free.

### 3. 👁️ Screen & Code Analysis (Vision AI)
Nova can see what you are doing (when you ask her to).
* **General Analysis:** Ask *"What's on my screen?"* or click the **👁 icon**. Nova will look at your screen and give you helpful observations or context.
* **Code Debugging:** Stuck on a bug? Click the **💻 icon** or say *"Analyze my code"*. Nova will scan your IDE, explain the logic, and point out bugs. Code responses are formatted in clean, copyable blocks.

### 4. ⏳ Passive Productivity Tracking
Nova watches your back so you don't burn out.
* **Distraction Warnings:** If you spend too long on YouTube, TikTok, or Reddit, Nova will gently (or sternly) remind you to get back to work.
* **Screen Time & Idle Checks:** She tracks how long you've been working. If you've been staring at the screen for 2+ hours, she will demand you take a break. If you go idle for a long time, she will welcome you back when you return.
* **Time Awareness:** She knows the time of day. Expect fresh greetings in the morning, and worried reminders to go to sleep if you are coding at 3 AM.

---

## 🛠️ THE HEADER TOOLBOX
At the top of Nova's chat window, you have quick access to essential tools:
* **🎙 (Mic):** Toggle Continuous Voice Input.
* **👁 (Eye):** Capture screen and perform General AI Vision Analysis.
* **💻 (Code):** Capture screen and perform Code/Logic Debugging.
* **⏱ (Timer):** Opens the floating Pomodoro Focus Timer.
* **💧 (Water):** Quickly log a glass of water towards your daily goal.
* **🧘 (Posture):** Triggers a manual posture check reminder.
* **🔊 (Speaker):** Toggle Nova's voice output on/off.

---

## 💻 SYSTEM COMMANDS (CHEAT SHEET)
Type these directly into the chat box for instant system actions:

**General:**
* `/help` - Show all commands.
* `/clear` - Wipes the current chat history for a fresh start.
* `/reset` - **Full Factory Reset.** Clears API keys, memory, and learned apps, then restarts Nova.

**Customization:**
* `/name [new name]` - Change what Nova calls you.
* `/fontsize [13-28]` - Adjust the chat UI font size.
* `/sound off|on` - Toggle UI sound effects.
* `/voice off|on` - Toggle Nova's Text-to-Speech voice.

**Productivity & Health:**
* `/timer [minutes]` - Start a custom focus timer (e.g., `/timer 45`). Stop it with `/timer stop`.
* `/screentime` - Ask Nova how long you've been working this session.
* `/break` - Manually log a break and reset your screen time counters.
* `/water` - Log a glass of water. Type `/water status` to see your daily progress.
* `/posture` - Force a posture check reminder.

**Memory Management:**
* `/learned` - Displays a list of all custom apps/links you have taught Nova.
* `/forget [name]` - Makes Nova forget a custom app or link you taught her.

---

## ⚠️ SMART ERROR HANDLING
If something goes wrong, Nova won't just crash. She will tell you exactly what happened in the chat:
* **API Quota Hit:** She will let you know if you've exhausted your free Gemini requests.
* **Network Issues:** She will warn you if your internet drops.
* **Invalid Key:** If your API key expires, she will prompt you to use the `/reset` command to enter a new one.

---

## 🛡️ THE MISSION
Nova isn't just software; she is a partner in the grind. Whether you are coding until dawn, grinding competitive games, or just need someone to organize your workflow, Nova is always watching, always learning, and always there.