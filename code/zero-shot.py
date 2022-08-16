import os
import openai
import json
import pandas as pd
import time
import argparse
from embedding import get_embeddings, get_most_similar

parser = argparse.ArgumentParser()
# if an argument is passed in as True, we do it
parser.add_argument("--Codex")
parser.add_argument("--Explain")
parser.add_argument("--GPT3")
parser.add_argument("--GPT3_CoT")
parser.add_argument("--Do_MATH")
parser.add_argument("--Do_Courses")
parser.add_argument("--Question")
args = parser.parse_args()
print("running")
column_labels = ['Question', 'Original Question', 'Actual Solution']
if args.Codex == 'True':
    column_labels += ['Codex Input', 'Codex Output', 'Zero-Shot Evaluation']
if args.Explain == 'True' and args.Codex == 'True':
    column_labels += ['Codex Explanation Input', 'Codex Explanation']
if args.GPT3 == 'True':
    column_labels += ['GPT-3 Output', 'GPT-3 Evaluation']
if args.GPT3_CoT == 'True':
    column_labels += ['GPT-3 CoT Input', 'GPT-3 CoT Output', 'GPT-3 CoT Evaluation']
column_labels += ['Most Similar Questions']


question = args.Question
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
print(question)
def execute_zero_shot(question):
    """
    Runs zero-shot on questions_per questions for each course in courses. 
    An individual CSV file of the results is made for each course in courses.
    The embeddings for all of the questions for all of the courses in courses are located in embeddings_location.
    """
    print("executing zero-shot")
    rows = []
    original_question = question
    row = [question]
    print('Running Zero-Shot on'+' question '+'...')
    start = time.time()

    if args.Codex == 'True':
        time.sleep(codex_time_delay) #to avoid an openai.error.RateLimitError
        codex_input = docstring_front + context_array[0] + ' ' + prompt_prefix + ' ' + question + docstring_back
        codex_output = openai.Completion.create(engine = codex_engine, 
                                                prompt = codex_input, 
                                                max_tokens = zero_shot_max_tokens, 
                                                temperature = engine_temperature, 
                                                top_p = engine_topP)['choices'][0]['text']
        row += [codex_input, codex_output, '']
        print(row)
        f = open("answer.py", "w")
        f.write(row[2])
        f.close()

    if args.Explain == 'True' and args.Codex == 'True':
        time.sleep(codex_time_delay) #to avoid an openai.error.RateLimitError
        explanation_input = codex_input + codex_output + explanation_suffix
        explanation_output = openai.Completion.create(engine = codex_engine, 
                                                    prompt = explanation_input, 
                                                    max_tokens = explanation_max_tokens, 
                                                    temperature = engine_temperature, 
                                                    top_p = engine_topP)['choices'][0]['text']
        row += [explanation_input, explanation_output]
        f = open("answer.txt", "w")
        f.write(row[2] + '\n' + row[3] + '\n' + row[4] + row[5])
        f.close()
        
    if args.GPT3 == 'True':
        time.sleep(gpt3_time_delay) #to avoid an openai.error.RateLimitError
        gpt3_output = openai.Completion.create(engine = gpt3_engine, 
                                            prompt = original_question, 
                                            max_tokens = gpt3_max_tokens, 
                                            temperature = engine_temperature, 
                                            top_p = engine_topP)['choices'][0]['text']
        row += [gpt3_output, '']
        print(row[1])
        # f = open("answer.txt", "w")
        # f.write(row[1])
        # f.close()

    if args.GPT3_CoT == 'True':
        time.sleep(gpt3_time_delay) #to avoid an openai.error.RateLimitError
        gpt3_CoT_input = 'Q: ' + original_question + "\nA: " + CoT
        gpt3_CoT_output = openai.Completion.create(engine = gpt3_engine,
                                            prompt = gpt3_CoT_input,
                                            max_tokens = gpt3_CoT_max_tokens,
                                            temperature = engine_temperature,
                                            top_p = engine_topP)['choices'][0]['text']
        row += [gpt3_CoT_input, gpt3_CoT_output, '']

    end = time.time()
    print('API call time: ' + str(end-start) + '\n')
    rows.append(row)
    # info = pd.DataFrame(rows, columns=column_labels)
    # course_results_location = ' result.csv'
    # info.to_csv(course_results_location, index=False)

if __name__ == "__main__":
    execute_zero_shot(question)