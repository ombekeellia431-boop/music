import streamlit as st
import numpy as np
from scipy.io import wavfile
import moviepy.editor as mp # MoviePy is imported but not used for audio playback in this example
import io
import random

def generate_tone(frequency, duration, sample_rate=44100):
    """Generates a sine wave tone for a specific frequency."""
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    tone = np.sin(frequency * t * 2 * np.pi)
    # Apply a small fade out to avoid clicking sounds
    fade_out = np.linspace(1, 0, len(tone))
    return tone * fade_out

def create_ai_melody(tempo, bars, selected_scale, sample_rate=44100):
    """AI algorithm to generate a procedural melody using NumPy based on a selected scale."""
    # Define a broader set of notes including common accidentals for various scales
    all_notes = {
        "C4": 261.63, "C#4": 277.18, "D4": 293.66, "Eb4": 311.13, "E4": 329.63, "F4": 349.23,
        "F#4": 369.99, "G4": 392.00, "Ab4": 415.30, "A4": 440.00, "Bb4": 466.16, "B4": 493.88,
        "C5": 523.25
    }

    # Define notes for each scale based on C as the root note for simplicity
    if selected_scale == 'Major':
        scale_notes = [all_notes['C4'], all_notes['D4'], all_notes['E4'], all_notes['F4'], all_notes['G4'], all_notes['A4'], all_notes['B4']]
    elif selected_scale == 'Minor':
        scale_notes = [all_notes['C4'], all_notes['D4'], all_notes['Eb4'], all_notes['F4'], all_notes['G4'], all_notes['Ab4'], all_notes['Bb4']]
    elif selected_scale == 'Pentatonic Major':
        scale_notes = [all_notes['C4'], all_notes['D4'], all_notes['E4'], all_notes['G4'], all_notes['A4']]
    elif selected_scale == 'Pentatonic Minor':
        scale_notes = [all_notes['C4'], all_notes['Eb4'], all_notes['F4'], all_notes['G4'], all_notes['Bb4']]
    else:
        # Default to Major scale if something unexpected happens
        scale_notes = [all_notes['C4'], all_notes['D4'], all_notes['E4'], all_notes['F4'], all_notes['G4'], all_notes['A4'], all_notes['B4']]

    duration_per_note = 60 / tempo
    total_audio = np.array([], dtype=np.float32)

    for _ in range(bars * 4):
        freq = random.choice(scale_notes)
        tone = generate_tone(freq, duration_per_note, sample_rate)
        total_audio = np.concatenate((total_audio, tone))

    # Normalize audio to 16-bit PCM range
    total_audio = (total_audio * 32767).astype(np.int16)
    return total_audio

# Streamlit User Interface
st.set_page_config(page_title="AI Music Generator")
st.title("AI Procedural Music Composer")
st.write("This application uses mathematical algorithms to generate original music sequences.")

with st.sidebar:
    st.header("Settings")
    user_tempo = st.slider("Select Tempo (BPM)", 60, 180, 120)
    user_bars = st.slider("Number of Bars", 1, 8, 4)
    user_scale = st.selectbox(
        'Select Musical Scale',
        ('Major', 'Minor', 'Pentatonic Major', 'Pentatonic Minor'),
        index=0
    )
    generate_btn = st.button("Generate New Music")

if generate_btn:
    st.write("The AI is currently calculating frequencies and synthesizing the waveform.")

    # Generate Audio Logic
    fs = 44100  # Sample rate
    audio_data = create_ai_melody(user_tempo, user_bars, user_scale, fs)

    # Save the audio data to a BytesIO object
    buffer = io.BytesIO()
    wavfile.write(buffer, fs, audio_data)
    buffer.seek(0) # Rewind the buffer to the beginning

    st.write("Here's your AI-generated melody:")
    st.audio(buffer.getvalue(), format='audio/wav')

    st.download_button(
        label="Download Melody",
        data=buffer.getvalue(),
        file_name="ai_melody.wav",
        mime="audio/wav"
    )
