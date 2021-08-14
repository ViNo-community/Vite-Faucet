import random


class Question:

    question = ""
    answers = []
    correct_answer = ""

    def __init__(self, question, answers):
        self.question = question
        self.answers = answers
        self.correct_answer = answers[0]

    def answer(self, my_answer):
        return my_answer.strip() == self.correct_answer

    def get_question(self):
        return self.question

    def get_correct_answer(self):
        return self.correct_answer
    
    def get_answers(self):
        return self.answers
