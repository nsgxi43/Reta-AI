"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { User as UserType } from "@/types";
import { motion, AnimatePresence } from "framer-motion";
import {
  User,
  Ghost,
  Mic,
  MessageSquare,
  ArrowRight,
  ArrowLeft,
  Phone,
  LogIn,
} from "lucide-react";
import { speak, stopSpeaking } from "@/lib/tts";

interface LoginProps {
  onLogin: (user: UserType, mode: "text" | "voice") => void;
}

type Step =
  | "landing"
  | "phone_input"
  | "name_input"
  | "guest_welcome"
  | "mode_selection";

/* ══════════════════════════════════════════════════════════════════
   Main LoginScreen
   ══════════════════════════════════════════════════════════════════ */
export function LoginScreen({ onLogin }: LoginProps) {
  const [step, setStep] = useState<Step>("landing");
  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");
  const [isGuest, setIsGuest] = useState(false);

  /* ── Guest flow ──────────────────────────────────────────────── */
  const handleGuestLogin = () => {
    setIsGuest(true);
    setName("Guest");
    setPhone("");
    setStep("guest_welcome");
    // Speak immediately from click handler (user gesture context)
    speak(
      "Welcome Guest! How may I assist you today? You can log in with your personal details for a personalized experience, or continue as a guest."
    );
  };

  /* ── Name login flow ─────────────────────────────────────────── */
  const handleNameLogin = () => {
    setIsGuest(false);
    setPhone("");
    setName("");
    setStep("phone_input");
  };

  const handlePhoneSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (phone.trim().length >= 10) {
      setStep("name_input");
    }
  };

  const handleNameSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (name.trim()) {
      setStep("mode_selection");
      // Speak immediately from click handler (user gesture context)
      speak(
        `Welcome ${name.trim()}! How may I assist you today? Click on voice to talk to me through voice, or click on text to chat with me. I am here to help you find the perfect product!`
      );
    }
  };

  /* ── Final mode pick ─────────────────────────────────────────── */
  const handleModeSelection = (mode: "voice" | "text") => {
    stopSpeaking();
    setTimeout(() => {
      onLogin({ name: name || "Guest", phone }, mode);
    }, 400);
  };

  /* ── Guest welcome → login redirect ─────────────────────────── */
  const handleGuestToLogin = () => {
    stopSpeaking();
    setIsGuest(false);
    setName("");
    setPhone("");
    setStep("phone_input");
  };

  const handleGuestContinue = () => {
    setStep("mode_selection");
    // Speak mode selection prompt from click handler
    speak(
      "Welcome Guest! How may I assist you today? Click on voice to talk to me through voice, or click on text to chat with me. I am here to help you find the perfect product!"
    );
  };

  const variants = {
    enter: { opacity: 0, y: 20, scale: 0.95 },
    center: { opacity: 1, y: 0, scale: 1 },
    exit: { opacity: 0, y: -20, scale: 0.95 },
  };

  return (
    <div className="flex-1 flex flex-col items-center justify-center p-6 bg-transparent text-white relative overflow-hidden">
      <div className="w-full max-w-md z-10">
        <AnimatePresence mode="wait">
          {/* ─────────────── LANDING ─────────────── */}
          {step === "landing" && (
            <motion.div
              key="landing"
              variants={variants}
              initial="enter"
              animate="center"
              exit="exit"
              transition={{ duration: 0.4, ease: "easeOut" }}
              className="space-y-12 text-center"
            >
              <motion.div
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.2 }}
                className="flex items-center justify-center p-8"
              >
                <div className="text-center space-y-2">
                  <h1 className="text-6xl md:text-7xl font-bold tracking-tight bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent drop-shadow-sm px-4">
                    RetAIl
                  </h1>
                  <p className="text-xl md:text-2xl text-white font-light tracking-wide opacity-90">
                    Made shopping easy
                  </p>
                </div>
              </motion.div>

              <div className="flex flex-col gap-4 w-full max-w-xs mx-auto">
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.96 }}
                  onClick={handleGuestLogin}
                  className="group relative p-6 rounded-3xl bg-zinc-900/50 border border-zinc-800 hover:bg-zinc-800/50 hover:border-zinc-700 transition-all duration-300 flex items-center gap-6 overflow-hidden"
                >
                  <div className="absolute inset-0 bg-blue-500/10 opacity-0 group-active:opacity-100 transition-opacity duration-300 rounded-3xl" />
                  <div className="absolute inset-0 bg-gradient-to-r from-blue-500/10 to-transparent opacity-0 group-hover:opacity-100 rounded-3xl transition-opacity" />
                  <div className="p-3 rounded-full bg-blue-500/20 text-blue-400">
                    <Ghost className="w-6 h-6" />
                  </div>
                  <span className="text-xl font-medium text-zinc-100">
                    Guest Login
                  </span>
                </motion.button>

                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.96 }}
                  onClick={handleNameLogin}
                  className="group relative p-6 rounded-3xl bg-zinc-900/50 border border-zinc-800 hover:bg-zinc-800/50 hover:border-zinc-700 transition-all duration-300 flex items-center gap-6 overflow-hidden"
                >
                  <div className="absolute inset-0 bg-purple-500/10 opacity-0 group-active:opacity-100 transition-opacity duration-300 rounded-3xl" />
                  <div className="absolute inset-0 bg-gradient-to-r from-purple-500/10 to-transparent opacity-0 group-hover:opacity-100 rounded-3xl transition-opacity" />
                  <div className="p-3 rounded-full bg-purple-500/20 text-purple-400">
                    <User className="w-6 h-6" />
                  </div>
                  <span className="text-xl font-medium text-zinc-100">
                    Login by Name
                  </span>
                </motion.button>
              </div>
            </motion.div>
          )}

          {/* ─────────────── PHONE INPUT ─────────────── */}
          {step === "phone_input" && (
            <motion.div
              key="phone_input"
              variants={variants}
              initial="enter"
              animate="center"
              exit="exit"
              transition={{ duration: 0.4 }}
              className="space-y-8"
            >
              <div className="text-center space-y-2">
                <div className="flex justify-center mb-4">
                  <div className="p-4 rounded-full bg-blue-500/20">
                    <Phone className="w-8 h-8 text-blue-400" />
                  </div>
                </div>
                <h2 className="text-3xl font-bold text-white">
                  Your phone number?
                </h2>
                <p className="text-zinc-400">
                  So we can personalise your experience.
                </p>
              </div>

              <form
                onSubmit={handlePhoneSubmit}
                className="space-y-6 flex flex-col items-center"
              >
                <div className="relative w-full max-w-sm">
                  <input
                    autoFocus
                    type="tel"
                    inputMode="numeric"
                    value={phone}
                    onChange={(e) =>
                      setPhone(e.target.value.replace(/[^0-9]/g, ""))
                    }
                    maxLength={10}
                    placeholder="Enter 10-digit number"
                    className="w-full text-center text-2xl font-medium tracking-[0.25em] bg-transparent border-b-2 border-zinc-700 focus:border-blue-400 pb-3 text-white placeholder-zinc-600 outline-none transition-colors"
                    autoComplete="tel"
                  />
                  <p className="text-xs text-zinc-500 text-center mt-2">
                    {phone.length}/10
                  </p>
                </div>

                <button
                  type="submit"
                  disabled={phone.length < 10}
                  className="rounded-full w-14 h-14 bg-white text-black flex items-center justify-center hover:scale-110 active:scale-95 disabled:opacity-50 disabled:hover:scale-100 transition-all duration-300 shadow-lg shadow-white/10"
                >
                  <ArrowRight className="w-6 h-6" />
                </button>
              </form>

              <button
                onClick={() => setStep("landing")}
                className="w-full text-center text-sm text-zinc-500 hover:text-white transition-colors flex items-center justify-center gap-1"
              >
                <ArrowLeft className="w-3 h-3" /> Back
              </button>
            </motion.div>
          )}

          {/* ─────────────── NAME INPUT ─────────────── */}
          {step === "name_input" && (
            <motion.div
              key="name_input"
              variants={variants}
              initial="enter"
              animate="center"
              exit="exit"
              transition={{ duration: 0.4 }}
              className="space-y-8"
            >
              <div className="text-center space-y-2">
                <h2 className="text-3xl font-bold text-white">
                  What&apos;s your name?
                </h2>
                <p className="text-zinc-400">
                  I&apos;d love to know who I&apos;m helping today.
                </p>
              </div>

              <form
                onSubmit={handleNameSubmit}
                className="space-y-6 flex flex-col items-center"
              >
                <div className="relative w-full max-w-sm h-16 flex items-center justify-center">
                  <input
                    autoFocus
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    className="absolute inset-0 w-full h-full opacity-0 z-10 cursor-text text-center caret-transparent"
                    autoComplete="off"
                  />
                  <div className="flex items-center justify-center gap-[1px] text-3xl font-medium border-b-2 border-zinc-700 w-full pb-2 transition-colors duration-300">
                    <AnimatePresence mode="popLayout">
                      {name.split("").map((char, index) => (
                        <motion.span
                          key={`${index}-${char}`}
                          initial={{
                            opacity: 0,
                            y: 10,
                            textShadow:
                              "0 0 10px #fff, 0 0 20px #fff, 0 0 30px #00ffff",
                          }}
                          animate={{
                            opacity: 1,
                            y: 0,
                            textShadow: "0 0 0px transparent",
                          }}
                          exit={{ opacity: 0, scale: 0.5 }}
                          transition={{ duration: 0.2 }}
                          className="inline-block text-white"
                        >
                          {char === " " ? "\u00A0" : char}
                        </motion.span>
                      ))}
                    </AnimatePresence>
                    <motion.div
                      animate={{ opacity: [0, 1, 0] }}
                      transition={{ duration: 0.8, repeat: Infinity }}
                      className="w-0.5 h-8 bg-blue-400 ml-1"
                    />
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={!name.trim()}
                  className="rounded-full w-14 h-14 bg-white text-black flex items-center justify-center hover:scale-110 active:scale-95 disabled:opacity-50 disabled:hover:scale-100 transition-all duration-300 shadow-lg shadow-white/10 relative z-20"
                >
                  <ArrowRight className="w-6 h-6" />
                </button>
              </form>

              <button
                onClick={() => setStep("phone_input")}
                className="w-full text-center text-sm text-zinc-500 hover:text-white transition-colors flex items-center justify-center gap-1"
              >
                <ArrowLeft className="w-3 h-3" /> Back
              </button>
            </motion.div>
          )}

          {/* ─────────────── GUEST WELCOME ─────────────── */}
          {step === "guest_welcome" && (
            <GuestWelcome
              variants={variants}
              onLoginHere={handleGuestToLogin}
              onContinueGuest={handleGuestContinue}
            />
          )}

          {/* ─────────────── MODE SELECTION (logged-in user) ─────────────── */}
          {step === "mode_selection" && (
            <ModeSelection
              variants={variants}
              name={name}
              isGuest={isGuest}
              onSelectMode={handleModeSelection}
            />
          )}
        </AnimatePresence>
      </div>

      {/* Footer */}
      <div className="absolute bottom-6 text-center w-full z-10">
        <p className="text-xs text-zinc-600">
          Powered by Reta AI • Shopping Assistant
        </p>
      </div>
    </div>
  );
}

