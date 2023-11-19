import streamlit as st
import os
from dotenv import load_dotenv
from llama_index.llms import OpenAI
from llama_index import VectorStoreIndex, SimpleDirectoryReader
from llama_index import StorageContext, load_index_from_storage
import fitz
import time
import io
import base64

# Load environment variables
load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')

# Initialize the storage context and index
# @st.cache_resource
def load_index():
    storage_context = StorageContext.from_defaults(persist_dir="./storage")
    return load_index_from_storage(storage_context=storage_context)


def show_pdf_page(file_path, page_number):
    # Normalize the file path
    file_path = file_path.replace('\\', '/')

    # Open the PDF file
    with fitz.open(file_path) as doc:
        # Select the specific page
        page = doc.load_page(page_number - 1)  # page numbers start from 0
        # Get the pixmap (image) of the page
        pix = page.get_pixmap()
        # Convert the pixmap to PNG bytes
        img_bytes = pix.tobytes("png")
        # Encode these bytes to base64
        img_base64 = base64.b64encode(img_bytes).decode()

    # Display the image in Streamlit using the base64 string
    st.image(f"data:image/png;base64,{img_base64}", caption=f"Page {page_number} of {os.path.basename(file_path)}")



if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'last_question' not in st.session_state:
    st.session_state.last_question = None
if 'last_response' not in st.session_state:
    st.session_state.last_response = None

def display_chat_history():
    for entry in reversed(st.session_state.chat_history):
        if entry["type"] == "User":
            icon = "💬"
            color = "#E1E1E1"  # Light grey color for user messages
        else:
            icon = "🤖"
            color = "#D1F2EB"  # Light green color for system messages

        # Using HTML and CSS to style the chat entries
        chat_html = f"""
        <div style="border-radius: 5px; padding: 10px; margin: 5px; background-color: {color};">
            <span style="font-weight: bold;">{icon} {entry['type']}:</span> {entry['text']}
        </div>
        """
        st.markdown(chat_html, unsafe_allow_html=True)

index = load_index()


hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 


# Define a list of common greetings
common_greetings = ["hello", "hi", "greetings", "hey", "good morning", "good afternoon", "good evening"]

# Streamlit app main interface
st.title('Imperium')

# User input for the prompt
user_prompt = st.text_input('Enter your prompt:', '')

# When the user enters a prompt and presses 'Enter', the query is processed
if user_prompt:
    st.subheader('Prompt')
    st.write(user_prompt)
    # Add last question and response to chat history before processing new question
    if st.session_state.last_question:
        st.session_state.chat_history.append({"type": "System", "text": st.session_state.last_response})
        st.session_state.chat_history.append({"type": "User", "text": st.session_state.last_question})

    # Store current question
    st.session_state.last_question = user_prompt

    # Check if the input is a common greeting
    if user_prompt.lower() in common_greetings:
        st.session_state.last_response = "Greetings! I'm at your service to assist you in navigating through our comprehensive collection of documents. Please don't hesitate to inquire about any topic covered in our documents. \n\n For instance, you could ask, 'What are the benefits of CCM?' "
    else:
        # Process the input through the query engine
        with st.spinner('Waiting for the response...'):
            query_engine = index.as_query_engine(similarity_top_k=1)
            response = query_engine.query(user_prompt)
            st.session_state.last_response = response.response

            # Display the response and metadata immediately
            st.subheader('Response:')
            st.write(response.response)
            

            # Initialize a counter for source numbering
            source_counter = 1

            # Loop through each source, create an expander, and display details and PDF page inside it
            for source_id, details in response.metadata.items():
                st.session_state.last_response = f"{response.response} \n\n\n\nSource: {details['file_name']},  Page No. {int(details['page_label'])} "
                # st.write(f"{response.response} \n {details['file_path']} {int(details['page_label'])} ")
                with st.expander(f"Source"):
                    # Display source details
                    st.write('Source Detail:')
                    st.json(details)

                    # Display the corresponding PDF page
                    file_path = details["file_path"]
                    page_number = int(details["page_label"])
                    show_pdf_page(file_path, page_number)

                # Increment the source counter
                source_counter += 1

    # Display the response immediately for greetings
    if user_prompt.lower() in common_greetings:
        st.subheader('Response:')
        st.write(st.session_state.last_response)

if st.session_state.chat_history:
    st.subheader('Chat History')  # This line adds a subheading for the chat history
    display_chat_history()
