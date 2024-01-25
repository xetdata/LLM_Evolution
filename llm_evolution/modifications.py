
class PromptDirectAsk:

    tag = "unmodified"
    answer_extraction_method = "just_the_answer"
    
    @staticmethod 
    def modify_prompt(text):
        return f"""
        Answer the following multiple choice question as A, B, C, or D.  {text} 
        """ 


class PromptSimpleExplanationFollowing:
    
    tag = "simple_explanation_following"
    answer_extraction_method = "answer_in_backticks"
    
    @staticmethod 
    def modify_prompt(text):
        return f"""
        {text}
        Please state your answer (E.g. The answer is X), and then follow that statement with an explanation of your reasoning.
        """


class PromptSimpleExplanationLeading:
    tag = "simple_explanation_following"
    answer_extraction_method = "answer_in_backticks"

    @staticmethod 
    def modify_prompt(text):
        return f"""
        {text}
        Please provide a step-by-step explanation of your reasoning, then state your final answer 
        using 
        enclose your final answer 
        in triple backticks (for example: ```XYZ```, where XYZ is your answer).
        """


all_modifications = [
    PromptDirectAsk,
    PromptSimpleExplanationFollowing, 
    PromptSimpleExplanationLeading]

