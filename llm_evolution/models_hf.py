import os
    
import torch
torch.set_default_device("cuda")
import gc

from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers import pipeline

from .common import *

from . import cache
from concurrent.futures import ThreadPoolExecutor
from .evaluation import score_answer_chatgpt, score_answer_simple

token = os.environ["HUGGING_FACE_TOKEN"]

def run_prompt_list_hf(model_tag, model_info, prompts):
    """
    Runs a long list of prompts on one model id. 
    """
    
    _, model_name, model_parameters = model_info

    # Log in 
    pipe = None 

    output_futures = [None] * len(prompts)

    set_run_total(len(prompts))

    with ThreadPoolExecutor(64) as executor: 

        for i, p in enumerate(prompts):

            result_cache = None ; # cache.load(key)
                
            # We use the tokenizer's chat template to format each message - see https://huggingface.co/docs/transformers/main/en/chat_templating
            messages = [
                {
                    "role": "system",
                    "content": p["role_description"] 
                },
                {"role": "user", "content": p["prompt"]},
            ]
            
            key = (run_tag, model_tag, messages)

            if result_cache is not None: 
                answer = result_cache
                report_task_completed("-")
            else:
                # Loading is expensive -- maybe everything is in cache so load here.
                if pipe is None:
                    gc.collect()
                    torch.cuda.empty_cache()

                    model = AutoModelForCausalLM.from_pretrained(model_name, **model_parameters.get("model", {}), device_map = "cuda:0")
                    tokenizer = AutoTokenizer.from_pretrained(model_name)
                    
                    pipe = pipeline("text-generation", tokenizer=tokenizer, model=model, device_map="cuda:0")

                prompt = pipe.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
                outputs = pipe(prompt, **model_parameters.get("pipeline", {})) 

                output_d = p.copy()
                output_d["response_full"] = outputs[0]
                response_text = outputs[0]["generated_text"]

                scan_text = "<|assistant|>"
                pos = response_text.find(scan_text)

                output_d["response"] = response_text[(pos + len(scan_text)):]

                cache.save(key, output_d)

                answer = output_d
                report_task_completed(".")

            answer = score_answer_simple(answer)

            # Now, do the simple scoring
            output_futures[i] = executor.submit(score_answer_chatgpt, answer) 

        output = [None] * len(prompts)
        
        for i, f in enumerate(output_futures):
            output[i] = f.result()

    return output










