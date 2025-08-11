# For loading environment variables (the keys)
from dotenv import load_dotenv
import os

# LangChain components for Google Gemini
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# LangChain components for the Agent
from langchain.agents import AgentType, Tool, initialize_agent
from langchain_community.utilities import SerpAPIWrapper

# --- Step 1: Load Environment Variables ---
# This command finds the .env file and loads the variables
load_dotenv()

# We can now access the keys using os.getenv()
google_api_key = os.getenv("GOOGLE_API_KEY")
serpapi_api_key = os.getenv("SERPAPI_API_KEY")

print("API Keys loaded successfully.")


# --- Step 2: Initialize Models, Tools, and Agents ---
# Initialize the Language Model (LLM)
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", google_api_key=google_api_key)
print("LLM Initialized.")

# Initialize the Search Tool
search = SerpAPIWrapper(serpapi_api_key=serpapi_api_key)
print("Search Tool Initialized.")

# Create the List of Tools for the Agent
tools = [
    Tool(
        name="google_search",
        func=search.run,
        description="Use this tool to search Google for recent information, facts, and statistics. Do not use it for opinions.",
    )
]

# Initialize the Fact-Checking Agent
# verbose=True lets us see the agent's "thought process"
fact_check_agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    handle_parsing_errors=True
)
print("Fact-Checking Agent Initialized.")


# --- Step 3: Define the Post-Generation Components ---
prompt_template_text = """
You are an expert social media strategist specializing in creating viral LinkedIn content.
Your task is to generate 5 unique, engaging, and professional LinkedIn posts for the topic: "{topic}".

For each of the 5 posts, you must follow these rules:
1.  **Tone:** Professional, insightful, and confident.
2.  **Length:** Keep each post concise, ideally between 100 and 200 words.
3.  **Structure:** Start with a strong, attention-grabbing hook. Provide a key insight, a surprising fact, or a valuable tip. End with a question or a call-to-action to encourage comments and engagement.
4.  **Formatting:** Use bullet points or numbered lists for clarity where appropriate.
5.  **Hashtags:** Include 3-5 highly relevant hashtags at the end of each post (e.g., #AI, #Tech, #FutureOfWork).
6.  **Uniqueness:** Ensure all 5 posts are distinct from each other, offering different angles or perspectives on the main topic.

IMPORTANT: After each post, add a clear separator like '---POST-SEPARATOR---' to make them easy to split and process.
"""

prompt = PromptTemplate(
    input_variables=["topic"],
    template=prompt_template_text
)

generation_chain = LLMChain(llm=llm, prompt=prompt)

def generate_posts_for_topic(topic):
    """Takes a topic, runs the generation chain, and returns a list of posts."""
    print(f"\nGenerating posts for topic: '{topic}'...")
    response = generation_chain.invoke({"topic": topic})
    generated_text = response['text']
    posts = generated_text.strip().split("---POST-SEPARATOR---")
    cleaned_posts = [post.strip() for post in posts if post.strip()]
    print(f"Successfully generated {len(cleaned_posts)} posts.")
    return cleaned_posts


# --- Step 4: Define the Fact-Checking Function ---
def fact_check_post(post_text):
    """Takes a post, runs the fact-checking agent, and returns a verdict."""
    print(f"\nFact-checking post starting with: '{post_text[:60]}...'")

    fact_check_prompt = f"""
    Please analyze the following LinkedIn post. Your task is to perform a fact-check on any specific claims.

    1. First, identify any clear, verifiable claims in the text (e.g., statistics, specific facts, data points). If there are no specific claims, you must conclude that the post is "Unverified".
    2. For each claim, use the google_search tool to find credible sources to verify it.
    3. Based on your search results, provide a final, one-word verdict for the post.

    The verdict must be one of the following:
    - "Verified": If all major claims are well-supported by the search results.
    - "Unverified": If you cannot find information to support the claims, or the claims are opinions that cannot be verified.
    - "Inaccurate": If search results directly contradict the claims.

    Here is the post:
    "{post_text}"

    Begin your analysis now. Reason step-by-step and use the search tool if necessary. Conclude with the final verdict as a single word.
    """
    
    try:
        response = fact_check_agent.run(fact_check_prompt)
        return response.strip()
    except Exception as e:
        print(f"An error occurred during fact-checking: {e}")
        return "Error"


# --- Step 5: Run the Full Workflow ---
if __name__ == "__main__":
    input_topics = [
        "Future of AI in healthcare",
        "Remote work culture trends"
    ]
    
    # Process each topic from the list
    for topic in input_topics:
        print("\n" + "="*60)
        print(f"PROCESSING TOPIC: {topic}")
        print("="*60)

        # Step 1: Generate posts for the topic
        generated_posts = generate_posts_for_topic(topic)
        
        # Step 2: Fact-check each generated post
        validated_posts = []
        for post in generated_posts:
            status = fact_check_post(post)
            validated_posts.append({"post": post, "status": status})

        # Step 3: Format and display the final, ready-to-publish output
        print("\n" + "="*60)
        print(f"FINAL, VALIDATED POSTS FOR: {topic}")
        print("="*60)

        for item in validated_posts:
            # Clean up the final status in case the agent adds extra text
            final_status = item['status'].split()[-1] 
            print(f"\n--- Status: {final_status} ---")
            print(item['post'])