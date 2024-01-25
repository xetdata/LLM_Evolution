#!/usr/bin/env python

import os
from datetime import datetime
import glob
import sys
import time
import itertools
import pandas as pd
import pickle
import json
import random

import llm_evolution as llme

# Runs through a small subset of things to test it all out.
prompt_limit = 5000
datasets = llme.all_datasets
models = llme.all_models # list(m for m in llme.all_models if m[0] == "HF")
modifications = llme.all_modifications

def make_prompt_list(): 

    prompt_list = []

    for d in datasets:
        prompts = d.load(quota=prompt_limit)

        if prompt_limit is not None:
            prompts = prompts[:prompt_limit]

        prompt_list += prompts

    return prompt_list

def run_all():
    """
    Runs all the results in the current configuration.
    """

    prompt_list = make_prompt_list()

    output_data = []

    for model_info in models: 
        output_data += llme.run_prompt_list(model_info, prompt_list.copy())

    sys.stderr.write('\nCompleted.\n')

    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    filename = f"output_data/output_data-{timestamp}.json"
    json.dump(output_data, open(filename, "w"))

    print(f"Output saved to {filename}")


if __name__ == '__main__':
    run_all()
                    
    













