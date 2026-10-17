
import { useState } from "react";
import "./Assistant.css";

const API_URL = "http://127.0.0.1:8000/api/assistant/chat";

export default function Assistant() {
  const [isOpen, setIsOpen] = useState(false);
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      text: "Hi! Welcome to Bluewater. How can I help with your boat trip?",
    },
  ]);
  const [loading, setLoading] = useState(false);

  async function sendMessage(event) {
    event.preventDefault();

    const text = message.trim();
    if (!text || loading) return;

    setMessages((previous) => [
      ...previous,
      { role: "user", text },
    ]);
    setMessage("");
    setLoading(true);

    try {
      const response = await fetch(API_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: text }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Unable to contact the assistant.");
      }

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          text: data.reply,
        },
      ]);
    } catch (error) {
      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          text: `Sorry, I couldn't connect. ${error.message}`,
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="bluewater-assistant">
      {isOpen && (
        <section className="assistant-panel">
          <header className="assistant-header">
            <div>
              <strong>Bluewater AI</strong>
              <div className="assistant-status">Powered by Gemini</div>
            </div>
            <button
              type="button"
              className="assistant-close"
              onClick={() => setIsOpen(false)}
              aria-label="Close assistant"
            >
              ×
            </button>
          </header>

          <div className="assistant-messages" aria-live="polite">
            {messages.map((item, index) => (
              <div
                key={index}
                className={`assistant-message ${item.role}`}
              >
                {item.text}
              </div>
            ))}

            {loading && (
              <div className="assistant-message assistant">
                Thinking...
              </div>
            )}
          </div>

          <form className="assistant-form" onSubmit={sendMessage}>
            <input
              value={message}
              onChange={(event) => setMessage(event.target.value)}
              placeholder="Ask about boat trips..."
              aria-label="Message the assistant"
              disabled={loading}
            />
            <button type="submit" disabled={loading || !message.trim()}>
              Send
            </button>
          </form>
        </section>
      )}

      <button
        type="button"
        className="assistant-float"
        onClick={() => setIsOpen((open) => !open)}
        aria-label={isOpen ? "Close AI assistant" : "Open AI assistant"}
      >
        {isOpen ? "×" : "✦"}
      </button>
    </div>
  );
}
