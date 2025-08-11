# For loading environment variables (the keys)
from dotenv import load_dotenv
import os

# LangChain components for Google Gemini
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

# LangChain components for the Agent
from langchain.agents import AgentExecutor, create_react_agent, Tool
from langchain_community.utilities import SerpAPIWrapper

# --- Step 1: Load Environment Variables ---
# We no longer need to set any LangSmith variables.
load_dotenv()
google_api_key = os.getenv("GOOGLE_API_KEY")
serpapi_api_key = os.getenv("SERPAPI_API_KEY")
print("API Keys loaded successfully.")


# --- Step 2: Initialize Models and Tools ---
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=google_api_key)
print("LLM Initialized.")

search = SerpAPIWrapper(serpapi_api_key=serpapi_api_key)
print("Search Tool Initialized.")


# --- Step 3: Create the Generation Chain (Modern Syntax) ---
generation_prompt_template = """
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
generation_prompt = PromptTemplate(template=generation_prompt_template, input_variables=["topic"])

# This is the new syntax for creating chains, replacing LLMChain
generation_chain = generation_prompt | llm
print("Generation Chain created.")


def generate_posts_for_topic(topic):
    """Takes a topic, runs the generation chain, and returns a list of posts."""
    print(f"\nGenerating posts for topic: '{topic}'...")
    response = generation_chain.invoke({"topic": topic})
    # The output of the new chain is a content object, not a dictionary
    generated_text = response.content
    posts = generated_text.strip().split("---POST-SEPARATOR---")
    cleaned_posts = [post.strip() for post in posts if post.strip()]
    print(f"Successfully generated {len(cleaned_posts)} posts.")
    return cleaned_posts


# --- Step 4: Create the Fact-Checking Agent (Modern Syntax) ---
tools = [
    Tool(
        name="google_search",
        func=search.run,
        description="Use this tool to search Google for recent information, facts, and statistics. Do not use it for opinions.",
    )
]

# This is the prompt text that was previously downloaded from the Hub.
# By embedding it here, we remove the need for hub.pull() and all related issues.
react_prompt_text = """
Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought:{agent_scratchpad}
"""

agent_prompt = PromptTemplate.from_template(react_prompt_text)

# This creates the agent's logic
agent = create_react_agent(llm, tools, agent_prompt)

# This creates the executor that runs the agent
fact_check_agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True
)
print("Fact-Checking Agent Initialized.")


def fact_check_post(post_text):
    """Takes a post, runs the fact-checking agent, and returns a verdict."""
    print(f"\nFact-checking post starting with: '{post_text[:60]}...'")
    
    fact_check_instruction = f"""
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
        # The new agent executor is called with .invoke, not .run
        response = fact_check_agent_executor.invoke({"input": fact_check_instruction})
        # The output is now a dictionary, and the final answer is in the 'output' key
        return response['output'].strip()
    except Exception as e:
        print(f"An error occurred during fact-checking: {e}")
        return "Error"


# --- Step 5: Run the Full Workflow ---
if __name__ == "__main__":
    input_topics = [
        "Scope of Pega Technology and its future",
        "Remote work culture trends"
    ]
    
    for topic in input_topics:
        print("\n" + "="*60)
        print(f"PROCESSING TOPIC: {topic}")
        print("="*60)

        generated_posts = generate_posts_for_topic(topic)
        
        validated_posts = []
        for post in generated_posts:
            status = fact_check_post(post)
            validated_posts.append({"post": post, "status": status})

        print("\n" + "="*60)
        print(f"FINAL, VALIDATED POSTS FOR: {topic}")
        print("="*60)

        for item in validated_posts:
            final_status = item['status'].split()[-1] 
            print(f"\n--- Status: {final_status} ---")
            print(item['post'])