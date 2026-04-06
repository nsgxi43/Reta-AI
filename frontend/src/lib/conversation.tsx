"use client";

import {
  createContext,
  useContext,
  useState,
  useCallback,
  useRef,
  type ReactNode,
} from "react";
import { Message, ChatState } from "@/types/chat";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface ConversationContextValue {
  chatState: ChatState;
  sendMessage: (text: string, userName: string) => Promise<string>;
  addUserMessage: (text: string) => void;
  addAiMessage: (text: string, suggestions?: string[]) => void;
  setTyping: (v: boolean) => void;
}

const ConversationContext = createContext<ConversationContextValue | null>(null);

export function ConversationProvider({ children }: { children: ReactNode }) {
  const [chatState, setChatState] = useState<ChatState>({
    messages: [],
    isTyping: false,
  });

  // Keep a ref so async callbacks always see latest messages
  const messagesRef = useRef(chatState.messages);
  messagesRef.current = chatState.messages;

  const addUserMessage = useCallback((text: string) => {
    const msg: Message = {
      id: Date.now().toString(),
      sender: "user",
      text,
      timestamp: new Date(),
    };
    setChatState((prev) => ({
      ...prev,
      messages: [...prev.messages, msg],
    }));
  }, []);

  const addAiMessage = useCallback(
    (text: string, suggestions?: string[]) => {
      const msg: Message = {
        id: (Date.now() + 1).toString(),
        sender: "ai",
        text,
        timestamp: new Date(),
        suggestions,
      };
      setChatState((prev) => ({
        ...prev,
        messages: [...prev.messages, msg],
        isTyping: false,
      }));
    },
    []
  );

  const setTyping = useCallback((v: boolean) => {
    setChatState((prev) => ({ ...prev, isTyping: v }));
  }, []);

  /**
   * Send a message through the RAG backend.
   * Returns the AI response text (useful for TTS in voice mode).
   */
  const sendMessage = useCallback(
    async (text: string, userName: string): Promise<string> => {
      addUserMessage(text);
      setTyping(true);

      try {
        const res = await fetch(`${API_URL}/chat`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ query: text, user_name: userName }),
        });

        if (!res.ok) throw new Error(`HTTP ${res.status}`);

        const data = await res.json();

        const suggestions =
          data.products && Array.isArray(data.products)
            ? data.products
                .map((p: any) => p.product_name || p.name)
                .filter(Boolean)
                .slice(0, 3)
            : undefined;

        const responseText =
          data.response || "Sorry, I couldn't find anything.";

        addAiMessage(responseText, suggestions);
        return responseText;
      } catch (err) {
        console.error("Backend error:", err);
        const fallback =
          "Sorry, I'm having trouble connecting. Please try again.";
        addAiMessage(fallback);
        return fallback;
      }
    },
    [addUserMessage, addAiMessage, setTyping]
  );

  return (
    <ConversationContext.Provider
      value={{ chatState, sendMessage, addUserMessage, addAiMessage, setTyping }}
    >
      {children}
    </ConversationContext.Provider>
  );
}

export function useConversation() {
  const ctx = useContext(ConversationContext);
  if (!ctx)
    throw new Error(
      "useConversation must be used within <ConversationProvider>"
    );
  return ctx;
}
