import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
from faster_whisper import WhisperModel
from rapidfuzz import fuzz, process
import queue

# Import your RAG to fetch brands dynamically
from services.rag_service import RAGService

SAMPLE_RATE = 16000
SILENCE_THRESHOLD = 400
SILENCE_DURATION = 1.2
CHUNK_SIZE = 1024

# -----------------------------
# Load Whisper (fast + accurate)
# -----------------------------
print("Loading Whisper model...")
model = WhisperModel("base", compute_type="int8")
print("Model loaded.\n")

# -----------------------------
# Load Known Brands Dynamically
# -----------------------------
rag = RAGService()
all_products = rag.searcher.get_all_products()

KNOWN_BRANDS = list(set(
    p["brand"].lower()
    for p in all_products
))

# -----------------------------
# Record Until Silence
# -----------------------------
def record_until_silence(filename="input.wav"):
    print("🎤 Speak now... (auto stop on silence)")

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
    print("✅ Recording stopped\n")

# -----------------------------
# Transcription
# -----------------------------
def transcribe_audio(filename="input.wav"):
    segments, _ = model.transcribe(
        filename,
        language="en",
        beam_size=5
    )

    text = " ".join([segment.text for segment in segments])
    return text.strip()

# -----------------------------
# Smart Brand Correction
# -----------------------------
def correct_brands(text):
    words = text.lower().split()
    corrected_words = []

    for word in words:
        match, score, _ = process.extractOne(
            word,
            KNOWN_BRANDS,
            scorer=fuzz.ratio
        )

        # If similarity high enough, replace
        if score > 75:
            corrected_words.append(match)
        else:
            corrected_words.append(word)

    return " ".join(corrected_words)

# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":

    record_until_silence()

    raw_text = transcribe_audio()
    print("📝 Raw Transcription:", raw_text)

    corrected_text = correct_brands(raw_text)
    print("🛍 Corrected Query:", corrected_text)
