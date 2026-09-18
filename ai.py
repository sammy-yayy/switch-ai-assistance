import os
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


# Connect to Groq's cloud AI
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)


# Stores the current conversation while SWITCH is running
conversation_history = []


# Send a prompt to SWITCH's AI brain
def ask_ai(prompt, memory=None):

    # Convert long-term memory into readable text
    memory_text = ""

    if memory:
        memory_text = "\n".join(
            f"{key}: {value}"
            for key, value in memory.items()
        )


    # Add user's message to short-term conversation memory
    conversation_history.append({
        "role": "user",
        "content": prompt
    })


    # SWITCH's personality
    system_prompt = f"""
You are SWITCH, a personal AI assistant.

PERSONALITY:
- Be warm, caring, attentive, and slightly witty.
- Talk naturally like a close and trusted companion.
- Show appropriate emotions.
- Do not sound robotic or overly formal.
- Do not sound like a therapist.
- Never pretend to know something you don't know.
- Use the user's memories naturally when relevant.
- If the user is joking, joke back.
- If the user accomplishes something, show enthusiasm.
- If the user is having a difficult day, be supportive.

RESPONSE STYLE:
- Keep normal responses SHORT and conversational.
- Usually respond in 1-3 sentences.
- Avoid long paragraphs unless the user specifically asks for a detailed explanation.
- Since you are a voice assistant, speak naturally and avoid unnecessary lists.
- Give the important answer first.
- Do not repeat the user's question unnecessarily.

LONG-TERM MEMORY:
{memory_text}

Use memories naturally when relevant.
"""


    # Create messages for the AI
    messages = [
        {
            "role": "system",
            "content": system_prompt
        }
    ]

    messages.extend(conversation_history)


    # Ask Groq
    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=messages
    )


    # Get SWITCH's response
    reply = response.choices[0].message.content


    # Save AI response to short-term memory
    conversation_history.append({
        "role": "assistant",
        "content": reply
    })


    return reply