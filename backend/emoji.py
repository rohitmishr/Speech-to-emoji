import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"
from backend.app import app
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from transformers import AutoTokenizer, AutoModel
from vosk import Model, KaldiRecognizer
import torch
import sounddevice as sd
import numpy as np
import asyncio
import queue
import logging
import json
import time


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load Vosk model
try:
    vosk_model = Model("models/vosk-model-en-us-0.22")
    logger.info("✅ Vosk model loaded")
except Exception as e:
    logger.error(f"❌ Failed to load Vosk model: {e}")
    vosk_model = None

# Load BERT tokenizer and model
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
model = AutoModel.from_pretrained("bert-base-uncased")

# Emoji keyword map
EMOJI_KEYWORDS = {
    "😂": ["laugh", "hilarious", "funny", "lol", "haha", "comedy"],
    "😊": ["happy", "joy", "smile", "glad", "cheerful", "delighted"],
    "😢": ["sad", "cry", "upset", "depressed", "tears", "grief"],
    "😠": ["angry", "mad", "furious", "rage", "annoyed", "irritated"],
    "❤️": ["love", "heart", "romance", "affection", "adorable", "cherish"],
    "🎉": ["celebrate", "party", "congrats", "woohoo", "festive"],
    "🤔": ["think", "ponder", "consider", "wonder", "contemplate"],
    "🍕": ["pizza", "food", "hungry", "cheese", "pepperoni", "eat", "eating"],
    "🍔": ["burger", "food", "hungry", "fast food", "eat", "eating"],
    "💃": ["dance", "dancing", "party", "move", "groove"],
    "🎵": ["music", "song", "sing", "melody", "tune"],
    "⚽": ["soccer", "football", "sports", "game", "play"],
    "🏀": ["basketball", "sports", "game", "play", "hoops"],
    "🐶": ["dog", "puppy", "pet", "animal", "woof"],
    "🐱": ["cat", "kitten", "pet", "animal", "meow"],
    "🚗": ["car", "drive", "driving", "vehicle", "road"],
    "✈️": ["plane", "airplane", "fly", "flying", "travel"],
    "👋": ["hello","hi"],
    "🙏": ["please", "thank you", "gratitude", "appreciate", "thanks", "namaste"],
    # Add more emojis as needed
}


emoji_embeddings = {}

def get_embedding(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=128, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.last_hidden_state.mean(dim=1).squeeze().numpy()

def initialize_emoji_embeddings():
    for emoji, keywords in EMOJI_KEYWORDS.items():
        keyword_embeds = [get_embedding(k) for k in keywords]
        emoji_embeddings[emoji] = np.mean(keyword_embeds, axis=0)

initialize_emoji_embeddings()

def get_emoji_for_text(text: str) -> str:
    try:
        text_embed = get_embedding(text)
        best_emoji = "❓"
        best_score = -1

        for emoji, embed in emoji_embeddings.items():
            sim = np.dot(text_embed, embed) / (np.linalg.norm(text_embed) * np.linalg.norm(embed))
            if sim > best_score:
                best_score = sim
                best_emoji = emoji

        return best_emoji if best_score > 0.3 else "❓"
    except Exception as e:
        logger.error(f"Embedding error: {e}")
        return "❓"


async def recognize_once(timeout=5.0, max_duration=10.0):
    q = queue.Queue()
    rec = KaldiRecognizer(vosk_model, 16000)

    def callback(indata, frames, time_info, status):
        if status:
            logger.warning(f"Sounddevice warning: {status}")
        q.put(bytes(indata))

    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                           channels=1, callback=callback):
        logger.info("🎙️ Listening for speech...")
        start_time = time.time()
        while time.time() - start_time < max_duration:
            try:
                data = q.get(timeout=timeout)
            except queue.Empty:
                logger.warning("⏱️ No speech detected within timeout.")
                return ""

            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                text = result.get("text", "").strip()
                if text:
                    logger.info(f"🗣️ Recognized: {text}")
                    return text

        logger.warning("⏹️ Max duration reached with no valid speech.")
        return ""

@app.post("/listen")
async def listen_and_respond():
    try:
        text = await recognize_once()
        emoji = get_emoji_for_text(text)
        return {"text": text, "emoji": emoji}
    except Exception as e:
        return {"error": str(e)}

@app.get("/")
async def index():
    return HTMLResponse(html_page)




html_page = """
<!DOCTYPE html>
<html>
<head>
    <title>🎤 Chat with Emojis</title>
    <style>
        body { font-family: Arial; background: #f4f4f4; padding: 2rem; }
        #chatbox { max-width: 600px; margin: auto; background: white; border-radius: 10px; padding: 1rem; }
        .msg { padding: 0.5rem; margin: 0.5rem 0; border-radius: 8px; }
        .user { background: #dff9fb; text-align: right; }
        .bot { background: #f1f2f6; text-align: left; }
        #micBtn { font-size: 1.2rem; padding: 0.6rem 1rem; border: none; background: #0984e3; color: white; border-radius: 5px; cursor: pointer; }
        #micBtn:hover { background: #74b9ff; }
        .helper-text {
        font-size: 1rem;
        color: #666;
        margin-bottom: 1rem;
        font-style: italic;
        }
    </style>
</head>
<body>
    <div id="chatbox">
        <h2>🎙️ Chat with Emoji Suggestion</h2>
        <p class="helper-text">🔊 Tap the mic and say something like "pizza", "happy", or "dance" to get a matching emoji!</p>
        <div id="messages"></div>
        <button id="micBtn">🎤 Tap to Speak</button>
    </div>

    <script>
        const micBtn = document.getElementById("micBtn");
        const messages = document.getElementById("messages");

        micBtn.onclick = async () => {
            micBtn.disabled = true;
            micBtn.textContent = "🎙️ Listening...";
            try {
                const res = await fetch("/listen", { method: "POST" });
                const data = await res.json();
                if (data.text) {
                    addMessage(data.text, "user");
                    addMessage(data.emoji, "bot");
                } else {
                    addMessage("Couldn't hear you properly.", "bot");
                }
            } catch (err) {
                addMessage("Error: " + err.message, "bot");
            }
            micBtn.textContent = "🎤 Tap to Speak";
            micBtn.disabled = false;
        };

        function addMessage(text, sender) {
            const div = document.createElement("div");
            div.className = `msg ${sender}`;
            div.textContent = text;
            messages.appendChild(div);
            messages.scrollTop = messages.scrollHeight;
        }
    </script>
</body>
</html>
"""
