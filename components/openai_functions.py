from openai import OpenAI
import streamlit as st
import json

OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=OPENAI_API_KEY)

def json_data(extracted_text: str):
    try:
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "structure_pdf_content",
                    "description": "Convert unstructured text into structured JSON format",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string", "description": "Document title"},
                            "sections": {"type": "array", "items": {"type": "string", "description": "Section headings"}},
                            "Skills": {"type": "array", "items": {"type": "string", "description": "Key points"}},
                            "experience": {"type": "array", "items": {"type": "string", "description": "Keywords"}},
                            "summary": {"type": "string", "description": "Brief summary"}
                        },
                        "required": ["title", "sections", "key_points", "keywords", "summary"]
                    }
                }
            }
        ]

        messages = [
            {
                "role": "system",
                "content": """Convert unstructured text into structured JSON with:
                - title
                - sections (array)
                - skills (array)
                - experience (array)
                - summary"""
            },
            {"role": "user", "content": extracted_text}
        ]

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            tools=tools,
            max_tokens=1000,
            tool_choice="auto"
        )

        if response and response.choices and response.choices[0].message.tool_calls:
            structured_data = response.choices[0].message.tool_calls[0].function.arguments
            return json.loads(structured_data)
        else:
            return {"error": f"Invalid response structure: {response}"}

    except Exception as e:
        return {"error": str(e)}
