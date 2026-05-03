from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()  ## Load environment variables from .env file

## Initializing OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_answer(context, query):

    context_text = "\n\n".join(context)

    prompt = f"""
You are a strict data extraction AI.

You MUST follow these rules:

1. Use ONLY the numbers present in the context.
2. DO NOT create placeholders like X1, A1, etc.
3. DO NOT assume or invent values.
4. If exact values are found → show them clearly.
5. If partial data is found → show available values only.
6. If nothing is found → say "Data not available".

For monthly summary:
- Extract month-wise values directly from context
- Show actual numbers

Context:
{context_text}

Question:
{query}

Answer:
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content