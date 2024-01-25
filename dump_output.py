#!/usr/bin/env python

import pandas as pd
import sys

def process_json(file_name):
    try:
        # Reading the JSON file using Pandas
        df = pd.read_json(file_name)

        # Iterating over each row and printing the required format
        for index, row in df.iterrows():
            print(">>>> MODEL:", row["model_tag"])
            print(">>>> MODIFICATION:", row["modification_tag"])
            print(">>>> PROMPT:")
            print(row['prompt'])
            print(">>>> RESPONSE:") 
            print(row['response'])
            print(">>>> SCORING:")
            print(f"CORRECT = {row['known_answer']}; Score (GPT) = {row['score_gpt']} ({row['score_response']}); score_simple = {row['score_simple']} ({row['answer']})")
            print("======================\n\n")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py filename.json")
    else:
        file_name = sys.argv[1]
        process_json(file_name)


