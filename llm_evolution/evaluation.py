import re 
from .common import * 
from concurrent.futures import ThreadPoolExecutor


#############################

def answer_in_backticks(xd):
    """
    Extracts the answer from between triple backticks like ```
    """
    
    text = xd["response"]

    first_backtick = text.find('```')
    second_backtick = text.find('```', first_backtick + 3)

    if first_backtick != -1 and second_backtick != -1:
        return text[first_backtick + 3:second_backtick]
    else:
        return text  # or handle the case where there aren't two backticks

def answer_colon_letter(xd):
    
    text = xd["response"]

    # Try each one to see what's the last answer.
    best_answer_pos = -1
    best_answer = ""
    for m in re.finditer(f"ANSWER[^A-Za-z0-9]*(?P<answer>[A-Za-z0-9]+)([^A-Za-z]|$)", text, re.MULTILINE):
        if m.start() > best_answer_pos: 
            best_answer_pos = m.start()
            best_answer = m.group("answer")

    return best_answer.upper()


def evaluation_multiple_choice_match(xd):
    """
    Gives a score of 1 if the choices match and 0 otherwise.
    """

    known_answer = xd["known_answer"]
    answer = xd["answer"]

    # print(f"known_answer: {known_answer}, answer: {answer}, response: {xd['response']}")

    # Modify this for sure
    if known_answer is not None and answer.lower().startswith(known_answer.lower()):
        score = 1.
    else:
        score = 0.

    return score

from .models import scoring_model

def score_answer_chatgpt(input_xd): 

    from .models_chatgpt import query_chatgpt

    if input_xd["score_simple"] == 1.0:
        out_d = input_xd.copy()
        out_d["score_gpt"] = 1.0
        out_d["scoring_model"] = None
        out_d["score_response"] = None 
        out_d["scoring_model_dump"] = None 
        out_d["scoring_prompt"] = None 
        return out_d
        
    xd = input_xd.copy()

    xd["role_description"] = f"""
    {input_xd['evaluation_role_description']}
    The question is given as QUESTION: ```<question>```.
    The correct answer is given as CORRECT ANSWER: ```<answer>```.
    The student's answer given as STUDENT ANSWER: ```<answer>```. 
    Respond with CORRECT if the student's answer is correct, and WRONG if the student's answer is wrong.  
    Do not give any other explanation.
    """

    xd["prompt"] = f"""QUESTION: ```{xd["prompt"]}```
    CORRECT ANSWER: ```{xd["known_answer"]}```
    STUDENT ANSWER: ```{xd["response"]}```
    """

    result_d = query_chatgpt(scoring_model + ":scoring", ("ChatGPT", scoring_model, {"model" : {"max_tokens" : 32, "temperature" : 0.0}}), xd)

    out_d = input_xd.copy()

    out_d["score_gpt_model"] = scoring_model
    out_d["score_gpt_response"] = result_d["response"]
    out_d["score_gpt_model_dump"] = result_d
    out_d["score_gpt_prompt"] = xd["prompt"]
    out_d["score_gpt"] = 1 if result_d["response"] == "CORRECT" else 0 

    return out_d


def score_answer_simple(xd): 

    answer_extraction_name = xd.get("answer_extraction_method", None)

    if answer_extraction_name:
        answer_extraction = globals()[answer_extraction_name]
        xd["answer"] = answer_extraction(xd)
    else:
        xd["answer"] = xd["response"]

    evaluation_method_name = xd.get("evaluation_method", None)
    if evaluation_method_name:
        evaluation_method = globals()[evaluation_method_name]
        xd["score_simple"] = evaluation_method(xd) 
    
    return xd


def score_all_answers(model_tag, input_list): 

    print("Scoring results for model {model_tag}:")

    set_run_total(len(input_list))

    with ThreadPoolExecutor(32) as executor:

        local_futures = [None]*len(input_list)

        def compute_scoring(xd):
            xd = score_answer_simple(xd)
            xd = score_answer_chatgpt(xd)
            return xd
        
        ret = [None]*len(local_futures)

        for i, xd in enumerate(input_list):
            local_futures[i] = executor.submit(compute_scoring, xd)
        
        for i, f in enumerate(local_futures):
            ret[i] = f.result()
            
    return ret

        

