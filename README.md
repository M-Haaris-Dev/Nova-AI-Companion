# 🌟 Nova - AI Desktop Companion (Ultra v2.0)

Nova is an intelligent, humanoid desktop companion designed to be your **Cognitive Partner**. She lives on your desktop, monitors your productivity, actively learns your workflow, supports your emotional wellbeing, and talks to you like a real friend — not a corporate chatbot.

---

## ⚠️ CRITICAL INSTALLATION NOTES (READ FIRST)

To avoid the most common errors, please ensure:
1.  **Python Version:** Use **Python 3.11**. (Newer versions like 3.12 or 3.14 often cause `PyAudio` and `PyQt5` installation failures).
2.  **Extraction:** Do **NOT** run Nova from a ZIP preview. Right-click the ZIP and select **"Extract All"** to your Desktop/Documents before starting.

---

## 🚀 GETTING STARTED

### 1. Open the Project Folder
Open the extracted folder in File Explorer. Click the **Address Bar** at the top, type `cmd`, and press **Enter**. This opens the terminal exactly where you need to be.

### 2. Install Dependencies
Copy and paste this command to install all necessary libraries at once:
```bash
py -3.11 -m pip install PyQt5 PyQtWebEngine google-genai edge-tts pyautogui Pillow SpeechRecognition PyAudio keyboard pyttsx3
```
*Note: If PyAudio fails, install `pipwin` first, then use `pipwin install pyaudio`.*

### 3. Launch Nova
Run the following command:
```bash
py -3.11 main.py
```

### 4. First Run Setup
A setup window will appear. Paste your free Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey) and tell Nova what to call you. She will validate your key automatically.

---

## 🔧 TROUBLESHOOTING (COMMON ERRORS)

*   **`ModuleNotFoundError: No module named 'PyQt5.QtWebEngineWidgets'`**
    *   *Fix:* Run `pip install PyQtWebEngine`.
*   **`Microsoft Visual C++ 14.0 is required` during PyAudio install.**
    *   *Fix:* This is caused by using a Python version newer than 3.11. Switch to **Python 3.11** for the easiest fix.
*   **`can't open file 'main.py': [Errno 2] No such file or directory`**
    *   *Fix:* You are in the wrong folder in your terminal. Use the "Address Bar" trick mentioned in Step 1 of Getting Started.

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
Nova knows hundreds of apps and websites out of the box. If she does not recognise something, she will learn it from you **right in the chat**.
- Say `open MyApp` or `open mywebsite`.
- If she doesn't know it, tell her the URL or path when she asks.
- Commands: `/learned` (see all), `/forget [name]` (remove).

### 2. 🎭 Emotional Intelligence and Dynamic Voice
Nova reacts to your mood with **26 distinct emotions**.
- **Contextual responses:** She celebrates wins and comforts struggles.
- **Natural Voice:** Uses Microsoft Edge TTS (`en-US-AvaNeural`).
- **Continuous Voice Mode:** Hands-free conversation via `Ctrl+1`.

### 3. 👁️ Screen and Code Analysis
Nova "sees" your screen via Gemini's vision capabilities.
- Trigger with `"analyse my screen"` or shortcuts `Ctrl+2` (General) / `Ctrl+3` (Code).
- She identifies bugs, suggests improvements, and provides formatted code blocks with a copy button.

### 4. ⏳ Passive Productivity Tracking
Nova monitors your active apps (VS Code, GitHub, YouTube, etc.) to help you stay focused.
- **Health Reminders:** Every 60-90 minutes, she suggests stretching or eye rests.
- **Distraction Nudges:** Notices if you spend too much time on social media or streaming sites.

### 5. ⏱️ Focus & Hydration
- **Pomodoro Timer:** `/timer 25` or `Ctrl+4` to start a focus session.
- **Hydration:** `/water` or `Ctrl+5` to log water intake. Nova reminds you to drink every 45 minutes.

---

## 🛠️ CHAT HEADER TOOLBAR

| Button | Action |
|---|---|
| 🎙 | Toggle voice input |
| 👁 | General screen analysis |
| 💻 | Code and bug analysis |
| ⏱ | Pomodoro timer |
| 🔊 | Toggle voice output |
| A+/A- | Font size adjustment |

---

## 📁 FILE STRUCTURE
```
Nova-AI-Companion/
    main.py               ← Full application code
    nova_live2d.html      ← Live2D character renderer
    config.json           ← API key and user name
    learned_commands.json ← User-taught apps and links
```

---

## 🛡️ THE MISSION
Nova is not just software. She is a partner in the grind. Whether you are coding until dawn, gaming, or studying—Nova is always watching, always learning, and always there.

> *"I am not just an assistant. I am your companion."* — Nova

***
