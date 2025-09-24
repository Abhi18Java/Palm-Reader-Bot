# 🪔 AI Baba Palm Reader 🪔

A Diwali-themed palm reading application using AI, computer vision, and festive UI.

## Features

- 🔮 **Real-time palm reading** using MediaPipe hand detection
- 🪔 **Diwali festival theme** with beautiful gradients and animations
- 📸 **Hand image capture** and display
- 🤖 **AI-powered predictions** using OpenAI GPT-4
- 🔄 **Multi-user support** with next person functionality

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up OpenAI API key:**
   Create `.env` file with:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

3. **Run the application:**
   ```bash
   python run_app.py
   ```

   Or run separately:
   ```bash
   # Terminal 1 - FastAPI backend
   cd app
   uvicorn main:app --reload

   # Terminal 2 - Streamlit frontend
   streamlit run streamlit_app.py
   ```

## Usage

1. Open http://127.0.0.1:8501 in your browser
2. Click "🔮 Read My Palm 🔮" button
3. Show your hand to the camera
4. View your palm image and AI Baba's prediction
5. Click "🔄 Next Person's Turn 🔄" for the next user

## API Endpoints

- `POST /predict` - Get palm reading prediction
- Response includes: summary, prediction, image_path

## Project Structure

```
hand_reader_ai_baba/
├── app/
│   ├── main.py          # FastAPI backend
│   ├── hand_reader.py   # Hand detection & analysis
│   ├── ai_baba.py       # AI prediction generation
│   └── schemas.py       # Pydantic models
├── images/              # Captured hand images
├── streamlit_app.py     # Streamlit UI
├── run_app.py          # Startup script
└── requirements.txt     # Dependencies
```

## Enhancements Made

- **Diwali Theme**: Golden colors, diyas, gradients, animations
- **Image Display**: Shows captured hand above prediction
- **Session Management**: Maintains state between interactions
- **Error Handling**: Graceful handling of camera/API errors
- **Responsive Design**: Centered layout with proper spacing
- **Auto-scroll**: Scrolls to results automatically
- **Visual Feedback**: Loading spinners and status messages

Happy Diwali! 🪔✨