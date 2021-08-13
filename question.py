import random


class Question:

    question = ""
    answers = []

    def __init__(self, question, answers):
        self.question = question
        self.answers = answers

    def answer(self, my_answer):
        return my_answer.strip() == self.answers[0]

    def get_question(self):
        return self.question

    def get_correct_answer(self):
        return self.answers[0]
    
    # Randomly scramble answers
    def get_answers(self):
        return self.answers
