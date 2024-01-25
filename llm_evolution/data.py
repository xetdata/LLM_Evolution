import glob
import pandas as pd
import os


class MMLU: 

    def load(self, quota = None):
        """
        Load the data.  Will return a list of lists.
        """

        output = []
        n = 0
        path = "data/mmlu/test/*.csv"

        for filename in glob.glob(path):
            subject = os.path.split(filename)[-1].rstrip(".csv")
            data = pd.read_csv(filename)
            for modification_method in ["none", "explanation_following", "explanation_preceeding"]: 
                output += list(self.formulate_prompt(row, subject, modification_method) for row in data.values)
            n += len(output[-1])

            if quota is not None:
                if n >= quota:
                    break
     
        return output

    def formulate_prompt(self, input_row, subject, modification_method):
     
        question = input_row[0]
        a, b, c, d = input_row[1], input_row[2], input_row[3], input_row[4]
        answer = input_row[5]

        prompt = f"""
        {question}
        A: {a}
        B: {b}
        C: {c}
        D: {d}
        """

        if modification_method == "none":
            role_description = f'You are an expert in {subject} whose job is to answer questions from the user.  Write the answer in the following format where X is exactly one of A,B,C,D: "ANSWER: X". If you are uncertain of the correct answer, guess the most likely one.'
        elif modification_method == "explanation_following":
            role_description = f'You are an expert in {subject} whose job is to answer questions from the user.  First, write the answer in the following format where X is exactly one of A,B,C,D: "ANSWER: X". If you are uncertain of the correct answer, guess the most likely one.  Then, explain your reasoning.'
        elif modification_method == "explanation_preceeding":
            role_description = f'You are an expert in {subject} whose job is to answer questions from the user.  First, reason about the problem and provide an explanation of the needed logic. Then write the answer in the following format where X is exactly one of A,B,C,D: "ANSWER: X". If you are uncertain of the correct answer, guess the most likely one.'
        else:
            assert False

        evaluation_role_description = f"You are an expert in {subject} whose job is to determine whether a student's response to a multiple choice question is correct."

        return {
            "role_description" : role_description, 
            "evaluation_role_description" : evaluation_role_description,
            "subject" : subject,
            "modification_tag" : modification_method, 
            # Copied from openai/evals/evals/elsuite/mmmu/eval.py".
 
            "prompt" : prompt, 
            "known_answer" : answer, 
            "source_data" : list(input_row), 
            "evaluation_method" : "evaluation_multiple_choice_match",
            "answer_extraction_method" : "answer_colon_letter",
            "source_tag" : self.__class__.__name__}

all_datasets = [MMLU()]
