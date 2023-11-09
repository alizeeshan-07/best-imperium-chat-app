

# import os
# from dotenv import load_dotenv
# from llama_index.llms import OpenAI
# from llama_index import VectorStoreIndex, SimpleDirectoryReader
# from IPython.display import Markdown, display
# import streamlit as st
# from llama_index import StorageContext, load_index_from_storage
# load_dotenv()
# openai_api_key = os.getenv('OPENAI_API_KEY')


# # documents = SimpleDirectoryReader("data").load_data()
# # index = VectorStoreIndex.from_documents(documents)
# # index.storage_context.persist()

# storage_context = StorageContext.from_defaults(persist_dir="./storage")
# index = load_index_from_storage(storage_context=storage_context)

# query_engine = index.as_query_engine()
# response=query_engine.query("What is data handling?")
# print(f"response from the llm is:\n {response.response}")
# print(f"reference details are: \n {response.metadata}")

import threading
import os
import streamlit as st
from dotenv import load_dotenv
from llama_index.llms import OpenAI
from llama_index import VectorStoreIndex, SimpleDirectoryReader
from llama_index import StorageContext, load_index_from_storage

# Load environment variables
load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')

# Initialize the storage context and index
@st.cache_resource
def load_index():
    storage_context = StorageContext.from_defaults(persist_dir="./storage")
    return load_index_from_storage(storage_context=storage_context)

index = load_index()

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Initialize the Streamlit app
st.title('Imperium')

# User input for the prompt
user_prompt = st.text_input('Enter your prompt:', '')

# When the user enters a prompt and presses 'Enter', the query is processed
if user_prompt:
    with st.spinner('Waiting for the response...'):
        query_engine = index.as_query_engine()
        response = query_engine.query(user_prompt)
    
    # Display the response and metadata outside the 'with' block
    st.subheader('Response:')
    st.write(response.response)
    st.subheader('Source(s) Detail:')
    st.write(response.metadata)








