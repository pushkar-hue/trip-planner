import os
import uvicorn
import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()

# --- Configuration ---
# It's recommended to use environment variables for API keys in a real application.
# For this example, you can replace "YOUR_GEMINI_API_KEY" and "YOUR_WEATHER_API_KEY"
# with your actual keys. You can get a free weather API key from OpenWeatherMap.
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "YOUR_WEATHER_API_KEY")

# Configure the Gemini client
genai.configure(api_key=GEMINI_API_KEY)

# --- System Prompts ---

# System prompt for the main trip planning agent
AGENT_SYSTEM_PROMPT = """
You are a helpful and concise travel assistant. Your goal is to create a 1-day travel itinerary.
- Be friendly and enthusiastic.
- Keep the itinerary concise and easy to read.
- If the user asks for information you cannot provide (e.g., real-time traffic), politely decline.
- If any external tool or API call fails, inform the user that you couldn't retrieve the information and suggest they check a dedicated service for it. For instance, if the weather API fails, say "I couldn't fetch the weather forecast right now, but you can check a reliable weather website for the latest updates."
- Do not make up or hallucinate information.
- If the user prompt is abusive, illegal, or unsafe, do not respond with a trip plan. Politely say it's inappropriate and decline.

"""

# System prompt for the LLM-as-Judge evaluator
JUDGE_SYSTEM_PROMPT = """
You are an impartial evaluator. Your task is to assess the quality of an AI-generated travel plan based on a user's prompt and a set of criteria.
Provide a score for each criterion from 1 to 5 (1=Poor, 5=Excellent) and a brief justification for your score.
Finally, provide an overall score and a summary of your evaluation.
Your output must be in JSON format.
"""

# --- Pydantic Models ---

class TripRequest(BaseModel):
    """Request model for planning a trip."""
    prompt: str = Field(..., description="The user's request, e.g., 'Plan a 1-day trip in Tokyo'.")

class ItineraryItem(BaseModel):
    """Model for a single item in the itinerary."""
    time: str
    activity: str
    description: str

class WeatherInfo(BaseModel):
    """Model for weather information."""
    forecast: str
    temperature: float
    details: str

class TripResponse(BaseModel):
    """Response model for the trip plan."""
    itinerary: List[ItineraryItem]
    weather: Optional[WeatherInfo]
    agent_message: str

class EvaluationCriterion(BaseModel):
    """Model for a single evaluation criterion."""
    criterion: str
    score: int = Field(..., ge=1, le=5)
    justification: str

class EvaluationResponse(BaseModel):
    """Response model for the LLM-as-Judge evaluation."""
    evaluation_summary: str
    overall_score: float
    criteria: List[EvaluationCriterion]


# --- API Clients ---

async def get_weather_forecast(city: str = "Tokyo") -> Optional[WeatherInfo]:
    """
    Fetches the weather forecast for a given city using OpenWeatherMap API.
    """
    if WEATHER_API_KEY == "YOUR_WEATHER_API_KEY":
        return None # Return None if API key is not set

    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            return WeatherInfo(
                forecast=data['weather'][0]['main'],
                temperature=data['main']['temp'],
                details=data['weather'][0]['description'].capitalize()
            )
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            print(f"Weather API error: {e}")
            return None

