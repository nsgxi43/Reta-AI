"use client";

import { useState } from "react";
import { User } from "@/types";
import { LoginScreen } from "@/components/LoginScreen";
import { ChatInterface } from "@/components/ChatInterface";
import { VoiceInterface } from "@/components/VoiceInterface";
import { ConversationProvider } from "@/lib/conversation";

export default function Home() {
  const [user, setUser] = useState<User | null>(null);
  const [mode, setMode] = useState<"text" | "voice">("text");

  const handleLogin = (u: User, selectedMode: "text" | "voice") => {
    setUser(u);
    setMode(selectedMode);
  };

  const handleLogout = () => {
    setUser(null);
    setMode("text");
  };

  return (
    <main className="flex-1 w-full h-full flex flex-col relative overflow-hidden bg-black text-foreground">
      {/* Ambient Background Effects */}
      <div className="absolute top-[-20%] left-[-10%] w-[500px] h-[500px] bg-purple-900/40 rounded-full blur-[120px] pointer-events-none z-0" />
      <div className="absolute bottom-[-20%] right-[-10%] w-[500px] h-[500px] bg-blue-900/40 rounded-full blur-[120px] pointer-events-none z-0" />

      <div className="relative z-10 w-full h-full flex flex-col">
        {!user ? (
          <LoginScreen onLogin={handleLogin} />
        ) : (
          <ConversationProvider>
            {mode === "voice" ? (
              <VoiceInterface
                user={user}
                onSwitchToText={() => setMode("text")}
                onLogout={handleLogout}
              />
            ) : (
              <ChatInterface
                user={user}
                onSwitchToVoice={() => setMode("voice")}
                onLogout={handleLogout}
              />
            )}
          </ConversationProvider>
        )}
      </div>
    </main>
  );
}
