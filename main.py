import os
import openai
import sys
import streamlit as st
import time

from langchain.llms import OpenAI

from langchain.chains import LLMChain
from langchain.prompts import (PromptTemplate)
from langchain.memory import (ConversationSummaryMemory)

sys.path.append('../..')

from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())  # read local .env file

openai.api_key = os.environ['OPENAI_API_KEY']

# wide format and displays title
st.set_page_config(page_title="Lesson Planner", layout="wide")
st.title("Lesson Planner")

# instructions
with st.expander('Instructions'):
    st.markdown(':blue[1. choose a subject from the left column]')
    st.markdown(':red[2. in the left column, choose the lesson, assignment, project, or rubric]')
    st.markdown(':orange[3. in the left column, type in the specific topic you would like to be the focus of your lesson]')
    st.markdown(':green[4. in the chat box, specify the length of time and any other ideas or constraints for the project or lesson]')

# options for temp variables in template, displayed in sidebar
with st.sidebar:
    option = st.selectbox(
        'Choose a category:',
        ('English', 'Math', 'Science', 'History','Latin', 'Mandarin', 'Spanish', 'Health', 'Athletics', 'Art', 'Music')
    )
    lessonType = st.selectbox(
        'Choose a lesson category:',
        ('Project', 'Lesson', 'Lab', 'Assignment', 'Rubric', 'Worksheet', 'Practice')
    )
    topic = st.text_input("Type the specific topic: ")
    userName = st.text_input("Type your first name: ")

# initializes chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# template passes framework for the ai response
script_template = PromptTemplate(
    input_variables=['convo'],
    partial_variables={'topic': topic, 'name': userName, 'subject': option, 'type': lessonType,
                       },
    template='''
    {history}
    You are an experienced middle school {subject} teacher and coach.
    You are planning a {type} that focuses on {topic}, and fits these constraints: {convo}.
    Respond with a {type} structured in a table.
    It is important that you explain your reasoning behind each step. 
    You are preparing this for another educator, named {name}.   
    .'''
)

model = OpenAI(temperature=0, max_tokens=1000)
memoryS = ConversationSummaryMemory(llm=model, memory_key='history', return_messages=True)
chainS = LLMChain(llm=model, prompt=script_template, verbose=True, output_key='script', memory=memoryS)

with st.sidebar:
    # reset button
    if st.button("Clear Messages", type="primary"):
        # streamlit_js_eval(js_expressions="parent.window.location.reload()")
        st.session_state.messages.clear()
        memoryS.clear()

# Display chat messages from session_state history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Format chat input and print it to screen
if input_text := st.chat_input("Type Here:"):
    with st.chat_message("user"):
        st.markdown(input_text)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": input_text})

# displaying the content if the user types any input
if input_text:
    with st.chat_message("assistant"):
        # loading previous chat into Summary memory
        if st.session_state.messages:
            for i in range(len(st.session_state.messages)):
                if "content" in st.session_state.messages[i] and st.session_state.messages[i]["role"] == "user":
                    question = st.session_state.messages[i]["content"]
                if "content" in st.session_state.messages[i] and st.session_state.messages[i]["role"] == "assistant":
                    answer = st.session_state.messages[i]["content"]
                    memoryS.save_context({"input": question}, {"output": answer})
        # running and printing the chain
        script = chainS.run(input_text)
        st.markdown(script, unsafe_allow_html=True)
        # saving the chain history to the session_state
        st.session_state.messages.append({"role": "assistant", "content": script})


