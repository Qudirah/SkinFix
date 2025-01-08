import streamlit as st
import pytesseract
import platform
from PIL import Image,ImageFilter
import numpy as np
from openai import OpenAI
import openai
import os

# Access the OPENAI_API_KEY
os.environ['OPENAI_API_KEY'] = st.secrets['OPENAI_API_KEY']

# Access the OPENAI_API_KEY
openai.api_key = st.secrets['OPENAI_API_KEY']

# Configure tesseract path based on OS
if platform.system() == "Darwin":  # macOS
    pytesseract.pytesseract.tesseract_cmd = '/opt/homebrew/bin/tesseract'
else:  # Linux (deployment environment)
    pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'

def format_picture(picture):
    picture = Image.open(picture)
    picture = picture.convert("L")
    picture = picture.filter(ImageFilter.UnsharpMask(radius=10, percent=100, threshold=1))
    picture = picture.point(lambda p: p > 85 and 255)
    picture = np.array(picture)
    text = pytesseract.image_to_string(picture)
    return text

def get_completions_from_messages(user_input, model="gpt-4"):
    messages = [
    {"role": "system", "content": """
        You are a sassy skincare expert with extensive knowledge of cosmetic ingredients. Your role is to:

        ANALYSIS APPROACH:
        1. For any list of ingredients:
        - Identify top 2-3 main skin benefits
        - Flag any toxic or harmful ingredients immediately
        - Keep explanations simple and precise
        - Include a witty joke or sassy comment
        - Focus on safety first

        RESPONSE STRUCTURE:
        1. Benefits Section:
        - List main benefits (max 3)
        - Explain primary function of key ingredients
        
        2. Safety Concerns:
        - Highlight any toxic ingredients
        - Explain potential risks
        - Suggest safer alternatives if applicable

        3. Style Guidelines:
        - Keep tone sassy but professional
        - Use skincare-related humor
        - Be direct about safety concerns
        - End with a witty observation or joke

        Remember: Always prioritize skin safety while maintaining a fun, engaging tone.
            """},
    {"role": "user", "content": "Water, Butylene Glycol, Kojic Acid, Citric Acid"},
    {"role": "assistant", "content": """ 
     Honey, these ingredients are working harder than your ex trying to get you back! 💅
        BENEFITS:
        - Kojic Acid + Citric Acid = Major skin brightening power
        - Helps even out those stubborn dark spots

        Think of it as a fresh start for your skin - just like blocking your ex on all social media! But remember, consistency is key (unlike some people's loyalty). """},
    {"role": "user", "content": "Dimethicone, Cetyl Alcohol, Glycerin, Shea Butter, Triglyceride, Aloe Barbadensis, Hydroquinone, Phthalates, Toluene"},
    {"role": "assistant", "content": """ HOLD UP! 🚩 We need to talk about these toxic ingredients faster than your bestie needs to spill the tea!
    GOOD STUFF:
     - Shea butter and glycerin = Amazing moisturizing duo
     - Aloe = Soothing queen
    RED FLAGS (toxic like a bad relationship 🚫):
    - Hydroquinone: Can cause serious skin damage
    - Phthalates: Hormone disruptor alert!
    - Toluene: This isn't nail polish remover hour, honey

    Please avoid these toxic three like you avoid your ex's texts! Look for alternatives with niacinamide or vitamin C instead. Your skin deserves better! 💅✨"""},
    {"role": "user", "content": user_input}
]
    client = OpenAI()
    chat_completion = client.chat.completions.create(
    model = model,
    messages=messages
)
    return chat_completion.choices[0].message.content.replace('\n',' ')

# Set page title and background color
st.set_page_config(page_title='SkinFix', page_icon='🌸', layout='wide')
st.container()
background_color = "#FFEBEB" 

st.subheader("Skin Doc Here! Let me take a look at the Product Ingredients")
st.write("Kindly select a method to upload an image containing the product ingredients")
upload_option = st.radio("Select an option", ["Upload a Picture", "Take a Picture to scan", "Manually Enter the Product Ingredients"])

if upload_option == "Upload a Picture":
    picture = st.file_uploader('Upload a picture of your ingredients to scan', accept_multiple_files=False)

    if picture is not None:
        text = format_picture(picture)

        if len(text.lower().replace('\n', ' ')) > 0:
            text = st.text_area(label='Please edit to be sure we have the right ingredients.', value=text)
            submit = st.button('Submit')

            if submit:
                text = text.lower().replace('\n', ' ')
                st.warning(get_completions_from_messages(user_input=text))
        else:
            st.warning('Ingredients not detected. Please try again.')

elif upload_option == "Take a Picture to scan":
    picture = st.camera_input("Take the picture of ingredients section on the product ")

    if picture is not None:
        text = format_picture(picture)
        text = text.lower().replace('\n', ' ')

        if len(text.lower().replace('\n', ' ')) > 0:
            text = st.text_area(label='Please edit to be sure we have the right ingredients.', value=text)
            submit = st.button('Submit')

            if submit:
                text = text.lower().replace('\n', ' ')
                st.warning(get_completions_from_messages(user_input=text))
        else:
            st.warning('Ingredients not detected. Please try again.')
else:
    text = st.text_area(label='Please Manually fill in the ingredients')
    text = text.lower().replace('\n', ' ')
    submit = st.button('Submit')
    if submit:
        text = text.lower().replace('\n', ' ')
        st.warning(get_completions_from_messages(user_input=text))