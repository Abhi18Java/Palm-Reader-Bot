import streamlit as st
import requests
import json
from PIL import Image
import os
from datetime import datetime

# Diwali theme configuration
st.set_page_config(
    page_title="🪔 AI Baba Palm Reader 🪔",
    page_icon="🪔",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for Diwali theme
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #ff6b35, #f7931e, #ffd700);
        background-attachment: fixed;
    }
    
    .stApp {
        background: linear-gradient(135deg, #1a1a2e, #16213e, #0f3460);
    }
    
    .title {
        text-align: center;
        color: #ffd700;
        font-size: 3rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        margin-bottom: 2rem;
    }
    
    .subtitle {
        text-align: center;
        color: #ff6b35;
        font-size: 1.5rem;
        margin-bottom: 2rem;
    }
    
    .prediction-box {
        background: linear-gradient(135deg, #ff6b35, #f7931e);
        padding: 20px;
        border-radius: 15px;
        border: 3px solid #ffd700;
        box-shadow: 0 0 20px rgba(255, 215, 0, 0.3);
        margin: 20px 0;
    }
    
    .prediction-text {
        color: white;
        font-size: 1.2rem;
        font-weight: bold;
        text-align: center;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
    }
    
    .diya {
        font-size: 2rem;
        animation: flicker 2s infinite alternate;
    }
    
    @keyframes flicker {
        0% { opacity: 1; }
        100% { opacity: 0.7; }
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #ff6b35, #f7931e);
        color: white;
        border: 2px solid #ffd700;
        border-radius: 25px;
        font-size: 1.2rem;
        font-weight: bold;
        padding: 10px 30px;
        box-shadow: 0 0 15px rgba(255, 215, 0, 0.3);
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0 0 25px rgba(255, 215, 0, 0.5);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'prediction_made' not in st.session_state:
    st.session_state.prediction_made = False
if 'current_image' not in st.session_state:
    st.session_state.current_image = None
if 'current_prediction' not in st.session_state:
    st.session_state.current_prediction = ""
if 'current_summary' not in st.session_state:
    st.session_state.current_summary = ""

# Header with Diwali decorations
st.markdown('<div class="diya">🪔</div>', unsafe_allow_html=True)
st.markdown('<h1 class="title">🪔 AI Baba Palm Reader 🪔</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">✨ Discover Your Destiny This Diwali ✨</p>', unsafe_allow_html=True)
st.markdown('<div class="diya">🪔 🎆 🪔 🎆 🪔</div>', unsafe_allow_html=True)

# Main content area
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    # Read Palm button
    if st.button("🔮 Read My Palm 🔮", key="read_palm"):
        with st.spinner("🪔 AI Baba is reading your palm... 🪔"):
            try:
                # Call FastAPI endpoint
                response = requests.post("http://127.0.0.1:8000/predict", json={})
                
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.current_summary = data['summary']
                    st.session_state.current_prediction = data['prediction']
                    st.session_state.current_image = data['image_path']
                    st.session_state.prediction_made = True
                else:
                    st.error("🚫 AI Baba is taking a break. Please try again!")
                    
            except Exception as e:
                st.error("🚫 Cannot connect to AI Baba. Make sure the FastAPI server is running!")

    # Display results if prediction was made
    if st.session_state.prediction_made:
        st.markdown("---")
        
        # Show hand image if available
        if st.session_state.current_image and os.path.exists(st.session_state.current_image):
            st.markdown("### 📸 Your Hand")
            image = Image.open(st.session_state.current_image)
            st.image(image, caption="Your Palm", use_column_width=True)
        
        # Show summary
        st.markdown("### 📊 Palm Analysis")
        st.info(f"🔍 {st.session_state.current_summary}")
        
        # Show prediction in styled box
        st.markdown("### 🔮 AI Baba's Prediction")
        st.markdown(f"""
        <div class="prediction-box">
            <div class="prediction-text">
                {st.session_state.current_prediction}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Next user button
        st.markdown("---")
        if st.button("🔄 Next Person's Turn 🔄", key="next_user"):
            st.session_state.prediction_made = False
            st.session_state.current_image = None
            st.session_state.current_prediction = ""
            st.session_state.current_summary = ""
            st.rerun()

# Footer with Diwali wishes
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #ffd700; margin-top: 2rem;">
    <p>🪔 ✨ Happy Diwali! May your future be as bright as the diyas! ✨ 🪔</p>
    <p style="font-size: 0.8rem; color: #ff6b35;">Powered by AI Baba's Ancient Wisdom & Modern Technology</p>
</div>
""", unsafe_allow_html=True)

# Auto-refresh for latest images (enhancement)
if st.session_state.prediction_made:
    st.markdown("""
    <script>
        // Auto-scroll to results
        window.scrollTo(0, document.body.scrollHeight);
    </script>
    """, unsafe_allow_html=True)