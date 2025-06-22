function injectMicButton() {
    const chatInput = document.querySelector('footer div[contenteditable="true"]');
    const inputParent = chatInput?.parentNode;
    if (!chatInput || !inputParent || document.getElementById("voiceToEmojiBtn")) return;
  
    const micBtn = document.createElement("button");
    micBtn.id = "voiceToEmojiBtn";
    micBtn.innerHTML = "🎤";
    micBtn.title = "Voice to Emoji";
    micBtn.style = `
      margin-left: 6px;
      background: transparent;
      border: none;
      font-size: 22px;
      cursor: pointer;
      padding: 4px;
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: 50%;
      transition: background 0.2s ease;
    `;
    micBtn.onmouseover = () => micBtn.style.background = "#2a2a2a";
    micBtn.onmouseout = () => micBtn.style.background = "transparent";
  
    const statusText = document.createElement("div");
    statusText.id = "voiceStatusMsg";
    statusText.style = `
      font-size: 12px;
      color: #888;
      margin-top: 5px;
      text-align: center;
      font-style: italic;
    `;
  
    micBtn.onclick = async () => {
      micBtn.innerHTML = "🎙️";
      micBtn.disabled = true;
  
      try {
        const beep = new Audio("data:audio/wav;base64,UklGRiQAAABXQVZFZm10IBAAAAABAAEAESsAACJWAAACABAAZGF0YRAAAAD//wD/AP8A/wD/AP8A/wD/AP8A/wD/AP8A/wD/AP8A/wD/AP8A/wD/AP8A/wD/AP8A/wD/AP8AAP8A/wD/AP8A//8AAAAA");
        await beep.play();
        
  
        // ⏳ Delay slightly before showing "Listening..."
        await new Promise(resolve => setTimeout(resolve, 200));
        statusText.textContent = "🎧 Listening...";
  
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const recorder = new MediaRecorder(stream);
        const chunks = [];
  
        recorder.ondataavailable = (e) => chunks.push(e.data);
  
        recorder.onstop = async () => {
          const blob = new Blob(chunks, { type: "audio/webm" });
          const form = new FormData();
          form.append("audio", blob);
  
          try {
            const res = await fetch("http://localhost:8000/listen", {
              method: "POST",
              body: form
            });
  
            const data = await res.json();
            const emoji = data.emoji || "❓";
  
            if (emoji !== "❓") {
              const range = document.createRange();
              range.selectNodeContents(chatInput);
              range.deleteContents();
  
              chatInput.focus();
              document.execCommand("insertText", false, emoji);
              chatInput.dispatchEvent(new InputEvent("input", { bubbles: true }));
  
              const sendBtn = document.querySelector('[data-testid="send"]');
              if (sendBtn) sendBtn.click();
  
              statusText.textContent = `✅ "${data.text}" → ${emoji}`;
            } else {
              statusText.textContent = `😕 No emoji match for: "${data.text}"`;
            }
          } catch (err) {
            statusText.textContent = `❌ Server error: ${err.message}`;
          }
  
          micBtn.innerHTML = "🎤";
          micBtn.disabled = false;
        };
  
        recorder.start();
        setTimeout(() => recorder.stop(), 2500);
      } catch (err) {
        statusText.textContent = `❌ Mic error: ${err.message}`;
        micBtn.innerHTML = "🎤";
        micBtn.disabled = false;
      }
    };
  
    inputParent.appendChild(micBtn);
  
    const footer = document.querySelector("footer");
    if (footer && !document.getElementById("voiceStatusMsg")) {
      footer.appendChild(statusText);
    }
  }
  
  setInterval(injectMicButton, 2000);
  