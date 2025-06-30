# Part 3: Conceptual Understanding & System Proficiency

## 1. Agent Evaluation & Correctness

### a) How would you measure whether your agent is taking the correct action in response to the prompt?

To measure correctness, I use a multi-step evaluation framework:

- **LLM-as-Judge**: I implemented a second Gemini model that evaluates the output of the main trip planner agent. It scores the generated plan on relevance, clarity, helpfulness, fallback handling, and tone. Each criterion is scored from 1 to 5 with justifications.

- **Schema Validation**: The FastAPI app uses strict Pydantic schemas to ensure the output format is correct and consistent.

- **Manual Test Prompts**: I also maintain a set of edge-case prompts to verify that the agent handles ambiguous or hostile inputs correctly (e.g., unsupported cities, unsafe queries).

### b) Propose a mechanism to detect conflicting or stale results.

Conflicting or stale results can be identified through:

- **Weather Timestamp Validation**: Weather data from OpenWeatherMap includes a timestamp. If it is older than a certain threshold (e.g. 2 hours), the system can flag it as stale.

- **Fallback Detection**: If the itinerary generator returns vague or fallback activities (e.g., "Explore nearby attractions"), the evaluation model detects low relevance or helpfulness scores.

- **Response Hashing**: By caching response hashes for repeated prompts, we can compare current results to earlier responses to detect divergence or degradation over time.

---

## 2. Prompt Engineering Proficiency

### a) How do you design system prompts to guide agent behavior effectively?

I use structured, rule-based system prompts that define:

- **Agent role**: E.g., "You are a helpful and concise travel assistant"
- **Behavior guidelines**: Encourage conciseness, accuracy, and clarity
- **Boundaries**: Instruct the agent not to hallucinate facts or respond to unsafe requests
- **Fallback behavior**: Specify what to do when an external API fails (e.g., weather)

This helps the model understand its identity, tone, and expected responsibilities.

### b) What constraints, tone, and structure do you enforce, and how do you test them?

- **Constraints**:
  - No hallucinated information
  - No real-time or unverifiable data
  - Reject unsafe or abusive prompts
  - Output must follow a JSON schema

- **Tone**:
  - Friendly and enthusiastic
  - Helpful but professional
  - No excessive verbosity

- **Structure**:
  - Itineraries are formatted as time + activity + description
  - Evaluation outputs must be in strict JSON format with scores and justifications

- **Testing**:
  - I validate prompt behavior using a test suite of prompts including edge cases
  - I also review outputs via FastAPI endpoints and analyze LLM-as-Judge scoring
  - I iteratively adjust the prompt to improve consistency, coverage, and tone control

