"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Keyboard, Mic, MicOff, X } from "lucide-react";
import { User } from "@/types";
import { useConversation } from "@/lib/conversation";
import { speak as ttsSpeak, stopSpeaking, isSpeaking } from "@/lib/tts";

/* ── Types ─────────────────────────────────────────────────────── */
type VoiceState = "idle" | "listening" | "processing" | "speaking";
type RatingPhase = "none" | "asking" | "listening" | "invalid" | "done";

interface VoiceInterfaceProps {
  user: User;
  onSwitchToText: () => void;
  onLogout: () => void;
}

/* ── Conclusive detection ──────────────────────────────────────── */
const CONCLUSIVE = [
  "thank you", "thanks", "that's all", "thats all", "bye",
  "goodbye", "good bye", "no more", "i'm done", "im done",
  "that will be all", "nothing else", "okay thanks", "ok thanks",
  "okay thank you", "ok thank you",
];
function isConclusive(t: string) {
  const lower = t.toLowerCase().trim();
  return CONCLUSIVE.some((p) => lower.includes(p));
}

/* ── Browser Speech Recognition ────────────────────────────────── */
const SpeechRecognition =
  typeof window !== "undefined"
    ? (window as any).SpeechRecognition ||
      (window as any).webkitSpeechRecognition
    : null;

