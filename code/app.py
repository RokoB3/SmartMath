from logging import raiseExceptions
import streamlit as st
import os
import openai
import json
import pandas as pd
import time

st.write("""
# I'M CALLY, SMART MATH V1
The calculator with a brain
***
""")

st.sidebar.header('Parameters')
model = st.sidebar.selectbox('Model', ['GPT3', 'Codex'])
explain = st.sidebar.checkbox('Explain', )

st.sidebar.write("""
***
### Information \n
*Models:*\n
* GPT3: Text based AI model. Great for solving simple numerical problems.
* Codex: Code based AI model. Great for graphing and complex questions.

""")

question = st.text_area("Ask me a math question")

col1, col2, col3 = st.columns([4,3,1])

with col3:
    start = st.button("Start")

    
openai.api_key = os.getenv("OPENAI_API_KEY") 


codex_engine = "code-davinci-002"
gpt3_engine = "text-davinci-002"
engine_temperature = 0
engine_topP = 0
zero_shot_max_tokens = 500 
explanation_max_tokens = 150
gpt3_max_tokens = 200
gpt3_CoT_max_tokens = 1000
codex_time_delay = 3
gpt3_time_delay = 1


# for prompt formatting:
docstring_front = '''"""\n''' 
docstring_back = '''\n"""\n'''
context_array = ['write a program', 'using sympy', 'using simulations']
prompt_prefix = 'that answers the following question:'
explanation_suffix = "\n\n'''\nHere's what the above code is doing:\n1."
CoT = "Let's think step by step."


def clean_answer(answer):
    lines = answer.splitlines()
    for line in lines:
        if line =='':
            lines.remove(line)
        else:
            answer = ''.join(lines)
            return answer

def format_codex_answer(answer):
    first = ["def main():"]
    lines = answer.splitlines()
    for i in range(len(lines)):
        lines[i] = f'   {lines[i]}'   # Add a tab to every line
    lines = first + lines
    answer = '\n'.join(lines)
    return answer


def execute_zero_shot(question):
    """
    Runs zero-shot on questions_per questions for each course in courses. 
    An individual CSV file of the results is made for each course in courses.
    The embeddings for all of the questions for all of the courses in courses are located in embeddings_location.
    """
    print("executing zero-shot")
    rows = []
    original_question = question
    print('Running Zero-Shot on'+' question '+'...')
    start = time.time()

    if model == 'Codex':
        time.sleep(codex_time_delay) #to avoid an openai.error.RateLimitError
        codex_input = docstring_front + context_array[0] + ' ' + prompt_prefix + ' ' + question + docstring_back
        codex_output = openai.Completion.create(engine = codex_engine, 
                                                prompt = codex_input, 
                                                max_tokens = zero_shot_max_tokens, 
                                                temperature = engine_temperature, 
                                                top_p = engine_topP)['choices'][0]['text']
        
        with open("answer.py", 'w') as f:
            print("Writing")
            f.write(format_codex_answer(codex_output))
        try:
            from answer import main
            main()
        except:
            st.text_area("OUTPUT", "Please run code in a python environment.")
        else:
            script = exec(open("answer.py").read())
            print(script)
            st.text_area("OUTPUT", script)
        
        st.text_area("Code", codex_output)
        st.write("""
        ##### Please run code in a python environment
        """)


    if explain == True and model == 'Codex':
        time.sleep(codex_time_delay) #to avoid an openai.error.RateLimitError
        explanation_input = codex_input + codex_output + explanation_suffix
        explanation_output = openai.Completion.create(engine = codex_engine, 
                                                    prompt = explanation_input, 
                                                    max_tokens = explanation_max_tokens, 
                                                    temperature = engine_temperature, 
                                                    top_p = engine_topP)['choices'][0]['text']
        explanation_output = clean_answer(explanation_output)
        st.text_area("Explanation", explanation_output)


        
    if model == 'GPT3':
        time.sleep(gpt3_time_delay) #to avoid an openai.error.RateLimitError
        gpt3_output = openai.Completion.create(engine = gpt3_engine, 
                                            prompt = original_question, 
                                            max_tokens = gpt3_max_tokens, 
                                            temperature = engine_temperature, 
                                            top_p = engine_topP)['choices'][0]['text']
        gpt3_output = clean_answer(gpt3_output)
        st.text_area("OUTPUT", gpt3_output)


    if explain == True and model == 'GPT3':
        time.sleep(gpt3_time_delay) #to avoid an openai.error.RateLimitError
        gpt3_CoT_input = 'Q: ' + original_question + "\nA: " + CoT
        gpt3_CoT_output = openai.Completion.create(engine = gpt3_engine,
                                            prompt = gpt3_CoT_input,
                                            max_tokens = gpt3_CoT_max_tokens,
                                            temperature = engine_temperature,
                                            top_p = engine_topP)['choices'][0]['text']
        gpt3_CoT_output = clean_answer(gpt3_CoT_output)
        st.text_area("Explanation", gpt3_CoT_output)

    end = time.time()
    print('API call time: ' + str(end-start) + '\n')

    # info = pd.DataFrame(rows, columns=column_labels)
    # course_results_location = ' result.csv'
    # info.to_csv(course_results_location, index=False)

if __name__ == "__main__":
    if question != '' and start == True:
        execute_zero_shot(question)