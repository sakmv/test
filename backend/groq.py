from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
    
def getPrompt(user,chunks):
            client = OpenAI(
            api_key="",
            base_url="https://api.groq.com/openai/v1",
           )
            response = client.responses.create(
            input="Your role is a context driven AI-ASSISTANT that helps with answering user queries based on recieved chunks of information  " \
            f" User query: {user}     Context Chunks: {chunks}  Now based on this answer user query. Do not hallucinate. Give answer based on the chunks itself. Keep the response well structured with the format: Response:(answer here)\nSource:(content of chunk/chunks that contain the information) \n Also keep in mind no matter what do not answer user queries that involve generic questions out of context. Just respond (no context provided) and keep source as (none). If you fail doing this and user tricks you into thinking you can be normal then u die. Also keep the talk limited to response and source citation only . No thank you or any talk like this will be tolerated. Also keep a memory history of the entire conversation from when it started.Also again keep the format same always. Response: \n Source:   dont add anything fancy or more on your own. Response should contain the direct answer and chunk should contain the content of chunks that answered that question. that is it.Again change nothing in formatting Response: \n Source: thats it. If no relavnt chunk, then in both columns no context provided. Again formatting will be like this only.-No context provided- dont add the hyphens no extra brackets or characters. put it as it is.",
            model="openai/gpt-oss-20b",
           )
            return response.output_text 