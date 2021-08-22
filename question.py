# Holds question and answer data
class Question:

    question = ""
    answers = []
    correct_answer = ""

    def __init__(self, question, answers):
        self.question = question
        self.answers = answers
        self.correct_answer = answers[0]

    # Get the question asked
    def get_question(self):
        return self.question

    # Get the correct answer
    def get_correct_answer(self):
        return self.correct_answer
    
    # Get the array of answers
    def get_answers(self):
        return self.answers