/* ══════════════════════════════════════════════════════════════════
   GUEST WELCOME — AI speaks greeting, offers login or continue
   ══════════════════════════════════════════════════════════════════ */
function GuestWelcome({
  variants,
  onLoginHere,
  onContinueGuest,
}: {
  variants: any;
  onLoginHere: () => void;
  onContinueGuest: () => void;
}) {
  // Speech is triggered from the parent click handler (user gesture)
  // so it works reliably across all browsers.

  return (
    <motion.div
      key="guest_welcome"
      variants={variants}
      initial="enter"
      animate="center"
      exit="exit"
      transition={{ duration: 0.4 }}
      className="space-y-10 text-center"
    >
      <TypewriterHeader name="Guest" isGuest />

      <motion.p
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1.8 }}
        className="text-lg text-zinc-400 max-w-xs mx-auto leading-relaxed"
      >
        How may I assist you today?
      </motion.p>

      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 2.4 }}
        className="flex flex-col gap-4 w-full max-w-xs mx-auto"
      >
        {/* Login here */}
        <button
          onClick={onLoginHere}
          className="group relative p-5 rounded-3xl bg-zinc-900/50 border border-zinc-800 hover:bg-zinc-800/50 hover:border-zinc-700 transition-all duration-300 flex items-center gap-5 overflow-hidden"
        >
          <div className="absolute inset-0 bg-purple-500/10 opacity-0 group-hover:opacity-100 rounded-3xl transition-opacity" />
          <div className="p-3 rounded-full bg-purple-500/20 text-purple-400">
            <LogIn className="w-5 h-5" />
          </div>
          <div className="text-left">
            <span className="text-base font-medium text-zinc-100 block">
              Login here
            </span>
            <span className="text-xs text-zinc-500">
              Get a personalised experience
            </span>
          </div>
        </button>

        {/* Continue as guest */}
        <button
          onClick={onContinueGuest}
          className="group relative p-5 rounded-3xl bg-zinc-900/50 border border-zinc-800 hover:bg-zinc-800/50 hover:border-zinc-700 transition-all duration-300 flex items-center gap-5 overflow-hidden"
        >
          <div className="absolute inset-0 bg-blue-500/10 opacity-0 group-hover:opacity-100 rounded-3xl transition-opacity" />
          <div className="p-3 rounded-full bg-blue-500/20 text-blue-400">
            <Ghost className="w-5 h-5" />
          </div>
          <div className="text-left">
            <span className="text-base font-medium text-zinc-100 block">
              Continue as Guest
            </span>
            <span className="text-xs text-zinc-500">Skip for now</span>
          </div>
        </button>
      </motion.div>
    </motion.div>
  );
}

