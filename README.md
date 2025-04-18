# AI Job Matching Platform

A platform that uses AI to match candidates with job opportunities, conduct automated interviews, and notify recruiters of potential matches via Telegram.

## Features

- Job listings display
- Candidate profile creation
- Resume upload and parsing
- AI-powered interview chat
- Match scoring system
- Telegram notifications for recruiters

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with the following variables:
```
OPENAI_API_KEY=your_openai_api_key
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
```

5. Create necessary directories:
```bash
mkdir -p app/static/{resumes,profiles}
```

## Running the Application

1. Start the Streamlit application:
```bash
streamlit run app/main.py
```

2. Open your browser and navigate to `http://localhost:8501`

## Usage

1. **Job Listings**: Browse available job opportunities
2. **Profile Setup**: Create your candidate profile and upload your resume
3. **Interview Chat**: Participate in an AI-powered interview for specific positions
4. **Match Results**: View your match scores and recommendations

## Architecture

- **Frontend**: Streamlit for the user interface
- **AI Agent**: LangChain and LangGraph for interview and matching logic
- **Notifications**: Telegram bot for recruiter alerts
- **File Storage**: Local file system for resumes and profiles

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License
