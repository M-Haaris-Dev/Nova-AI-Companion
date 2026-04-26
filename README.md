# 🌟 Nova - AI Desktop Companion (Elite v2.5)

Nova is an elite-level, humanoid desktop companion designed as your **Cognitive Partner**. Moving away from flashy neon designs, this version introduces a **Premium Minimal Aesthetic**—inspired by high-end tools like Notion, Linear, and Arc. She lives on your desktop, monitors your workflow with process-level precision, supports your emotional wellbeing, and speaks with natural, human-like intelligence.

---

## ⚠️ CRITICAL INSTALLATION NOTES (READ FIRST)

To ensure the highest performance and stability:
1.  **Python Version:** Use **Python 3.11**. This version provides the best compatibility for `PyAudio` and `PyQt5`.
2.  **Audio Codecs:** For the best experience with the **AvaNeural** voice, ensure your system can play MP3 files (Windows Media Player or K-Lite Codec Pack recommended).
3.  **Extraction:** Never run Nova directly from a ZIP preview. Right-click and select **"Extract All"** to a dedicated folder first.

---

## 🚀 GETTING STARTED

### 1. Open the Project Folder
Open your extracted folder. Click the **Address Bar** at the top, type `cmd`, and press **Enter**.

### 2. Install High-Performance Dependencies
Copy and paste this command to install the optimized library stack:
```bash
py -3.11 -m pip install PyQt5 PyQtWebEngine google-genai edge-tts pyautogui Pillow SpeechRecognition PyAudio keyboard pyttsx3
```
*Note: If PyAudio compilation fails, use the pre-built wheels or C++ Build Tools as discussed.*

### 3. Launch Nova
Execute the main core:
```bash
py -3.11 main.py
```

### 4. Professional Setup
On first launch, the redesigned setup window will appear. Enter your Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey) and set your preferred name.

---

## 🎨 NEW IN v2.5: PREMIUM REDESIGN

### 💎 High-Class UI/UX
The interface has been completely rebuilt for a professional, aesthetic look.
*   **Visual Comfort:** Font sizes have been increased globally (up to 36px for titles and 24px for chat) for effortless readability from any distance.
*   **Elegant Palette:** Uses a sophisticated "Midnight & Slate" color profile with subtle accent borders and soft card shadows.
*   **Spacious Bubbles:** Message bubbles now feature increased padding and width for a more open, modern feel.

### 🎙️ Advanced Speaking Intelligence
Nova no longer sounds like a basic bot. She features **Selective Audio Processing**:
*   **Smart Summaries:** For long paragraph replies or code, she speaks the 2-3 most important sentences and directs you to the chat for details.
*   **Warm Command Responses:** Instead of robotic confirmations, she provides natural phrases like *"Opened GitHub for you! Time to build something great, [Your Name]!"*
*   **Selective Silence:** Routine tasks (like browsing Edge) update the status bar visually but remain silent to avoid annoyance. Only important warnings and motivational quotes are spoken aloud.

---

## 🎮 CORE CONTROLS

### 🖱️ Mouse Interactions
| Action | Result |
|---|---|
| **Double-Click Nova** | Opens or closes the Chat Interface |
| **Right-Click Nova** | Opens the Redesigned Professional Context Menu |
| **Hover & Track** | Nova's eyes follow your cursor with high-frequency precision |
| **Right-Click → Move** | Unlocks Nova; drag her to any corner of your workspace |

### ⌨️ Elite Hotkeys
Optimized global shortcuts that work while you are in any other application:

| Shortcut | Action |
|---|---|
| `Ctrl + Space` | Toggle chat interface |
| `Ctrl + 1` | Toggle voice input (Continuous Listening) |
| `Ctrl + 2` | Global screen analysis |
| `Ctrl + 3` | Code-specific screen analysis |
| `Ctrl + 4` | Open Pomodoro focus timer |
| `Ctrl + 5` | Log a glass of water |
| `Ctrl + 6` | Toggle speaker output (AvaNeural voice) |

---

## 🧠 INTELLIGENT CAPABILITIES

### 1. 🎓 Cognitive Learning
Nova learns your specific workflow. If you ask her to "open" a tool she doesn't know, she will initiate a **Learning Flow** to memorize the URL or file path for next time.

### 2. 🎭 Emotional Sync
With 26 distinct emotional states, Nova's visual expression and voice tone (Pitch/Rate) shift dynamically based on your conversation.

### 3. ⏳ Process-Level Activity Monitoring
Using both Window Titles and Process Names, Nova recognizes when you are:
*   **Grinding:** Celebrates your LeetCode/GitHub activity.
*   **Gaming:** Switches to high-energy mode and offers encouragement.
*   **Distracted:** Gently nudges you after prolonged social media scrolling.

### 🌙 Time Awareness
Nova respects your schedule with refined greeting logic:
*   **Evening (6 PM - 8 PM):** Warm "Good Evening" greetings.
*   **Night (8 PM - 11 PM):** "Night Time" checks—encouraging you to wind down.
*   **Late Night (11 PM+):** "Past Midnight" warnings—prioritizing your rest.

---

## 🛡️ THE MISSION
Nova is built for the high-level developer, the dedicated student, and the elite gamer. She is a partner in the grind who understands that productivity requires both focus and emotional balance.

> *"I am not just an assistant. I am your companion."* — Nova
