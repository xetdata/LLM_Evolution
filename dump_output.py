#!/usr/bin/env python

import pandas as pd
import sys
from collections import defaultdict
import argparse



def process_json(file_name, dump_models, model_filter):
    
    score_gpt = defaultdict(lambda: [0, 0])
    score_simple = defaultdict(lambda: [0, 0])

    try:
        # Reading the JSON file using Pandas
        df = pd.read_json(file_name)

        # Iterating over each row and printing the required format
        for index, row in df.iterrows():
            if model_filter is not None and model_filter not in row["model_tag"]:
                continue

            if dump_models:

                gpt_response = row.get('score_gpt_response', None)
                
                if gpt_response is None:
                    # Old version
                    print(row.keys())
                    gpt_response = row.get('score_response', "")

                print(">>>> MODEL:", row["model_tag"])
                print(">>>> MODIFICATION:", row["modification_tag"])
                print(">>>> PROMPT:")
                print(row['prompt'])
                print(">>>> RESPONSE:") 
                print(row['response'])
                print(">>>> SCORING:")
                print(f"CORRECT = {row['known_answer']}; score_simple = {row['score_simple']}; score_gpt = {row['score_gpt']} ({gpt_response}); ")
                print("======================\n\n")

            model = row["model_tag"]
            t = score_gpt[model]
            t[0] += 1
            t[1] += row["score_gpt"]

            t = score_simple[model]
            t[0] += 1
            t[1] += row["score_simple"]

    except Exception as e:
        print(f"An error occurred: {e}")


    for k in score_gpt.keys():
        score_gpt_t = score_gpt[k]
        score_simple_t = score_simple[k]
        print(f"{k}: simple_score = {score_simple_t[1] / score_simple_t[0]}, score_gpt = {score_gpt_t[1] / score_gpt_t[0]}")

if __name__ == "__main__":

    # Create the parser
    parser = argparse.ArgumentParser(description='Process a file with an optional debug mode.')

    # Add the positional argument for the file
    parser.add_argument('file', type=str, help='The JSON model dump.')

    # Add the optional argument '-d' for debug mode
    parser.add_argument('-f', '--full', action='store_true', help='Dump full responses')

    parser.add_argument('--model', type=str, help='The model to use (substring search in tag)', default= None)

    # Parse the arguments
    args = parser.parse_args()

    # Now you can use args.file and args.debug in your script
    print(f'Processing file: {args.file}')

    process_json(args.file, args.full, args.model)


