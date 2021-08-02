import random


class Question:

    question = ""
    answers = []

    def __init__(self, question, answers):
        self.question = question
        self.answers = answers
        # First answer is always the correct one
        self.correct = answers[0]

    def answer(self, my_answer):
        return my_answer.strip() == self.answers[0]


    def get_question(self):
        return self.question

    # Randomly scramble answers
    def get_anwers(self):
        return random.shuffle(self.answers)