/* ── Component ─────────────────────────────────────────────────── */
export function VoiceInterface({
  user,
  onSwitchToText,
  onLogout,
}: VoiceInterfaceProps) {
  const { sendMessage } = useConversation();

  const [voiceState, setVoiceState] = useState<VoiceState>("idle");
  const [transcript, setTranscript] = useState("");
  const [aiText, setAiText] = useState("");
  const [isMuted, setIsMuted] = useState(false);

  /* ── Rating state ── */
  const [ratingPhase, setRatingPhase] = useState<RatingPhase>("none");
  const [hasRated, setHasRated] = useState(false);
  const ratingPhaseRef = useRef<RatingPhase>("none");

  const recognitionRef = useRef<any>(null);
  const synthRef = useRef<SpeechSynthesisUtterance | null>(null);
  const silenceTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const lastFinalRef = useRef("");

  // Keep rating phase ref in sync
  useEffect(() => {
    ratingPhaseRef.current = ratingPhase;
  }, [ratingPhase]);

  /* ── Clean up on unmount ─────────────────────────────────────── */
  useEffect(() => {
    return () => {
      recognitionRef.current?.stop();
      stopSpeaking();
      if (silenceTimerRef.current) clearTimeout(silenceTimerRef.current);
    };
  }, []);

  /* ── Speak utility (uses shared tts module) ──────────────────── */
  const speak = useCallback(
    async (text: string, onDone?: () => void) => {
      setVoiceState("speaking");
      const utterance = await ttsSpeak(text, () => {
        setVoiceState("idle");
        synthRef.current = null;
        onDone?.();
      });
      synthRef.current = utterance;
    },
    []
  );

  /* ── Start listening ─────────────────────────────────────────── */
  const startListening = useCallback(() => {
    if (!SpeechRecognition || isMuted) return;
    // Only cancel speech if something is actively speaking
    if (isSpeaking()) stopSpeaking();

    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = "en-US";

    recognition.onstart = () => {
      setVoiceState("listening");
      setTranscript("");
      setAiText("");
      lastFinalRef.current = "";
    };

    recognition.onresult = (event: any) => {
      let finalText = "";
      let interimText = "";
      for (let i = 0; i < event.results.length; i++) {
        if (event.results[i].isFinal) {
          finalText += event.results[i][0].transcript;
        } else {
          interimText += event.results[i][0].transcript;
        }
      }
      const display = (finalText + " " + interimText).trim();
      setTranscript(display || "Listening...");
      lastFinalRef.current = finalText;

      if (silenceTimerRef.current) clearTimeout(silenceTimerRef.current);

      if (finalText.trim()) {
        silenceTimerRef.current = setTimeout(() => {
          recognition.stop();

          // If we're in rating phase, handle rating
          if (
            ratingPhaseRef.current === "listening" ||
            ratingPhaseRef.current === "invalid"
          ) {
            handleRatingResponse(finalText.trim());
          } else {
            handleQuery(finalText.trim());
          }
        }, 1800);
      }
    };

    recognition.onerror = (event: any) => {
      if (event.error === "no-speech" || event.error === "aborted") return;
      console.error("Speech error:", event.error);
      if (event.error === "not-allowed") {
        setTranscript("Microphone access denied.");
        setVoiceState("idle");
      }
    };

    recognition.onend = () => {};
    recognitionRef.current = recognition;

    try {
      recognition.start();
    } catch {
      /* already started */
    }
  }, [isMuted]);

  /* ── Ask for rating via voice ────────────────────────────────── */
  const askForRating = useCallback(() => {
    const askText =
      "Thank you! Before you go, could you please rate your experience from 1 to 5? 1 being the lowest and 5 being the highest.";
    setAiText(askText);
    setRatingPhase("listening");
    speak(askText, () => {
      // Start listening for the rating number
      setTimeout(() => startListening(), 400);
    });
  }, [speak, startListening]);

  /* ── Handle normal query → backend → TTS ─────────────────────── */
  const handleQuery = useCallback(
    async (text: string) => {
      setVoiceState("processing");
      setTranscript(text);

      // If conclusive and not yet rated, skip LLM and go straight to rating
      if (!hasRated && isConclusive(text)) {
        setRatingPhase("asking");
        askForRating();
        return;
      }

      const response = await sendMessage(text, user.name);
      setAiText(response);

      speak(response, () => {
        if (!isMuted) setTimeout(() => startListening(), 400);
      });
    },
    [sendMessage, user.name, hasRated, speak, isMuted, startListening, askForRating]
  );

  /* ── Handle voice rating response ────────────────────────────── */
  const handleRatingResponse = useCallback(
    (text: string) => {
      // Extract a number 1-5 from the response
      const match = text.match(/\b([1-5])\b/);

      if (match) {
        const rating = parseInt(match[1], 10);
        console.log("Voice rating:", rating);
        setHasRated(true);
        setRatingPhase("done");
        const thankText = `Thank you for rating us ${rating} out of 5! We appreciate your feedback. Have a great day!`;
        setAiText(thankText);
        speak(thankText, () => {
          setRatingPhase("none");
        });
      } else {
        // Invalid — ask again
        setRatingPhase("invalid");
        const retryText =
          "I didn't catch a valid number. Please rate only between 1 to 5.";
        setAiText(retryText);
        speak(retryText, () => {
          setRatingPhase("listening");
          setTimeout(() => startListening(), 400);
        });
      }
    },
    [speak, startListening]
  );

  /* ── Mic toggle ──────────────────────────────────────────────── */
  const toggleMic = useCallback(() => {
    if (voiceState === "speaking") {
      stopSpeaking();
      setVoiceState("idle");
      return;
    }
    if (voiceState === "listening") {
      recognitionRef.current?.stop();
      if (silenceTimerRef.current) clearTimeout(silenceTimerRef.current);
      setVoiceState("idle");
    } else if (voiceState === "idle") {
      startListening();
    }
  }, [voiceState, startListening]);

  /* ── Mute toggle ─────────────────────────────────────────────── */
  const toggleMute = useCallback(() => {
    const newMuted = !isMuted;
    setIsMuted(newMuted);
    if (newMuted) {
      recognitionRef.current?.stop();
      stopSpeaking();
      if (silenceTimerRef.current) clearTimeout(silenceTimerRef.current);
      setVoiceState("idle");
    }
  }, [isMuted]);

  /* ── Auto-start on mount ─────────────────────────────────────── */
  useEffect(() => {
    const timer = setTimeout(() => {
      if (!isMuted) startListening();
    }, 600);
    return () => clearTimeout(timer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  /* ── Status label ────────────────────────────────────────────── */
  const statusLabel =
    ratingPhase === "listening" || ratingPhase === "invalid"
      ? "Waiting for your rating..."
      : voiceState === "listening"
      ? "Listening..."
      : voiceState === "processing"
      ? "Thinking..."
      : voiceState === "speaking"
      ? "Speaking..."
      : isMuted
      ? "Microphone muted"
      : "Tap the mic to speak";

  const displayText =
    voiceState === "speaking" || voiceState === "processing"
      ? aiText || transcript
      : transcript || "";

  /* ── Orb colours per state ── */
  const orbColors: Record<VoiceState, [string, string]> = {
    idle: ["rgba(63,63,70,0.4)", "rgba(39,39,42,0.4)"],
    listening: ["rgba(59,130,246,0.5)", "rgba(168,85,247,0.5)"],
    processing: ["rgba(234,179,8,0.5)", "rgba(168,85,247,0.5)"],
    speaking: ["rgba(16,185,129,0.5)", "rgba(59,130,246,0.5)"],
  };

  return (
    <div className="flex-1 flex flex-col h-full w-full bg-transparent relative overflow-hidden text-white select-none">
      {/* ── Top Bar ── */}
      <div className="flex items-center justify-between px-5 pt-5 pb-2 z-20">
        <button
          onClick={onLogout}
          className="p-3 rounded-full bg-zinc-900/60 border border-zinc-800 text-zinc-400 hover:text-white transition-colors active:scale-95"
        >
          <X className="w-5 h-5" />
        </button>

        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="px-4 py-1.5 rounded-full bg-zinc-900/60 border border-zinc-800"
        >
          <span className="text-xs font-medium text-zinc-300 flex items-center gap-2">
            <span
              className={`w-2 h-2 rounded-full ${
                voiceState === "listening"
                  ? "bg-blue-400 animate-pulse"
                  : voiceState === "speaking"
                  ? "bg-emerald-400 animate-pulse"
                  : voiceState === "processing"
                  ? "bg-yellow-400 animate-pulse"
                  : "bg-zinc-600"
              }`}
            />
            {statusLabel}
          </span>
        </motion.div>

        <button
          onClick={toggleMute}
          className={`p-3 rounded-full border transition-colors active:scale-95 ${
            isMuted
              ? "bg-red-950/40 border-red-900/50 text-red-300"
              : "bg-zinc-900/60 border-zinc-800 text-zinc-400 hover:text-white"
          }`}
        >
          {isMuted ? (
            <MicOff className="w-5 h-5" />
          ) : (
            <Mic className="w-5 h-5" />
          )}
        </button>
      </div>

      {/* ── Main Visual Area ── */}
      <div className="flex-1 flex flex-col items-center justify-center relative z-10 -mt-4">
        {/* Animated Orb */}
        <div className="relative w-72 h-72 flex items-center justify-center mb-12">
          <motion.div
            animate={{
              background: `radial-gradient(circle, ${orbColors[voiceState][0]}, transparent 70%)`,
            }}
            transition={{ duration: 0.8 }}
            className="absolute inset-[-40px] rounded-full blur-3xl"
          />
          <motion.div
            animate={{
              scale:
                voiceState === "listening"
                  ? [1, 1.12, 1]
                  : voiceState === "speaking"
                  ? [1, 1.08, 1]
                  : 1,
              opacity: voiceState === "idle" ? 0.2 : 0.5,
            }}
            transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
            className="absolute w-64 h-64 rounded-full border-2 border-white/10"
          />
          <motion.div
            animate={{
              rotate: [0, 360],
              scale:
                voiceState === "listening"
                  ? [1, 1.2, 1]
                  : voiceState === "speaking"
                  ? [1, 1.15, 1]
                  : [1, 1.02, 1],
            }}
            transition={{
              rotate: {
                duration: voiceState === "listening" ? 6 : 12,
                repeat: Infinity,
                ease: "linear",
              },
              scale: { duration: 2, repeat: Infinity, ease: "easeInOut" },
            }}
            className="absolute w-28 h-56 rounded-full mix-blend-screen blur-xl"
            style={{
              background: `linear-gradient(to bottom, ${orbColors[voiceState][0]}, ${orbColors[voiceState][1]})`,
              opacity: voiceState === "idle" ? 0.3 : 0.7,
            }}
          />
          <motion.div
            animate={{
              rotate: [0, -360],
              scale:
                voiceState === "listening"
                  ? [1, 1.25, 1]
                  : voiceState === "speaking"
                  ? [1, 1.1, 1]
                  : [1, 1.03, 1],
            }}
            transition={{
              rotate: {
                duration: voiceState === "listening" ? 8 : 16,
                repeat: Infinity,
                ease: "linear",
              },
              scale: { duration: 3, repeat: Infinity, ease: "easeInOut" },
            }}
            className="absolute w-28 h-56 rounded-full mix-blend-screen blur-xl"
            style={{
              background: `linear-gradient(to top, ${orbColors[voiceState][1]}, rgba(234,179,8,0.4))`,
              opacity: voiceState === "idle" ? 0.3 : 0.7,
            }}
          />
          <motion.div
            animate={{
              scale:
                voiceState === "listening"
                  ? [1, 1.8, 1]
                  : voiceState === "speaking"
                  ? [1, 1.4, 1]
                  : [1, 1.1, 1],
              opacity:
                voiceState === "idle"
                  ? 0.15
                  : voiceState === "processing"
                  ? 0.6
                  : 0.35,
            }}
            transition={{ duration: 1.5, repeat: Infinity }}
            className="absolute w-16 h-16 bg-white rounded-full blur-2xl"
          />
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 25, repeat: Infinity, ease: "linear" }}
            className="absolute w-60 h-60 border border-white/5 rounded-full"
          />
        </div>

        {/* ── Subtitle Area ── */}
        <div className="text-center space-y-3 max-w-sm px-6 min-h-[120px] flex flex-col justify-start">
          <AnimatePresence mode="wait">
            <motion.p
              key={displayText || statusLabel}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.25 }}
              className={`text-lg font-medium leading-relaxed ${
                voiceState === "speaking"
                  ? "bg-gradient-to-r from-emerald-200 via-blue-200 to-purple-200 bg-clip-text text-transparent"
                  : voiceState === "listening"
                  ? "bg-gradient-to-r from-blue-200 via-purple-200 to-pink-200 bg-clip-text text-transparent"
                  : voiceState === "processing"
                  ? "text-yellow-200/80"
                  : "text-zinc-500"
              }`}
            >
              {displayText || statusLabel}
            </motion.p>
          </AnimatePresence>

          {voiceState === "processing" && (
            <div className="flex justify-center gap-1.5">
              {[0, 1, 2].map((i) => (
                <motion.div
                  key={i}
                  animate={{ y: [0, -8, 0] }}
                  transition={{
                    duration: 0.6,
                    repeat: Infinity,
                    delay: i * 0.15,
                  }}
                  className="w-2 h-2 rounded-full bg-yellow-400/60"
                />
              ))}
            </div>
          )}
        </div>
      </div>

      {/* ── Bottom Controls ── */}
      <div className="px-8 pb-10 pt-4 flex items-center justify-between w-full max-w-sm mx-auto z-20">
        <button
          onClick={onSwitchToText}
          className="p-4 rounded-full bg-zinc-900/60 border border-zinc-800 text-white hover:bg-zinc-800 transition-all active:scale-95"
          title="Switch to Text"
        >
          <Keyboard className="w-6 h-6" />
        </button>

        <div className="relative">
          {voiceState === "listening" && (
            <motion.div
              animate={{ scale: [1, 1.4, 1], opacity: [0.4, 0, 0.4] }}
              transition={{ duration: 2, repeat: Infinity }}
              className="absolute inset-0 rounded-full bg-blue-500/30"
            />
          )}
          {voiceState === "speaking" && (
            <motion.div
              animate={{ scale: [1, 1.3, 1], opacity: [0.3, 0, 0.3] }}
              transition={{ duration: 1.5, repeat: Infinity }}
              className="absolute inset-0 rounded-full bg-emerald-500/30"
            />
          )}
          <button
            onClick={toggleMic}
            disabled={voiceState === "processing" || isMuted}
            className={`relative w-20 h-20 rounded-full flex items-center justify-center shadow-xl transition-all active:scale-95 disabled:opacity-50 ${
              voiceState === "listening"
                ? "bg-white text-black animate-glow"
                : voiceState === "speaking"
                ? "bg-emerald-500 text-white"
                : "bg-zinc-800 text-white border border-zinc-700 hover:bg-zinc-700"
            }`}
          >
            {voiceState === "listening" ? (
              <div className="flex gap-[3px] items-center justify-center h-8">
                {[0, 1, 2, 3, 4].map((i) => (
                  <motion.span
                    key={i}
                    animate={{ height: [10, 24 + i * 3, 10] }}
                    transition={{
                      duration: 0.7,
                      repeat: Infinity,
                      delay: i * 0.1,
                    }}
                    className="w-[3px] bg-black rounded-full"
                  />
                ))}
              </div>
            ) : voiceState === "speaking" ? (
              <div className="flex gap-[3px] items-center justify-center h-8">
                {[0, 1, 2, 3, 4].map((i) => (
                  <motion.span
                    key={i}
                    animate={{ height: [8, 18 + i * 2, 8] }}
                    transition={{
                      duration: 0.9,
                      repeat: Infinity,
                      delay: i * 0.12,
                    }}
                    className="w-[3px] bg-white rounded-full"
                  />
                ))}
              </div>
            ) : (
              <Mic className="w-8 h-8" />
            )}
          </button>
        </div>

        <button
          onClick={onLogout}
          className="p-4 rounded-full bg-red-950/30 border border-red-900/50 text-red-200 hover:bg-red-900/50 transition-all active:scale-95"
          title="End Session"
        >
          <X className="w-6 h-6" />
        </button>
      </div>
    </div>
  );
}
