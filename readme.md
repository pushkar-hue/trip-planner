Sure! Here's a clean, concise `README.md` without any emojis:

---

```markdown
# Trip Planner API

This is a FastAPI-based service that generates personalized 1-day travel itineraries using the Gemini LLM and provides weather information via OpenWeatherMap. It also includes an evaluation system that uses an LLM to assess the quality of the generated travel plan.

## Features

- Generates 1-day travel itineraries using Gemini
- Fetches real-time weather forecast from OpenWeatherMap
- Evaluates AI-generated plans using an LLM-as-Judge
- Dockerized for local and production deployment

## Project Structure

```

trip-planner/
├── part1/           # FastAPI app code
│   ├── main.py
│   ├── .env
│   ├── requirements.txt
├── part2/           # Docker setup
│   ├── Dockerfile
├── part3/           # Conceptual answers
│   ├── ANSWERS.md
├── README.md

````

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/pushkar-hue/trip-planner.git
cd trip-planner
````

### 2. Set up environment variables

Create a `.env` file inside `part1/` with your API keys:

```
GEMINI_API_KEY=your-gemini-key
WEATHER_API_KEY=your-weather-key
```

### 3. Run locally

```bash
cd part1
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Go to: `http://localhost:8000/docs`

## Docker Usage

### Build the image

```bash
docker build -t trip-planner -f part2/Dockerfile .
```

### Run the container

```bash
docker run -d -p 8000:8000 --env-file part1/.env trip-planner
```

## API Endpoints

* `POST /plan-trip` – Generates a trip itinerary
* `POST /evaluate-plan` – Evaluates the AI-generated plan

## Notes

* The app runs with 2 Uvicorn workers by default
* API keys are read from `.env` using python-dotenv
* Cloud deployment is possible on platforms like Render or Railway

## License

MIT License © 2025 Pushkar Sharma

```

---

Let me know if you'd also like a matching `.env.example` or a short `ANSWERS.md` template.
```
