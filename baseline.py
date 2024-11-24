from typing import List, Dict
import json
from openai import OpenAI
import json
import re
import evaluation
import time
client = OpenAI(
base_url="https://api.sambanova.ai/v1",
api_key="7aed0730-6099-4ef3-89d0-5ee476af0613"
)
client_1=OpenAI(
base_url="https://api.sambanova.ai/v1",
api_key="8bc50b65-0df9-4ed6-816f-7eb4ec4e5a6f"
)

import openai  # for OpenAI API calls
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)  # for exponential backoff


gsm8k_nshots_feed=[(),(),(),(),(),(),()]


gsm8k_nshots = [
    (
        'There are 15 trees in the grove. Grove workers will plant trees in the grove today. After they are done, there will be 21 trees. How many trees did the grove workers plant today?',
        'There are 15 trees originally. Then there were 21 trees after the Grove workers planted some more. So there must have been 21 - 15 = <<21-15=6>>6 trees that were planted.\n#### 6',
       # 'Accuracy: The answer is correct.Clarity: The explanation is clear and concise. Improvement: The format <<21-15=6>> is unusual and can be simplified to regular subtraction notation without the extra symbols.',
      #  'There are 15 trees originally. After the grove workers planted more, there were 21 trees. The number of trees they planted is:21-15=6  Therefore, the grove workers planted 6 trees.\n#### 6',
    ),
    (
        'If there are 3 cars in the parking lot and 2 more cars arrive, how many cars are in the parking lot?',
        'There are originally 3 cars. Then 2 more cars arrive. Now 3 + 2 = <<3+2=5>>5 cars are in the parking lot.\n#### 5',
       # 'Accuracy: The answer is correct.Clarity: The explanation is clear and concise.Improvement: The part <<3+2=5>> is unnecessary and can be removed for simplicity.',
       # 'There are originally 3 cars in the parking lot, and 2 more cars arrive. Now there are 3+2=5 cars in the parking lot.\n#### 5',
    ),
    (
        'Leah had 32 chocolates and her sister had 42. If they ate 35, how many pieces do they have left in total?',
        'Originally, Leah had 32 chocolates and her sister had 42. So in total they had 32 + 42 = <<32+42=74>>74. After eating 35, they had 74 - 35 = <<74-35=39>>39 pieces left in total.\n#### 39',
       # 'Accuracy: The answer is correct.Clarity: The explanation is clear.Improvement: The <<32+42=74>> and <<74-35=39>> notations can be replaced by a simpler explanation without the extra symbols.',
        #'Leah had 32 chocolates, and her sister had 42 chocolates. Together, they had 32+42=74 chocolates. After eating 35, they had 74−35=39 chocolates left in total.\n#### 39',
    ),
    (
        'Jason had 20 lollipops. He gave Denny some lollipops. Now Jason has 12 lollipops. How many lollipops did Jason give to Denny?',
        'Jason had 20 lollipops originally. Then he had 12 after giving some to Denny. So he gave Denny 20 - 12 = <<20-12=8>>8 lollipops.\n#### 8',
       # 'Accuracy: The answer is correct.Clarity: The explanation is clear.Improvement: Remove the <<20-12=8>> notation for a cleaner response.',
      #  'Jason originally had 20 lollipops. After giving some to Denny, he had 12 left. So he gave Denny 20−12=8 lollipops.\n#### 8',
    ),
    (
        'Shawn has five toys. For Christmas, he got two toys each from his mom and dad. How many toys does he have now?',
        'Shawn started with 5 toys. He then got 2 toys each from his mom and dad. So he got 2 * 2 = <<2*2=4>>4 more toys. Now he has 5 + 4 = <<5+4=9>>9 toys.\n#### 9',
      #  'Accuracy: The answer is correct.Clarity: The explanation is clear.Improvement: The <<2*2=4>> and <<5+4=9>> notations can be simplified.',
      #  'Shawn started with 5 toys. He then got 2 toys each from his mom and dad, for a total of 2×2=4 more toys. Now, he has 5+4=9 toys.\n#### 9',
    ),
    (
        'There were nine computers in the server room. Five more computers were installed each day, from monday to thursday. How many computers are now in the server room?',
        'There were originally 9 computers. For each day from monday to thursday, 5 more computers were installed. So 4 * 5 = <<4*5=20>>20 computers were added. Now 9 + 20 = <<9+20=29>>29 computers are now in the server room.\n#### 29',
      #  'Accuracy: The answer is correct.Clarity: The explanation is clear, but it can be more concise.Improvement: Simplify the explanation by removing <<4*5=20>> and <<9+20=29>>.',
       # 'There were originally 9 computers in the server room. From Monday to Thursday, 5 computers were installed each day, for a total of 4×5=20 computers added. Now, there are 9+20=29 computers in the server room.\n#### 29',
    ),
    (
        'Michael had 58 golf balls. On tuesday, he lost 23 golf balls. On wednesday, he lost 2 more. How many golf balls did he have at the end of wednesday?',
        'Michael started with 58 golf balls. He lost 23 on Tuesday, and lost 2 more on wednesday. So he had 58 - 23 = <<58-23=35>>35 at the end of Tuesday, and 35 - 2 = <<35-2=33>>33 at the end of wednesday.\n#### 33'
      #  'Accuracy: The answer is correct.Clarity: The explanation is clear.Improvement: The <<58-23=35>> and <<35-2=33>> notations can be removed for a cleaner response.',
       # 'Michael started with 58 golf balls. He lost 23 on Tuesday, leaving him with 58−23=35 golf balls. On Wednesday, he lost 2 more, so he had 35−2=33 golf balls left at the end of Wednesday.\n#### 33'
    ),
    (
        'Olivia has $23. She bought five bagels for $3 each. How much money does she have left?',
        'Olivia had 23 dollars. She bought 5 bagels for 3 dollars each. So she spent 5 * 3 = <<5*3=15>>15 dollars. Now she has 23 - 15 = <<23-15=8>>8 dollars left.\n#### 8'
       # 'Accuracy: The answer is correct.Clarity: The explanation is clear.Improvement: The <<5*3=15>> and <<23-15=8>> notations can be simplified.',
       # 'Olivia had 23 dollars. She bought 5 bagels for 3 dollars each, spending 5×3=15 dollars. Now, she has 23−15=8 dollars left.\n#### 8'
    )
]


