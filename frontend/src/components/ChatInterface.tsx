"use client";

import { useEffect, useRef, useState } from "react";
import { Send, Mic, ArrowLeft, Star } from "lucide-react";
import { useConversation } from "@/lib/conversation";
import { RatingModal } from "@/components/RatingModal";

/* ── Conclusive phrases that trigger the rating prompt ──────── */
const CONCLUSIVE_PHRASES = [
  "thank you",
  "thanks",
  "that's all",
  "thats all",
  "bye",
  "goodbye",
  "good bye",
  "no more",
  "i'm done",
  "im done",
  "that will be all",
  "nothing else",
  "okay thanks",
  "ok thanks",
  "ok thank you",
  "okay thank you",
];

function isConclusive(text: string): boolean {
  const lower = text.toLowerCase().trim();
  return CONCLUSIVE_PHRASES.some((p) => lower.includes(p));
}

interface ChatInterfaceProps {
  user: { name: string };
  onSwitchToVoice: () => void;
  onLogout: () => void;
}

export function ChatInterface({
  user,
  onSwitchToVoice,
  onLogout,
}: ChatInterfaceProps) {
  const { chatState, sendMessage } = useConversation();
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [showRating, setShowRating] = useState(false);
  const [hasRated, setHasRated] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-scroll on new messages
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [chatState.messages, chatState.isTyping]);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height =
        Math.min(textareaRef.current.scrollHeight, 128) + "px";
    }
  }, [input]);

  const handleSend = async (override?: string) => {
    const text = override ?? input;
    if (!text.trim() || sending) return;

    if (!override) setInput("");
    setSending(true);

    await sendMessage(text, user.name);
    setSending(false);

    // Check if user said something conclusive → show rating
    if (!hasRated && isConclusive(text)) {
      setTimeout(() => setShowRating(true), 1500);
    }
  };

  const handleRatingSubmit = (rating: number) => {
    console.log("User rated:", rating);
    setHasRated(true);
  };

  return (
    <div className="flex flex-col h-full w-full bg-transparent relative">
      {/* ── Rating Modal ── */}
      <RatingModal
        isOpen={showRating}
        onClose={() => setShowRating(false)}
        onSubmit={handleRatingSubmit}
      />

      {/* ── Header ── */}
      <header className="flex items-center justify-between px-4 py-3 border-b border-border bg-background/80 backdrop-blur-md sticky top-0 z-10">
        <div className="flex items-center gap-3">
          <button
            onClick={onLogout}
            className="p-2 rounded-full text-zinc-400 hover:text-white hover:bg-zinc-800 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
          <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-sky-400 to-blue-600 flex items-center justify-center text-white font-bold text-xs ring-2 ring-background shadow-sm">
            R
          </div>
          <div>
            <h2 className="text-sm font-semibold text-foreground leading-tight">
              RetAIl
            </h2>
            <p className="text-[10px] text-muted-foreground">
              AI Shopping Assistant
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {/* Rate Us button */}
          {!hasRated && (
            <button
              onClick={() => setShowRating(true)}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-yellow-500/10 border border-yellow-500/20 text-yellow-400 text-xs font-medium hover:bg-yellow-500/20 transition-colors active:scale-95"
            >
              <Star className="w-3 h-3 fill-yellow-400" />
              Rate Us
            </button>
          )}
          <span className="text-xs text-zinc-500">{user.name}</span>
          <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
        </div>
      </header>

      {/* ── Chat Area ── */}
      <div
        className="flex-1 overflow-y-auto p-4 space-y-5 scroll-smooth pb-28"
        ref={scrollRef}
      >
        {/* Welcome if empty */}
        {chatState.messages.length === 0 && (
          <div className="flex justify-start w-full">
            <div className="flex flex-col max-w-[85%] items-start">
              <div className="px-4 py-3 rounded-2xl rounded-bl-none text-sm leading-relaxed bg-secondary text-secondary-foreground border border-border">
                Welcome, {user.name}! I&apos;m RetAIl — your AI shopping
                assistant. Ask me about any product.
              </div>
            </div>
          </div>
        )}

        {chatState.messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex w-full ${
              msg.sender === "user" ? "justify-end" : "justify-start"
            }`}
          >
            <div
              className={`flex flex-col max-w-[85%] ${
                msg.sender === "user" ? "items-end" : "items-start"
              }`}
            >
              {/* Bubble */}
              <div
                className={`px-4 py-3 rounded-2xl text-sm leading-relaxed shadow-sm whitespace-pre-wrap ${
                  msg.sender === "user"
                    ? "bg-primary text-primary-foreground rounded-br-none"
                    : "bg-secondary text-secondary-foreground rounded-bl-none border border-border"
                }`}
              >
                {msg.text}
              </div>

              {/* Suggestions */}
              {msg.sender === "ai" && msg.suggestions && (
                <div className="flex flex-wrap gap-2 mt-2.5">
                  {msg.suggestions.map((s) => (
                    <button
                      key={s}
                      onClick={() => handleSend(s)}
                      className="px-3 py-1.5 text-xs font-medium text-primary bg-primary/10 border border-primary/20 rounded-full hover:bg-primary/20 transition-colors active:scale-95"
                    >
                      {s}
                    </button>
                  ))}
                </div>
              )}

              {/* Timestamp */}
              <span className="text-[10px] text-muted-foreground mt-1 px-1">
                {msg.timestamp.toLocaleTimeString([], {
                  hour: "2-digit",
                  minute: "2-digit",
                })}
              </span>
            </div>
          </div>
        ))}

        {/* Typing indicator */}
        {chatState.isTyping && (
          <div className="flex justify-start w-full">
            <div className="bg-secondary px-4 py-3 rounded-2xl rounded-bl-none border border-border flex space-x-1.5 items-center h-10 w-16">
              <div className="w-1.5 h-1.5 bg-muted-foreground rounded-full animate-bounce delay-0" />
              <div className="w-1.5 h-1.5 bg-muted-foreground rounded-full animate-bounce delay-150" />
              <div className="w-1.5 h-1.5 bg-muted-foreground rounded-full animate-bounce delay-300" />
            </div>
          </div>
        )}
      </div>

      {/* ── Input Area ── */}
      <div className="absolute bottom-0 left-0 right-0 p-3 bg-background/90 backdrop-blur-lg border-t border-border z-20 pb-safe">
        <div className="relative flex items-end gap-2 bg-secondary rounded-3xl border border-border/50 shadow-sm focus-within:ring-2 focus-within:ring-primary/50 focus-within:border-transparent transition-all p-1.5">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSend();
              }
            }}
            placeholder="Ask about products..."
            className="w-full bg-transparent border-none text-sm text-foreground placeholder-muted-foreground focus:outline-none focus:ring-0 px-3 py-2.5 min-h-[44px] max-h-32 resize-none overflow-hidden"
            rows={1}
          />

          {/* Mic switch */}
          <button
            onClick={onSwitchToVoice}
            className="p-2.5 rounded-full text-muted-foreground hover:bg-muted hover:text-foreground transition-colors active:scale-95"
            title="Switch to Voice"
          >
            <Mic className="w-4 h-4" />
          </button>

          {/* Send */}
          <button
            onClick={() => handleSend()}
            disabled={!input.trim() || sending}
            className="p-2.5 rounded-full bg-primary text-primary-foreground shrink-0 hover:opacity-90 disabled:opacity-40 disabled:cursor-not-allowed transition-all active:scale-90"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
