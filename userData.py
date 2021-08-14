import random
import datetime as dt
import time

class UserData:

    vite_address = ""
    discord_name = ""

    # Number of questions asked in this current period
    question_count = 1
    # The time when the greylist period began
    greylist_start = 0

    greylist_limit = 0
    # Balance of the account
    balance = 0

    right_answers = 0
    wrong_answers = 0

    def __init__(self, discord_name, vite_address):
        print("In init function")
        self.discord_name = discord_name
        self.vite_address = vite_address
        self.balance = 0

    def get_balance(self):
        return self.balance

    def get_question_count(self):
        return self.question_count

    def next_question_count(self):
        self.question_count = self.question_count + 1
        print(f"Incrementing account to {self.question_count}")

    def start_greylist(self):
        greylist_start = time.time()

    def greylist_remaining(self):
         return 0

    def deposit(self):
        # Deposit the balance to the vite account
        print(f"Attempting to deposit {self.balance} to {self.vite_address} owned by {self.discord_name}")

'''
    def __str__(self):
        total_answers = self.right_answers + self.wrong_answers
        return f"Discord Name: {self.discord_name}\n" + \
            f"Vite Address: {self.vite_address}\n" + \
            f"Balance: {self.balance}\n" + \
            f"Right Answers: {self.right_answers} {self.right_answers / total_answers}\n" + \
            f"Wrong Answers: {self.wrong_answers} {self.wrong_answers / total_answers}\n" + \
            f"Current Question: {self.current_question}"
            '''