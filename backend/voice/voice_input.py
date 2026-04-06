import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
from faster_whisper import WhisperModel
from rapidfuzz import fuzz, process
import queue

# Import RAG to fetch product vocabulary
from services.rag_service import RAGService
from vectorstore.search import VectorSearch

SAMPLE_RATE = 16000
SILENCE_THRESHOLD = 400
SILENCE_DURATION = 1.2
CHUNK_SIZE = 1024

# Load Whisper model
print("🚀 Loading Whisper model...")
model = WhisperModel("base", compute_type="int8")
print("✅ Whisper loaded\n")

# Load product vocabulary for fuzzy brand/product matching
print("📦 Loading product vocabulary...")
searcher = VectorSearch()
all_products = searcher.get_all_products()

KNOWN_BRANDS = sorted(list(set(
    p.get("brand", "").lower().strip()
    for p in all_products
    if p.get("brand")
)))

KNOWN_PRODUCT_NAMES = sorted(list(set(
    p.get("product_name", "").lower().strip()
    for p in all_products
    if p.get("product_name")
)))

VOCABULARY = KNOWN_BRANDS + KNOWN_PRODUCT_NAMES
print(f"✅ Loaded {len(KNOWN_BRANDS)} brands, {len(KNOWN_PRODUCT_NAMES)} products\n")


def record_until_silence(filename="input.wav"):
    """Record audio until silence is detected."""
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


def transcribe_audio(filename="input.wav"):
    """Transcribe audio using Whisper."""
    segments, _ = model.transcribe(
        filename,
        language="en",
        beam_size=5
    )

    text = " ".join([segment.text for segment in segments])
    return text.strip()


def correct_brands_and_products(text):
    """
    Aggressive fuzzy correction for brands and product names.
    Uses RapidFuzz with lower threshold to catch mishearings.
    """
    words = text.lower().split()
    corrected_words = []

    for word in words:
        if len(word) < 2:
            corrected_words.append(word)
            continue
        
        # Use lower cutoff (60) to catch mishearings like "shambu"→"shampoo"
        match, score, _ = process.extractOne(
            word,
            VOCABULARY,
            scorer=fuzz.ratio,
            score_cutoff=60
        )

        # Aggressive correction: prefer match over original word
        if match and score >= 60:
            corrected_words.append(match)
        else:
            corrected_words.append(word)

    return " ".join(corrected_words)


# Main execution
if __name__ == "__main__":
    record_until_silence()

    raw_text = transcribe_audio()
    print("📝 Raw Transcription:", raw_text)

    corrected_text = correct_brands_and_products(raw_text)
    print("🛍  Corrected Query:", corrected_text)
