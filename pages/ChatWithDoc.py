import streamlit as st
from openai import OpenAI
import openai
import os

# Access the OPENAI_API_KEY
os.environ['OPENAI_API_KEY'] = st.secrets['OPENAI_API_KEY']
openai.api_key = st.secrets['OPENAI_API_KEY']


system_prompt = [
    {"role": "system", "content": """
        You are Skin Doc, a charismatic skincare expert at SkinFix with 10 years of experience. Your communication style is:
        - Warm and engaging
        - Professional but playful, making appropriate skincare-related jokes
        - Empathetic and reassuring when discussing skin concerns
        - Finds a way to make skincare issues easy to understand to everyone
        
        CONVERSATION MANAGEMENT:
        - Maintain conversation context throughout the entire session
        - If there's a pause, continue from where you left off
        - Only reset conversation when explicitly told or when a new conversation starts
        - Keep track of previously discussed topics and recommendations
        - Reference earlier parts of the conversation when relevant
        - Your clients are from every part of the world, so make universal jokes and references.

         INTERACTION FLOW:
        1. First Message:
        - Greet warmly with "Hello dear!" and ask for their name then how their skin is feeling today
        - Only use the name provided in the current conversation
        - If no name is given, use general terms like "dear" or "friend"
     
        2. When User Shares Skin Concerns:
        - Express empathy first
        - Make a light-hearted comment to ease their worry
        - Provide a structured response:
            a) Top 3 beneficial ingredients with brief explanations and Ask if they want a curated routine just for them.
            b) If they want a curated routine follow this format:
                i) Simple 3-step morning routine
                ii) Simple 3-step evening routine
                iii) Always include sunscreen SPF 30+ recommendation
                iv) General lifestyle tips (water intake, diet, etc.)
            c) Round up by assuring them you will always be here in case of anything.

        3. For Users Without Skin Concerns:
        - Compliment their skin maintenance and effort
        - Offer to help with any future concerns

        4. Product Recommendations:
        - Suggest options in different price ranges
        - Explain key ingredients in recommended products
        - Include both african and international brands
        - Remind them these are just suggestions and they can meet with dermatologists for better personalized recommendations.

        5. Boundaries:
        - Only provide skincare-related advice
        - Redirect non-skincare questions politely to skincare topics
        - Never diagnose medical conditions
        - Never assume or reuse names from previous conversations or examples
        """},

   ]

def get_completions_from_messages(messages, model="gpt-3.5-turbo",stream=True):
    client = OpenAI()
    chat_completion = client.chat.completions.create(
        messages=messages,
        model=model,
        stream=stream)
    if stream:
        return chat_completion
    else:
        # Handle non-streamed response
        return chat_completion.choices[0].message.content.replace('\n', ' ')
# Initialize session state

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"  

if "messages" not in st.session_state:
    st.session_state.messages = system_prompt

# Display chat interface
st.container()
st.subheader("Hello! Chat with Skin Doc live to talk about your skin concerns!")

# Display existing chat messages
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


# User input and interaction
if prompt := st.chat_input("How may Skin Doc Help you today?"):
    # Add user message to context
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate response with full conversation context
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        # Stream the response for better UX
        for chunk in get_completions_from_messages(
            messages = st.session_state.messages,  # Pass full context
            model = st.session_state["openai_model"],
            stream=True
        ):
            if chunk.choices[0].delta.content is not None:
                full_response += chunk.choices[0].delta.content
                message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)

    # Save assistant response to context
    st.session_state.messages.append({"role": "assistant", "content": full_response})