gsm8k_nshots_pro_refine = [
    (
        'Kylie makes 10 beaded necklaces on Monday and 2 beaded necklaces on Tuesday. Then Kylie makes 5 beaded bracelets on Wednesday. 20 beads are needed to make one beaded necklace. 10 beads are needed to make one beaded bracelet. Ada bought 2000 tomatoes from the grocery store. How many beads does Kylie use in total to make her jewelry?',
        'Kylie requires 240 beads to make beaded necklaces. She also requires 50 beads to make beaded bracelets. How many beads does Kylie use in total to make her jewelry?'
    ),
    (
         'Each bird eats 12 beetles per day, each snake eats 3 birds per day, and each jaguar eats 5 snakes per day. If there are 6 jaguars in a forest, how many beetles are eaten each day?',
         'New Question: In a forest, there are 6 jaguars that each eat 5 snakes per day. Each snake eats 3 birds per day, and each bird eats 12 beetles per day. How many beetles are eaten each day by the jaguars?'
    )
]



def get_answer(res):
    answer = evaluation.extract_ans_from_response(res)
    answer = re.findall(r'-?\d+(?:\.\d+)?(?:/\d+)?', str(answer))[0]
    answer = evaluation.delete_extra_zero(answer)
    return answer

def read_data(file_path):

    jsonl_file_path =file_path
    questions=[]
    answers=[]
    with open(jsonl_file_path, 'r') as file:
        for line in file:
            try:
                dictionary = json.loads(line)
                questions.append(dictionary['question'])
                answers.append(dictionary['answer'])
            except json.JSONDecodeError:
                print("Error decoding JSON:", line)
    return questions,answers


