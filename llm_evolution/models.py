import torch

all_models = [("ChatGPT", "gpt-3.5-turbo-1106", {"temperature": 0.0}), 
              ("ChatGPT", "gpt-3.5-turbo-0613", {"temperature": 0.0}), 
              ("ChatGPT", "gpt-3.5-turbo-0301", {"temperature": 0.0}), 
              ("ChatGPT", "gpt-4-0613", {}), 
              #("ChatGPT", "gpt-4-0314", {}),
              # "gpt-4-1106-preview" 

              ("HF", "TinyLlama/TinyLlama-1.1B-Chat-v1.0", 
               {"model" : {"torch_dtype" : torch.bfloat16}, "pipeline" : {"do_sample" : False, "top_k"  : 50}}),
              ("HF", "meta-llama/Llama-2-7b-chat-hf", 
              {"model" : {"load_in_8bit" : True}, "pipeline" : {"do_sample" : False, "top_k"  : 50}}),
              #("HF", "meta-llama/Llama-2-13b-chat-hf", 
              # {"model" : {"load_in_8bit" : True}, "pipeline" : {"do_sample" : False, "top_k"  : 50}}),
              # ("HF", "meta-llama/Llama-2-13b-chat-hf", {"load_in_8bit" : True}),
              # ("HF", "mistralai/Mistral-7B-v0.1",  {"load_in_4bit" : True})
              ]
    
scoring_model = "gpt-3.5-turbo-0613"

import xetcache
import sys
from .common import run_tag

def run_prompt_list(model_info, prompts):
    model_type, model_name, model_parameters = model_info

    def get_name(kd): 
        return ','.join(f"{kv[0]}=|{get_name(kv[1])}|" if isinstance(kv[1], dict) else f"{kv[0]}={kv[1]}" for kv in sorted(kd.items()))

    model_param_info = get_name(model_parameters) 
    model_tag = f"{model_type}:{model_name}|{model_param_info}"
    
    print(f"Running {len(prompts)} prompts with model {model_tag}")

    if model_type == "ChatGPT":
        from .models_chatgpt import run_prompt_list_chatgpt
        outputs = run_prompt_list_chatgpt(model_tag, model_info, prompts)
    elif model_type == "HF":
        from .models_hf import run_prompt_list_hf
        outputs = run_prompt_list_hf(model_tag, model_info, prompts)
    else:
        assert False, f"Unrecognized model type {model_tag}"

    print("Done.")

    for d in outputs:
        d["model_type"] = model_type
        d["model"] = model_name
        d["model_tag"] = model_tag
        d["run_tag"] = run_tag

    # Now, also, score everything using chatgpt
    score_gpt = sum(d["score_gpt"] for d in outputs) / len(outputs)
    score_simple = sum(d["score_simple"] for d in outputs) / len(outputs)
    print(f"Average score for {model_tag}: SIMPLE: {score_simple}")
    print(f"Average score for {model_tag}: GPT Scored: {score_gpt}")


    return outputs