/* ══════════════════════════════════════════════════════════════════
   MODE SELECTION — AI speaks guidance, show voice / text buttons
   ══════════════════════════════════════════════════════════════════ */
function ModeSelection({
  variants,
  name,
  isGuest,
  onSelectMode,
}: {
  variants: any;
  name: string;
  isGuest: boolean;
  onSelectMode: (mode: "voice" | "text") => void;
}) {
  const displayName = isGuest ? "Guest" : name;
  // Speech is triggered from the parent click handler (user gesture)

  return (
    <motion.div
      key="mode_selection"
      variants={variants}
      initial="enter"
      animate="center"
      exit="exit"
      transition={{ duration: 0.4 }}
      className="space-y-10 text-center"
    >
      <div className="space-y-4">
        <TypewriterHeader name={displayName} isGuest={isGuest} />
        <motion.h3
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.8 }}
          className="text-xl text-zinc-400 max-w-sm mx-auto leading-relaxed"
        >
          How may I assist you today?
        </motion.h3>
      </div>

      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 2.4 }}
        className="grid grid-cols-1 sm:grid-cols-2 gap-4"
      >
        <button
          onClick={() => onSelectMode("voice")}
          className="group flex flex-col items-center justify-center p-8 rounded-3xl bg-zinc-900/50 border border-zinc-800 hover:bg-zinc-800 hover:border-zinc-600 transition-all duration-300 aspect-square sm:aspect-auto sm:h-48"
        >
          <div className="w-16 h-16 rounded-full bg-indigo-500/20 text-indigo-400 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
            <Mic className="w-8 h-8" />
          </div>
          <span className="text-lg font-medium text-white">Voice</span>
          <span className="text-sm text-zinc-500 mt-1">Talk to me</span>
        </button>

        <button
          onClick={() => onSelectMode("text")}
          className="group flex flex-col items-center justify-center p-8 rounded-3xl bg-zinc-900/50 border border-zinc-800 hover:bg-zinc-800 hover:border-zinc-600 transition-all duration-300 aspect-square sm:aspect-auto sm:h-48"
        >
          <div className="w-16 h-16 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
            <MessageSquare className="w-8 h-8" />
          </div>
          <span className="text-lg font-medium text-white">Text</span>
          <span className="text-sm text-zinc-500 mt-1">Chat with me</span>
        </button>
      </motion.div>
    </motion.div>
  );
}

/* ══════════════════════════════════════════════════════════════════
   Typewriter Header
   ══════════════════════════════════════════════════════════════════ */
function TypewriterHeader({
  name,
  isGuest,
}: {
  name: string;
  isGuest: boolean;
}) {
  const text = `Hi ${isGuest ? "Guest" : name}, I am RetAIl`;
  const [displayedText, setDisplayedText] = useState("");
  const [showCursor, setShowCursor] = useState(true);

  useEffect(() => {
    let i = 0;
    setDisplayedText("");
    setShowCursor(true);
    const timer = setInterval(() => {
      if (i <= text.length) {
        setDisplayedText(text.substring(0, i));
        i++;
      } else {
        clearInterval(timer);
        setShowCursor(false);
      }
    }, 80);
    return () => clearInterval(timer);
  }, [text]);

  return (
    <div className="h-20 flex items-center justify-center">
      <h2 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent text-center inline-block">
        {displayedText || "\u00A0"}
        <AnimatePresence>
          {showCursor && (
            <motion.span
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="bg-purple-400 inline-block w-1 h-8 md:h-10 ml-1 align-middle"
            />
          )}
        </AnimatePresence>
      </h2>
    </div>
  );
}
