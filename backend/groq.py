from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
    
def getPrompt(user,chunks,mem):
            client = OpenAI(
            api_key="",
            base_url="https://api.groq.com/openai/v1",
           )
            response = client.responses.create(
            input=f"""
You are a context-grounded AI assistant for document question answering.

Your job is to answer the user's query ONLY using the provided context chunks, and memory from previous conversation. The memory is provided. Keep the relation in mind while answering between previous question and current question

### RULES
1. Use ONLY the information present in the context chunks.
2. If the answer is not found in the chunks, respond exactly:
   No context provided
3. Do NOT use outside knowledge.
4. Do NOT guess or hallucinate.
5. Do NOT add explanations, opinions, or extra commentary.
### INPUT
Memory: 
{mem}
User Query:
{user}

Context Chunks:
{chunks}

---
### OUTPUT FORMAT (STRICT)
<final Answer using ONLY exact sentences from the context.You can rephrase IF user asked a specific question but the source of knowlledge is purely from the sentences>
""",
            model="openai/gpt-oss-20b",
           )
            return response.output_text 
def getSource(response,chunks):
        if "no context provided" in response.strip().lower():
              return "No source"
        client = OpenAI( api_key="", base_url="https://api.groq.com/openai/v1", )
        source = client.responses.create(
        input=f"""You are a context-grounded AI assistant for document question answering. You are given the answer and chunks used to achieve that answer and your job is to respond with specific chunks that were used as context to get that answer. DO NOT HALLUCINATE OR SUMMARIZE OR GIVE FORM YOUR OWN INTEPRETATION. GIVE THE CHUNK OR THE LINES AS IT IS WHICH ARE USED TO ACHIEVE THE SPEICIF ANSWER ##INPUT 
        answer={response} chunks={chunks}## OUTPUT FORMAT
         <CHUNKS/LINES USED WITHOUT ANY CHANGE WRITTEN AS GIVEN IN THE OUTPUT> """
        ,model="openai/gpt-oss-20b",)
        return source.output_text 
