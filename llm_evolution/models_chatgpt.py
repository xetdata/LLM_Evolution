from concurrent.futures import ThreadPoolExecutor
import sys
import time
import os
import random
from collections import defaultdict
from .rate_limiting import RateLimiter

# Set up the open ai input
import openai
openai_client = openai.OpenAI(api_key = os.environ['OPENAI_API_KEY'])

from .common import * 
from . import cache

import time

from threading import Lock

seen_exceptions = []

rate_limits = defaultdict(lambda: RateLimiter())

# Cache local low-level results in the disk-backed cache 
def query_chatgpt(model_tag, model_info, p):
    
    _, model_name, parameters = model_info

    messages = [{"role" : "system", 
                 "content" : p["role_description"]},
                {"role" : "user", "content" : p["prompt"]}]
    
    key = (model_tag, model_name, messages) 

    cached_result = cache.load(key)

    model_parameters = parameters.get("model", {})
    max_tokens = model_parameters.get("max_tokens", 256)

    rli = rate_limits[model_name]

    if cached_result is not None:
        output_d = cached_result 
        report_task_completed('-')
    else:
        n_tries = 0

        # Make the API call
        while True:

            current_query_spacing = rli.wait_to_go()

            try:
                sys.stderr.write('s')
                sys.stderr.flush()
                response = openai_client.chat.completions.create(model = model_name, messages = messages, **model_parameters)

                # On successful response, slowly increase the rate
                rli.register_successful(current_query_spacing)

                if response.choices[0].finish_reason != "stop" and max_tokens <= 4096:
                    sys.stderr.write('T')
                    sys.stderr.flush()

                    max_tokens *= 2
                    continue
                else:
                    sys.stderr.write('.')
                    sys.stderr.flush()

                    break
            except openai.RateLimitError as r:
                if "RPD" in str(r):
                    # Overflow of requests per day
                    sys.stderr.write(f"\n\nError: {r}\n")
                    rli.next_query_time = time.time() + n_tries * 10. * 60.

                if n_tries <= 64:
                    rli.register_rate_limited(current_query_spacing)

                    sys.stderr.write('R')
                    sys.stderr.flush()
                    # Increase the spacing and cool off a bit 
                    n_tries += 1
                    continue
                else:
                    raise
            
            except Exception as e:

                if n_tries == 0: 
                    sys.stderr.write(f"\n\nError: {e}\n")

                if n_tries <= 4:
                    n_tries += 1
                    time.sleep(5.)
                    sys.stderr.write('E')
                    sys.stderr.flush()
                    continue
                else:
                    error_str = str(e)
                    global seen_exceptions
                    if error_str not in seen_exceptions:
                        sys.stderr.write(f"\n\nUnrecoverable exception encountered: {e}\n")
                        sys.stderr.write(f"    Model = {model_tag}, Context = {p}, \n\n")
                        seen_exceptions.add(error_str)

                    raise

        output_d = {"model_dump" : response.model_dump_json(), 
                    "response" : response.choices[0].message.content}

        report_task_completed('.')

        cache.save(key, output_d)

    return output_d
    
from .evaluation import score_answer_chatgpt, score_answer_simple

def run_prompt_list_chatgpt(model_tag, model_info, input_list):
    """
    Runs a distinct collection of prompts that gets cached remotely. 
    """
    
    set_run_total(len(input_list))

    with ThreadPoolExecutor(32) as executor:

        local_futures = [None]*len(input_list)

        def compute_result(xd):
            result_d = query_chatgpt(model_tag, model_info, xd)

            output_d = xd.copy()
            output_d.update(result_d)
            
            return output_d 

        
        ret = [None]*len(local_futures)

        for i, xd in enumerate(input_list):
            local_futures[i] = executor.submit(compute_result, xd)
        
        for i, f in enumerate(local_futures):
            ret[i] = f.result()
    
    return ret


