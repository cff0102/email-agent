import os
from openai import OpenAI
from app.gmail.gmail_prompt_formatter import format_prompt

def get_llm_response(prompt):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # or "gpt-4o-mini" if available and supported
        messages=[
            {"role": "system", "content": "You are a helpful assistant that processes emails."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )
    
    return response.choices[0].message.content