import random


class Question:

    question = ""
    answers = []

    def __init__(self, question, answers):
        
        self.question = question
        self.answers = answers
        print("New Question: " + self.question)
        print("New Answers: " + ','.join(self.answers))

    def answer(self, my_answer):
        return my_answer.strip() == self.answers[0]

    def get_question(self):
        return self.question

    # Randomly scramble answers
    def get_anwers(self):
        print("Getting answers")
        return random.shuffle(self.answers)
