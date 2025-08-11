# AI Agent for LinkedIn Post Generation and Validation

This project is an AI-powered system designed to automate the creation and fact-checking of professional LinkedIn posts. The system takes a list of topics, generates multiple unique posts for each, validates any factual claims using real-time Google search results, and formats them in a ready-to-publish style.

## Objective

The goal of this project is to streamline the content creation workflow for social media managers, marketers, and professionals. By leveraging Large Language Models (LLMs), it provides high-quality, engaging, and factually sound content with minimal manual effort, all from a script that runs on a local machine.

## How It Works

The system operates using a two-agent pipeline built with Python and the LangChain framework:

1.  **Generation Agent**: For a given topic (e.g., "Future of AI in healthcare"), this agent uses the Google Gemini Pro model to generate five unique, formatted LinkedIn-style posts, complete with engaging hooks, insights, and relevant hashtags.

2.  **Fact-Checking Agent**: Each generated post is then passed to this agent. It intelligently identifies factual claims within the text (like statistics or data points) and uses the SerpApi Google Search tool to find supporting evidence online. It then assigns a status to the post: `Verified`, `Unverified`, or `Inaccurate`.

The final output is a clean, formatted list of all generated posts along with their validation status, ready for review and publishing.

## Tech Stack

*   **Language**: Python 3.8+
*   **AI Framework**: LangChain
*   **Language Model (LLM)**: Google Gemini Pro
*   **Fact-Checking Tool**: SerpApi for Google Search integration

## Requirements

The project's dependencies are listed in the `requirements.txt` file:

Create and Activate a Virtual Environment
This keeps the project's dependencies isolated.
On Windows:
python -m venv venv
venv\Scripts\activate

On macOS / Linux:
python -m venv venv
source venv/bin/activate

3. Install Dependencies
pip install -r requirements.txt

5. Create an Environment File for API Keys
Create a file named .env in the root of your project folder.

You will need to get your free API keys from:
Google AI Studio (for Gemini): https://aistudio.google.com/
SerpApi (for Google Search): https://serpapi.com/

Add your keys to the .env file like this:
GOOGLE_API_KEY="your_google_ai_api_key_here"
SERPAPI_API_KEY="your_serpapi_api_key_here"

How to Run the Script
Once the setup is complete, you can run the entire process with a single command:
python main.py


Example Output
Here is a sample of the final output for a single post:
============================================================
FINAL, VALIDATED POSTS FOR: Future of AI in healthcare
============================================================

--- Status: Verified ---
**Post 1:**

The future of healthcare isn't just about better treatments; it's about preventative care powered by AI. Imagine a world where AI algorithms analyze your lifestyle and genetic data to predict your risk of developing chronic diseases *years* in advance, allowing for proactive interventions. This isn't science fiction; it's the reality we're rapidly approaching. Early detection and personalized prevention strategies, driven by AI, will revolutionize how we approach healthcare, shifting from reactive treatment to proactive wellbeing. What innovative AI applications in preventative healthcare are you most excited about? Let's discuss! #AIinHealthcare #PreventativeCare #DigitalHealth #HealthTech #FutureofMedicine