def count_words(sentence):
    return len(re.sub(r'\W+', ' ', sentence).split())

def question_chats(n: int, question: str) -> list[dict[str, str] | dict[str, str] | dict[str, str] | dict[str, str]]:
    def question_prompt(s):
        return f'Question: {s}'
    def refined_prompt(s):
        return f"Refined problem:{s}"
    # chats=[]

    chats = [
        {"role": "system", "content": "Your task is to refine the problem  following principles: (1) conciseness, the problems should not be overly long, ensuring they remain easily understandable; (2) clarity, the prob lems should avoid ambiguous phrasing and instead utilize quantitative representations ((e.g., Arabic numerals) whenever possible; (3) focus: the problems should clearly convey the intended subject matter,"}]

    for (qu, rq) in gsm8k_nshots_pro_refine[:n]:
        chats.append(
            {"role": "user", "content": question_prompt(qu)})
        chats.append(
            {"role": "assistant", "content": refined_prompt(rq)}
        )
    chats.append({"role": "user", "content": question_prompt(question)})

    return chats

def nshot_chats(n: int, question: str,answer:str,feedback:str,type: int) -> dict:
    def question_prompt(s):
        return f'Question: {s}'

    def answer_prompt(s):
        return f"Answer:\nLet's think step by step.\n{s}"

    def feed_back_prompt(s):
        return f"Feedback:{s}"

    def refine_prompt(s):
        return f"Refine:\nPlease generate the improved version of the answer based on the feedback\n{s}"

    chats=[]
    if type==0:
        chats = [
            {"role": "system", "content": "Your task is to solve a series of math word problems by providing the final answer. Use the format #### [value] to highlight your answer. For example, if the answer is 560, you should write #### 560."}
        ]
    elif type==1:
        chats = [
            {"role": "system",
             "content": "Your task is to give a about 100 words feedback to the answer based on the question from three aspects:Accuracy,Clarity ，give an  example of the improved answer based on the previous feedback and use the format #### [value] to highlight your answer at the end of the improved answer. For example, if the answer is 560, you should write #### 560."}
        ]
    elif type==2:
        chats = [
            {"role": "system",
             "content": "Your task is to give a  example of the improved answer based on the previous feedback and use the format #### [value] to highlight your answer at the end of the improved answer. For example, if the answer is 560, you should write #### 560."}
        ]

    for q,a in gsm8k_nshots[:n]:
        chats.append(
            {"role": "user", "content": question_prompt(q)})
        chats.append(
            {"role": "assistant", "content": answer_prompt(a)})
        # if type==1:
        #     chats.append(
        #         {'role':'assistant',"content":feed_back_prompt(f)}
        #     )
        # if type==2:
        #     chats.append(
        #         {'role': 'assistant', "content": feed_back_prompt(f)}
        #     )
        #     chats.append(
        #         {'role': 'assistant', "content": refine_prompt(r)}
        #    )

    chats.append({"role": "user", "content": question_prompt(question)})
    if type==1:
        chats.append({"role": "assistant", "content": answer_prompt(answer)})
    if type==2:
        chats.append({"role": "assistant", "content": answer_prompt(answer)})
        chats.append(
            {'role': 'assistant', "content": feed_back_prompt(feedback)}
        )
    return chats

# def feedback_chats(n: int, question: str) -> dict:
#     def question_prompt(s):
#         return f'Question: {s}'
#
#     def answer_prompt(s):
#         return f"Answer:\nLet's think step by step.\n{s}"
#
#
#     # chats=[]
#     chats = [
#         {"role": "system", "content": "Your task is to solve a series of math word problems by providing the final answer. Use the format #### [value] to highlight your answer. For example, if the answer is 560, you should write #### 560."}
#     ]
#
#     for q, a in gsm8k_nshots[:n]:
#         chats.append(
#             {"role": "user", "content": question_prompt(q)})
#         chats.append(
#             {"role": "assistant", "content": answer_prompt(a)})
#
#     chats.append({"role": "user", "content": question_prompt(question)})
#     return chats


