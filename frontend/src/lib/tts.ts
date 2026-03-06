/**
 * Shared TTS (Text-to-Speech) utility for the entire app.
 *
 * Handles:
 *  - Async voice loading (Chrome loads voices lazily)
 *  - Chrome 15-second pause bug (keep-alive via resume())
 *  - Proper cancel-before-speak sequencing
 */

let keepAliveTimer: ReturnType<typeof setInterval> | null = null;

/* ── Load voices (resolves immediately on Safari, waits on Chrome) ── */
function loadVoices(): Promise<SpeechSynthesisVoice[]> {
  return new Promise((resolve) => {
    if (typeof window === "undefined" || !window.speechSynthesis) {
      resolve([]);
      return;
    }
    const synth = window.speechSynthesis;
    const voices = synth.getVoices();
    if (voices.length > 0) {
      resolve(voices);
      return;
    }
    // Chrome fires this event once voices are ready
    const onReady = () => {
      synth.removeEventListener("voiceschanged", onReady);
      resolve(synth.getVoices());
    };
    synth.addEventListener("voiceschanged", onReady);
    // Safety fallback — speak with default voice after 1.5s
    setTimeout(() => {
      synth.removeEventListener("voiceschanged", onReady);
      resolve(synth.getVoices());
    }, 1500);
  });
}

/* ── Pick a nice voice ─────────────────────────────────────────── */
function pickVoice(voices: SpeechSynthesisVoice[]) {
  return (
    voices.find((v) => v.name.includes("Samantha")) ||
    voices.find((v) => v.name.includes("Google") && v.lang.startsWith("en")) ||
    voices.find((v) => v.name.includes("Female") && v.lang.startsWith("en")) ||
    voices.find((v) => v.lang.startsWith("en")) ||
    null
  );
}

/* ── Chrome bug: synth pauses after ~15s. Keep it alive. ───────── */
function ensureKeepAlive() {
  if (keepAliveTimer) return;
  keepAliveTimer = setInterval(() => {
    const synth = window.speechSynthesis;
    if (synth?.speaking && !synth.paused) {
      synth.pause();
      synth.resume();
    }
  }, 5000);
}

/* ── Clean text for speech ─────────────────────────────────────── */
function cleanForSpeech(text: string): string {
  return text
    .replace(/[#*_`>|]/g, "")
    .replace(/\n{2,}/g, ". ")
    .replace(/\n/g, " ")
    .replace(/\s{2,}/g, " ")
    .trim();
}

/* ══════════════════════════════════════════════════════════════════
   PUBLIC: speak(text, onEnd?)
   ══════════════════════════════════════════════════════════════════ */
export async function speak(
  text: string,
  onEnd?: () => void
): Promise<SpeechSynthesisUtterance | null> {
  if (typeof window === "undefined" || !window.speechSynthesis) {
    onEnd?.();
    return null;
  }

  const synth = window.speechSynthesis;
  const clean = cleanForSpeech(text);
  if (!clean) {
    onEnd?.();
    return null;
  }

  const voices = await loadVoices();

  // Cancel any ongoing speech
  synth.cancel();

  const utterance = new SpeechSynthesisUtterance(clean);
  utterance.rate = 1.0;
  utterance.pitch = 1.0;
  utterance.volume = 1.0;

  const voice = pickVoice(voices);
  if (voice) utterance.voice = voice;

  utterance.onend = () => onEnd?.();
  utterance.onerror = (e) => {
    const err = (e as any).error;
    if (err !== "interrupted" && err !== "canceled") {
      console.warn("TTS error:", err);
    }
    onEnd?.();
  };

  // Speak after a micro-task so cancel() fully settles
  await new Promise((r) => setTimeout(r, 60));
  synth.speak(utterance);
  ensureKeepAlive();

  return utterance;
}

/* ══════════════════════════════════════════════════════════════════
   PUBLIC: stopSpeaking()
   ══════════════════════════════════════════════════════════════════ */
export function stopSpeaking() {
  if (typeof window !== "undefined" && window.speechSynthesis) {
    window.speechSynthesis.cancel();
  }
}

/* ══════════════════════════════════════════════════════════════════
   PUBLIC: isSpeaking()
   ══════════════════════════════════════════════════════════════════ */
export function isSpeaking(): boolean {
  return (
    typeof window !== "undefined" &&
    !!window.speechSynthesis &&
    window.speechSynthesis.speaking
  );
}