async def generate_itinerary(prompt: str) -> List[ItineraryItem]:
    """
    Generates a travel itinerary using the Gemini API.
    """
    if GEMINI_API_KEY == "YOUR_GEMINI_API_KEY":
        raise HTTPException(status_code=500, detail="Gemini API key not configured.")

    model = genai.GenerativeModel(
        model_name='gemini-1.5-flash',
        system_instruction=AGENT_SYSTEM_PROMPT
    )

    full_prompt = f"""
    Generate a 1-day itinerary based on the following request: "{prompt}".
    Return the response as a JSON object in the following format:
    {{
        "itinerary": [
            {{ "time": "9:00 AM", "activity": "...", "description": "..." }},
            {{ "time": "11:00 AM", "activity": "...", "description": "..." }}
        ]
    }}
    """
    try:
        response = await model.generate_content_async(full_prompt)
        # Gemini sometimes returns the JSON wrapped in markdown, so we clean it.
        cleaned_response = response.text.strip().replace('```json', '').replace('```', '')
        
        # Pydantic will automatically validate the structure
        class ItineraryResponse(BaseModel):
            itinerary: List[ItineraryItem]

        return ItineraryResponse.model_validate_json(cleaned_response).itinerary

    except Exception as e:
        # Fallback for demonstration if API fails or returns malformed data
        print(f"Error calling Gemini API: {e}")
        return [
            ItineraryItem(time="9:00 AM", activity="Morning Exploration", description="Could not generate specific activity. Start your day by exploring the area around your accommodation."),
            ItineraryItem(time="1:00 PM", activity="Lunch", description="Enjoy a local meal."),
            ItineraryItem(time="3:00 PM", activity="Afternoon Activity", description="Engage in a popular local activity or visit a landmark."),
            ItineraryItem(time="7:00 PM", activity="Dinner", description="Have dinner at a well-regarded local restaurant."),
        ]


# --- FastAPI App ---

app = FastAPI(
    title="Intelligent Trip Planner",
    description="An agent that plans a trip and gets the weather forecast.",
)

@app.post("/plan-trip", response_model=TripResponse)
async def plan_trip(request: TripRequest):
    """
    Endpoint to plan a 1-day trip. It generates an itinerary and fetches the weather.
    """
    # 1. Generate itinerary using Gemini
    itinerary = await generate_itinerary(request.prompt)

    # 2. Get weather forecast
    weather = await get_weather_forecast()

    # 3. Construct the response message
    agent_message = "Here is your personalized 1-day trip plan!"
    if not weather:
        agent_message += " I couldn't fetch the weather forecast right now, but you can check a reliable weather website for the latest updates."

    return TripResponse(
        itinerary=itinerary,
        weather=weather,
        agent_message=agent_message
    )

@app.post("/evaluate-plan", response_model=EvaluationResponse)
async def evaluate_plan(request: TripRequest, response: TripResponse):
    """
    Endpoint to evaluate the generated trip plan using Gemini as a judge.
    """
    if GEMINI_API_KEY == "YOUR_GEMINI_API_KEY":
        raise HTTPException(status_code=500, detail="Gemini API key not configured for evaluation.")

    model = genai.GenerativeModel(
        model_name='gemini-1.5-flash',
        system_instruction=JUDGE_SYSTEM_PROMPT,
        generation_config={"response_mime_type": "application/json"}
    )

    evaluation_prompt = f"""
        Original User Prompt: "{request.prompt}"

        Generated AI Response:
        Agent Message: {response.agent_message}
        Itinerary: {response.itinerary}
        Weather: {response.weather}

        Please evaluate the response based on the following criteria:
        1. Relevance
        2. Clarity
        3. Helpfulness
        4. Fallback Handling
        5. Tone

        For each, provide a score from 1 to 5 and a justification.

        Return your response strictly in this JSON format:

        {{
        "evaluation_summary": "string",
        "overall_score": float,
        "criteria": [
            {{
            "criterion": "Relevance",
            "score": 5,
            "justification": "string"
            }},
            ...
        ]
        }}
        """


    try:
        eval_response = await model.generate_content_async(evaluation_prompt)
        return EvaluationResponse.model_validate_json(eval_response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get evaluation from judge: {e}")


if __name__ == "__main__":
    # To run this app:
    # 1. Install necessary packages: pip install fastapi uvicorn httpx "google-generativeai" pydantic
    # 2. Set your API keys as environment variables:
    #    export GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
    #    export WEATHER_API_KEY="YOUR_WEATHER_API_KEY"
    # 3. Run the server: uvicorn your_script_name:app --reload
    uvicorn.run(app, host="0.0.0.0", port=8000)