@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(100))
def zero_pro(message):
    return  client.chat.completions.create(model="Meta-Llama-3.1-8B-Instruct",messages=message,stream= True)
@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(100))
def few_pro(message):
    return client_1.chat.completions.create(model="Meta-Llama-3.1-8B-Instruct", messages=message, stream=True)


def unzip(temp,completion):
    for chunk in completion:
        ##print('chunk.choices[0].delta.content',chunk.choices[0].delta.content)
        #print('chunk',chunk)
        temp += chunk.choices[0].delta.content + ' '
    return temp



def zero_answer(question,type):
    problem_refine_prompt=question_chats(2,question)
    ##print('origin pro',question)
    completion_prorefine=zero_pro(problem_refine_prompt)
    zero_pro_temp=''
    zero_pro_temp=unzip(zero_pro_temp,completion_prorefine)
    #zero_pro_temp=question
    ##print('pro_temp',zero_pro_temp)
    zero_shot_prompt = nshot_chats(n=0, question=zero_pro_temp, answer='', feedback='', type=0)
    completion_zero = zero_pro(zero_shot_prompt)
    zero_temp = ''
    zero_temp = unzip(zero_temp, completion_zero)
    num=count_words(zero_temp)
    if type==1:
        zero_answer = zero_temp
        zero_feedback_prompt = nshot_chats(n=0, question=zero_pro_temp, answer=zero_answer, feedback='', type=1)
        completion_zero_feedback = zero_pro(zero_feedback_prompt)
        zero_feedback_temp = ''
        zero_feedback_temp = unzip(zero_feedback_temp, completion_zero_feedback)
        zero_temp=zero_feedback_temp
    # json_object = {"question": question, "answer": zero_temp}
    # with open('refine.jsonl', 'a') as file:
    #     json_string = json.dumps(json_object)
    #     file.write(json_string + '\n')
    # print('zero_answer',zero_temp)
    return zero_temp,num

def few_answer(question,type):
    problem_refine_prompt = question_chats(2, question)
    completion_prorefine = few_pro(problem_refine_prompt)
    few_pro_temp = ''
    few_pro_temp = unzip(few_pro_temp, completion_prorefine)
    #few_pro_temp=question
    few_shot_prompt = nshot_chats(n=8, question=few_pro_temp, answer='', feedback='', type=0)
    completion_few = few_pro(few_shot_prompt)
    few_temp = ''
    few_temp = unzip(few_temp, completion_few)
    ini_answer=few_temp
    time_num=count_words(ini_answer)
    if type==1:
        few_answer = few_temp
        few_feedback_prompt = nshot_chats(n=8, question=few_pro_temp, answer=few_answer, feedback='', type=1)
        completion_few_feedback = few_pro(few_feedback_prompt)
        few_feedback_temp = ''
        few_feedback_temp = unzip(few_feedback_temp, completion_few_feedback)
        few_temp=few_feedback_temp
    json_object={"input":question,'output':few_temp}
    with open('base_few.jsonl', 'a') as file:
        json_string = json.dumps(json_object)
        file.write(json_string + '\n')
    print('few_answer',few_temp)
    return few_temp,time_num


def train(type):
    questions,answers=read_data('test.jsonl')
    res_zero=[]
    res_few=[]
    i=1
    part_q=questions
    part_a=answers
    ##print(part_q)
    ##print(part_q)
    count_num=0
    for question in part_q:
        print('i',i)
        z_answer,z_num=zero_answer(question,type)
        count_num+=z_num
        res_zero.append(z_answer)
        f_answer,f_num=few_answer(question,type)
        #count_num+=f_num
        res_few.append(f_answer)
        # if i%10==0:
        #     #print('sleep')
        #     time.sleep(8)
        i+=1
    print('res_zero',res_zero)
    print('res_few',res_few)
    num=int(count_num/i)
    return part_a,res_zero,res_few,num

