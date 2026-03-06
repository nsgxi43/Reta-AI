import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
from faster_whisper import WhisperModel
from rapidfuzz import process, fuzz
import pyttsx3
import queue
import time

from services.rag_service import RAGService
from vectorstore.search import VectorSearch

# -----------------------------
# CONFIG
# -----------------------------
SAMPLE_RATE = 16000
SILENCE_THRESHOLD = 500
SILENCE_DURATION = 1.2
CHUNK_SIZE = 1024

print("🚀 Loading Whisper...")
whisper_model = WhisperModel("base", compute_type="int8")
print("✅ Whisper loaded")

print("🧠 Loading RAG...")
rag = RAGService()
print("✅ RAG loaded")

print("🔊 Initializing TTS...")
engine = pyttsx3.init()
engine.setProperty('rate', 170)
print("✅ TTS ready\n")

# -----------------------------
# BRAND LIST
# -----------------------------
searcher = VectorSearch()
all_products = searcher.get_all_products()
ALL_BRANDS = list(set(p["brand"] for p in all_products))


# -----------------------------
# RECORD UNTIL SILENCE
# -----------------------------
def record_until_silence(filename="input.wav"):
    print("\n🎤 Speak now...")

    q = queue.Queue()
    recording = []
    silence_counter = 0
    silence_limit = int(SILENCE_DURATION * SAMPLE_RATE / CHUNK_SIZE)

    def callback(indata, frames, time, status):
        q.put(indata.copy())

    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype='int16',
        blocksize=CHUNK_SIZE,
        callback=callback
    ):
        while True:
            data = q.get()
            volume = np.abs(data).mean()
            recording.append(data)

            if volume < SILENCE_THRESHOLD:
                silence_counter += 1
            else:
                silence_counter = 0

            if silence_counter > silence_limit:
                break

    audio = np.concatenate(recording, axis=0)
    wav.write(filename, SAMPLE_RATE, audio)
    print("✅ Recording stopped")


# -----------------------------
# TRANSCRIBE
# -----------------------------
def transcribe_audio(filename="input.wav"):
    segments, _ = whisper_model.transcribe(
        filename,
        language="en",
        beam_size=5
    )

    text = ""
    for segment in segments:
        text += segment.text

    return text.strip()


# -----------------------------
# BRAND NORMALIZATION
# -----------------------------
from rapidfuzz import process, fuzz

MIN_BRAND_LENGTH = 4
BRAND_THRESHOLD = 80

def correct_brands(text):
    words = text.split()
    corrected_words = []

    for word in words:
        best_match = None
        best_score = 0

        for brand in ALL_BRANDS:
            if len(brand) < MIN_BRAND_LENGTH:
                continue  # ignore short brands like "Rin"

            score = fuzz.ratio(word.lower(), brand.lower())

            if score > best_score:
                best_score = score
                best_match = brand

        if best_score >= BRAND_THRESHOLD:
            print(f"🔧 Brand corrected: {word} → {best_match}")
            corrected_words.append(best_match)
        else:
            corrected_words.append(word)

    return " ".join(corrected_words)




# -----------------------------
# SPEAK
# -----------------------------
def speak(text):
    print("\n🤖 Assistant:", text)
    engine.say(text)
    engine.runAndWait()


# -----------------------------
# MAIN LOOP
# -----------------------------
def main():
    print("🎙 Voice Retail Assistant Ready (Say 'exit' to stop)\n")

    while True:
        
        record_until_silence()

        raw_text = transcribe_audio()
        print("\n📝 Raw:", raw_text)

        if not raw_text:
            continue

        if raw_text.lower() in ["exit", "quit", "stop"]:
            speak("Goodbye! Have a great day.")
            break

        corrected_query = correct_brands(raw_text)
        print("🛍 Corrected:", corrected_query)

        # Query RAG
        result = rag.query(corrected_query)

        response = result.get("response", "Sorry, I couldn't find anything.")

        # Speak response
        speak(response)


if __name__ == "__main__":
    main()
