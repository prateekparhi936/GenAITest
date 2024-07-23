import streamlit as st
import google.generativeai as genai
import os

from config import GOOGLE_API_KEY

# Configure Google Generative AI with your API key
genai.configure(api_key=GOOGLE_API_KEY)

def upload_to_gemini(file, mime_type=None):
    """Uploads the given file to Gemini."""
    file = genai.upload_file(file, mime_type=mime_type)
    st.write(f"Uploaded file '{file.display_name}' as: {file.uri}")
    return file

# Create the model
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)

# Streamlit interface
st.title("ER Diagram to BigQuery Script Generator")

uploaded_file = st.file_uploader("Upload an Entity Relationship Diagram", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    mime_type = uploaded_file.type
    # Upload file to Gemini
    with open(uploaded_file.name, "wb") as f:
        f.write(uploaded_file.getbuffer())
    gemini_file = upload_to_gemini(uploaded_file.name, mime_type=mime_type)

    # Start a chat session with the uploaded file
    chat_session = model.start_chat(
        history=[
            {
                "role": "user",
                "parts": [
                    gemini_file,
                    "You are an intelligent system. I am going to provide an Entity relationship diagram. You need to read that diagram and develop a BigQuery script using that. Use temp tables to store the joined table results. In one temp table do not have more than 3 tables joined. Create a separate table to store more than 3 tables join. Subsequently use the temp tables created and form the logic.",
                ],
            }
        ]
    )

    response = chat_session.send_message("Use this to develop the script. Use the context from above and also use the annotation/notes from the diagram.")

    st.write("Generated BigQuery Script:")
    st.code(response.parts[0].text)
