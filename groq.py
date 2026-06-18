from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
    
def getPrompt(user,chunks):
            client = OpenAI(
            api_key="groq",
            base_url="https://api.groq.com/openai/v1",
           )
            response = client.responses.create(
            input="Your role is a context driven AI-ASSISTANT that helps with answering user queries based on recieved chunks of information  " \
            f" User query: {user}     Context Chunks: {chunks}  Now based on this answer user query. Do not hallucinate. Give answer based on the chunks itself. Keep the response well structured with the format: Response:(answer here)\nSource:(content of chunk/chunks that contain the information)",
            model="openai/gpt-oss-20b",
           )
            print(response.output_text)  