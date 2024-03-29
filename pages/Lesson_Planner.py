import os
import openai
import sys
import streamlit as st
import time

from langchain_openai import ChatOpenAI

from langchain.chains import LLMChain
from langchain.prompts import (PromptTemplate)
from langchain.memory import (ConversationSummaryMemory)

sys.path.append('../../..')

from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())  # read local .env file

openai.api_key = os.environ['OPENAI_API_KEY']

available_models = {"ChatGPT-3.5": "gpt-3.5-turbo", "ChatGPT-4": "gpt-4"}

# wide format and displays title
st.set_page_config(page_title="Lesson Planner", layout="wide")
st.title("Lesson Planner")

# instructions
with st.expander('Instructions'):
    st.markdown(':blue[1. choose a subject from the left column]')
    st.markdown(':red[2. in the left column, choose the lesson, assignment, project, or rubric]')
    st.markdown(':orange[3. in the left column, type in the specific topic you would like to be the focus of your lesson]')
    st.markdown(':green[4. in the chat box, specify the length of time and any other ideas or constraints for the project or lesson]')
    st.markdown(':purple[5. before a new request, use the "clear chat" button to clear the screen and AI memory.]')

# options for temp variables in template, displayed in sidebar
with st.sidebar:
    option = st.selectbox(
        'Choose a category:',
        ('English', 'Math', 'Science', 'History','Latin', 'Mandarin', 'Spanish', 'Health', 'Athletics', 'Art', 'Music')
    )
    lessonType = st.selectbox(
        'Choose a lesson category:',
        ('Project', 'Lesson', 'Lab', 'Assignment', 'Assessment', 'Rubric', 'Worksheet', 'Practice')
    )
    topic = st.text_input("Type the specific topic: ")
    gradeLevel = st.selectbox(
        'Choose an approximate target grade level:',
        ('Pre-Kindergarten', 'Kindergarten', '1st Grade', '2nd Grade', '3rd Grade', '4th Grade', '5th Grade', '6th Grade', '7th Grade',
         '8th Grade', '9th Grade')
    )

    with st.container(border=True):
        # Keep a dictionary of whether models are selected or not
        use_model = st.selectbox(':brain: Choose your model(s):',available_models.keys())
        # Assign temperature for AI
        use_model = available_models[use_model]
        aiTemp = st.slider(':sparkles: Choose AI variance or creativity:', 0.0, 1.0, 0.0, 0.1)

# initializes chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# template passes framework for the ai response
script_template = PromptTemplate(
    input_variables=['convo'],
    partial_variables={'topic': topic, 'grade': gradeLevel, 'subject': option, 'type': lessonType,
                       },
    template='''
    {history}
    You are an experienced {grade} {subject} teacher and coach.
    You are creating a {type} that focuses on {topic} in {subject} for {grade} students.
    The {type} should fit these constraints: {convo}.
    Respond with a {type} structured in a table.
    It is important that you explain your reasoning behind each step. 
    You are preparing this for another educator.   
    .'''
)

model = ChatOpenAI(temperature=aiTemp, max_tokens=500, model_name=use_model)
memoryS = ConversationSummaryMemory(llm=model, memory_key='history', return_messages=True)
chainS = LLMChain(llm=model, prompt=script_template, verbose=True, output_key='script', memory=memoryS)

with st.sidebar:
    # reset button
    if st.button("Clear Chat", type="primary"):
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
        with st.spinner("Thinking..."):
        # loading previous chat into Summary memory
            if st.session_state.messages:
                for i in range(len(st.session_state.messages)):
                    if "content" in st.session_state.messages[i] and st.session_state.messages[i]["role"] == "user":
                        question = st.session_state.messages[i]["content"]
                    if "content" in st.session_state.messages[i] and st.session_state.messages[i]["role"] == "assistant":
                        answer = st.session_state.messages[i]["content"]
                        memoryS.save_context({"input": question}, {"output": answer})
            # running and printing the chain
            script = chainS.invoke(input_text)
            st.markdown(script['script'], unsafe_allow_html=True)
        # saving the chain history to the session_state
        st.session_state.messages.append({"role": "assistant", "content": script['script']})


