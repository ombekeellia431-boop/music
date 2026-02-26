import streamlit as st
import numpy as np
from scipy.io import wavfile
import io
import random
from streamlit_mic_recorder import mic_recorder

st.set_page_config(page_title="Audio Creative Suite", layout="wide")

def generate_tone(freq, duration, sample_rate, wave_type):
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    if wave_type == "Pure Sinus":
        audio = np.sin(2 * np.pi * freq * t)
    elif wave_type == "Rich Square":
        audio = np.sign(np.sin(2 * np.pi * freq * t))
    elif wave_type == "Soft":
        audio = 0.5 * np.sin(2 * np.pi * freq * t) + 0.2 * np.sin(4 * np.pi * freq * t)
    
    # Apply a small fade in/out to avoid clicks
    fade = int(0.1 * sample_rate)
    envelope = np.ones_like(audio)
    envelope[:fade] = np.linspace(0, 1, fade)
    envelope[-fade:] = np.linspace(1, 0, fade)
    return audio * envelope

def get_scale_frequencies(scale_type):
    base_freq = 440.0  # A4
    major_intervals = [0, 2, 4, 5, 7, 9, 11, 12]
    minor_intervals = [0, 2, 3, 5, 7, 8, 10, 12]
    pentatonic_intervals = [0, 2, 4, 7, 9, 12]
    
    if scale_type == "Major":
        intervals = major_intervals
    elif scale_type == "Minor":
        intervals = minor_intervals
    else:
        intervals = pentatonic_intervals
        
    return [base_freq * (2 ** (i / 12)) for i in intervals]

st.sidebar.title("Navigation Menu")
app_mode = st.sidebar.selectbox("Choose functionality", ["Melody Generator", "Voice Recorder & Enhancement", "Text Entry"])

if app_mode == "Melody Generator":
    st.title("AI Melody Generator")
    
    col1, col2 = st.columns(2)
    with col1:
        instrument = st.selectbox("Select Instrument", ["Pure Sinus", "Rich Square", "Soft"])
        scale_choice = st.selectbox("Select Scale", ["Major", "Minor", "Pentatonic"])
    
    with col2:
        bpm = st.slider("Tempo (BPM)", min_value=60, max_value=180, value=120)
        measures = st.slider("Number of Measures", min_value=1, max_value=8, value=4)

    if st.button("Generate Random Melody"):
        sample_rate = 44100
        sec_per_beat = 60 / bpm
        note_duration = sec_per_beat / 2  # Eighth notes
        total_notes = measures * 8
        
        scale_freqs = get_scale_frequencies(scale_choice)
        full_melody = np.array([], dtype=np.float32)
        
        for _ in range(total_notes):
            freq = random.choice(scale_freqs)
            note_wave = generate_tone(freq, note_duration, sample_rate, instrument)
            full_melody = np.concatenate((full_melody, note_wave))
            
        # Normalize to 16-bit PCM
        full_melody = (full_melody * 32767).astype(np.int16)
        
        # Buffer for download
        buffer = io.BytesIO()
        wavfile.write(buffer, sample_rate, full_melody)
        
        st.audio(buffer, format="audio/wav")
        st.download_button(label="Download Melody as WAV", data=buffer.getvalue(), file_name="melody.wav", mime="audio/wav")

elif app_mode == "Voice Recorder & Enhancement":
    st.title("Voice Recording & Enhancement")
    
    st.write("Click the button below to record your voice:")
    audio_record = mic_recorder(start_prompt="Start Recording", stop_prompt="Stop Recording", key="recorder")
    
    if audio_record:
        st.audio(audio_record["bytes"], format="audio/wav")
        
        if st.button("Enhance Recorded Voice"):
            # Simulation of enhancement (Normalization and gain)
            audio_data = np.frombuffer(audio_record["bytes"], dtype=np.int16)
            enhanced_audio = np.array(audio_data, dtype=np.float32)
            enhanced_audio = enhanced_audio / np.max(np.abs(enhanced_audio))
            enhanced_audio = (enhanced_audio * 32767).astype(np.int16)
            
            enhanced_buffer = io.BytesIO()
            wavfile.write(enhanced_buffer, 44100, enhanced_audio)
            
            st.write("Enhanced Audio:")
            st.audio(enhanced_buffer, format="audio/wav")
            st.download_button(label="Download Enhanced Voice", data=enhanced_buffer.getvalue(), file_name="enhanced_voice.wav", mime="audio/wav")

elif app_mode == "Text Entry":
    st.title("Text Information")
    user_name = st.text_input("Enter Project Name", "My Awesome Music")
    user_desc = st.text_area("Description", "This is a melody generated with Python and Streamlit.")
    
    st.info(f"Project: {user_name}")
    st.write(f"Details: {user_desc}")
