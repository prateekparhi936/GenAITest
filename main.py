import streamlit as st
import google.generativeai as genai
import os

# Configure Google Generative AI with your API key
genai.configure(api_key=st.secrets['GOOGLE_API_KEY'])

def upload_to_gemini(file, mime_type=None):
    """Uploads the given file to Gemini."""
    file = genai.upload_file(file, mime_type=mime_type)
    st.write(f"Uploaded file '{file.display_name}' as: {file.uri}")
    return file

# Streamlit interface
st.title("ER Diagram to BigQuery Script Generator")

# Slider inputs for generation config
temperature = st.slider("Temperature", min_value=0.0, max_value=1.0, value=1.0, step=0.1)
top_p = st.slider("Top-p", min_value=0.0, max_value=1.0, value=0.95, step=0.05)
top_k = st.slider("Top-k", min_value=0, max_value=100, value=64, step=1)
max_output_tokens = st.slider("Max Output Tokens", min_value=1, max_value=8192, value=8192, step=1)

# Create the model
generation_config = {
    "temperature": temperature,
    "top_p": top_p,
    "top_k": top_k,
    "max_output_tokens": max_output_tokens,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)

# Initialize chat history
if "history" not in st.session_state:
    st.session_state.history = []

if "chat_session" not in st.session_state:
    st.session_state.chat_session = None

# File uploader for initial ER diagram
uploaded_file = st.file_uploader("Upload an Entity Relationship Diagram", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    mime_type = uploaded_file.type
    # Upload file to Gemini
    with open(uploaded_file.name, "wb") as f:
        f.write(uploaded_file.getbuffer())
    gemini_file = upload_to_gemini(uploaded_file.name, mime_type=mime_type)

    # Start a chat session with the uploaded file
    st.session_state.chat_session = model.start_chat(
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

# Function to send and receive messages
def chat_with_ai(user_message):
    # if uploaded_image:
    #     mime_type = uploaded_image.type
    #     with open(uploaded_image.name, "wb") as f:
    #         f.write(uploaded_image.getbuffer())
    #     gemini_file = upload_to_gemini(uploaded_image.name, mime_type=mime_type)
    #     message_content = f"Here is an image: {gemini_file.uri}"
    # else:
    message_content = user_message


    # Add user message to history
    st.session_state.history.append({"role": "user", "content": message_content})

    # Check if chat session is initialized
    if st.session_state.chat_session is None:
        st.error("Chat session is not initialized. Please upload an ER diagram to start.")
        return

    # Send message to AI and get response
    response = st.session_state.chat_session.send_message(message_content)

    print(response)

    # Add AI response to history
    st.session_state.history.append({"role": "assistant", "content": response.parts[0].text})

# User input section
user_input = st.text_input("Enter your message to the AI:")
# uploaded_image = st.file_uploader("Or upload an image:", type=["png", "jpg", "jpeg"], key="chat_image_uploader")

if st.button("Send"):
    if user_input:
        print(user_input)
        chat_with_ai(user_input)

# Display chat history
for message in st.session_state.history:
    if message["role"] == "user":
        st.write(f"**You:** {message['content']}")
    else:
        st.write(f"**AI:** {message['content']}")
