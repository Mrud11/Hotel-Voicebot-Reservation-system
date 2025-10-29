# Smart Voicebot Hotel Reservation System

## Overview
Smart Voicebot Hotel Reservation System is an AI-powered hotel booking web app for India that enables you to **search and book hotels conversationally using voice or text**. The app combines Streamlit for a slick UI, OpenAI Whisper for speech-to-text, gTTS for text-to-speech, Perplexity's Sonar model for conversational AI, and SerpApi for reliable hotel data and price comparisons.

---

## Features
- 🔍 Voice or text-based hotel search with natural language queries.
- 💰 Price comparison from multiple booking platforms simulated for better deals.
- 🛏️ Multi-step conversational booking, including room selection, dates, guest info, and confirmation — all via voice or text.
- 📊 View detailed price and rating comparisons.
- ✅ Bookings automatically saved locally in `bookings.xlsx` with downloadable receipts.
- 🎙️ Voice feedback at every step to guide and confirm user actions.

---

## Technologies Used
- Python 3.10+
- Streamlit
- OpenAI Whisper (local speech recognition)
- gTTS (text-to-speech)
- Perplexity Sonar API (conversational AI)
- SerpApi (hotel search and pricing)
- pandas, sounddevice, wavio, and others

---

## Installation

### 1. Clone the repository:
git clone <your-repository-url>
cd Hotel-Voicebot-Reservation-system


### 2. Install dependencies:
pip install -r requirements.txt


### 3. Create a `.env` file with your API keys:
PERPLEXITY_API_KEY=your_perplexity_api_key
SERPAPI_API_KEY=your_serpapi_api_key


### 4. Run the app:
streamlit run app.py


---

## Usage

- Start the app and provide your query via voice or text to search hotels.
- Browse price and rating comparisons.
- Select your hotel and provide booking info via voice or text.
- Confirm your booking to save it and receive a receipt.
- Use voice prompts throughout the experience for a seamless interaction.

---

## Contributing

Contributions and suggestions are welcome! Please submit issues and pull requests to improve the app.

---

## License

This project is licensed under the MIT License.

---

## Contact

For help or feedback, contact me at [r.mrudula27@gmail.com].


---



