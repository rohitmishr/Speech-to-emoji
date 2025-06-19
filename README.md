# Speech-to-emoji
This is AI tool that recognize your word and gives emoji.
![alt text](image.png)




# Steps to install:
- Clone this repo https://github.com/rohitmishr/Speech-to-emoji.git
- Follow the A
- create an env using ```python3 -m venv emoji-ai-env```
- Activate the venv ``` source emoji-ai-env/bin/activate```
- Run ```python3 run.py```
### Note: If something fails please install the python packages


### A: 
- curl -L -o vosk-model-en-us-0.22.zip https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip
- unzip vosk-model-en-us-0.22.zip
- move this vosk-model-en-us-0.22.zip unziped one inside models






## 🧠 AI Tools & Technologies Used
``` This project combines cutting-edge AI libraries for offline speech recognition and natural language understanding to suggest relevant emojis based on spoken phrases.

🎤 Speech Recognition: Vosk
Model: vosk-model-en-us-0.22

Function: Converts spoken audio into text.

Highlights:

Lightweight and fully offline.

Built on the Kaldi speech recognition toolkit.

Supports real-time audio streaming.

```

## 🧠 Natural Language Understanding: Hugging Face Transformers
Model: bert-base-uncased

Function: Generates sentence embeddings to understand user intent.

Highlights:

Powered by BERT, a pre-trained transformer model.

Captures contextual meaning of speech for semantic similarity.

## ⚙️ Backend Intelligence: PyTorch
Function: Executes the BERT model for embedding generation.

Role: High-performance tensor computations for AI inference.

➗ Semantic Matching: NumPy
Function: Calculates cosine similarity between spoken text and emoji keyword embeddings.

Purpose: Determines the most semantically relevant emoji.

## 🚀 Web Framework: FastAPI
Function: Serves as the backend web API.

Features:

Async support for speech streaming.

Exposes REST endpoints like /listen for real-time interaction.

## 💬 Frontend: Vanilla JavaScript + HTML
Function: Captures user interaction via a microphone button and displays emoji suggestions.

Features: Chat-like interface with real-time feedback.

## ✅ Flow Overview

graph TD;
```    User[🎤 User Speaks] --> Vosk[Vosk: Speech-to-Text];
    Vosk --> Text[📝 Recognized Text];
    Text --> BERT[BERT: Generate Embedding];
    BERT --> Match[🔍 Cosine Similarity with Emoji Keywords];
    Match --> Emoji[😄 Suggested Emoji];
    Emoji --> UI[🖥️ Display in Web Interface];

```





# Happy Coding 👨‍💻