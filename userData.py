import random
import datetime as dt
import time

class UserData:

    discord_name = ""

    # Total amount of rewards 
    total_rewards = 0
    # The time when the greylist period began
    greylist_start = 0

    greylist_limit = 0
    # Balance of the account
    balance = 0

    right_answers = 0
    wrong_answers = 0

    def __init__(self, discord_name):
        print("In init function")
        self.discord_name = discord_name
        self.balance = 0

    def get_balance(self):
        return self.balance

    def set_balance(self,new_balance):
        self.balance = new_balance

    # Rewards earned in a 24H period
    def get_total_rewards(self):
        return self.total_rewards

    def add_total_rewards(self, amount):
        self.total_rewards = self.total_rewards + amount

    # Clear rewards amount for 24H period
    def clear_total_rewards(self):
        self.total_rewards = 0

    def add_win_to_score(self):
        self.right_answers = self.right_answers + 1

    def get_right_answers(self):
        return self.right_answers

    def get_wrong_answers(self):
        return self.wrong_answers

    def add_loss_to_score(self):
        self.wrong_answers = self.wrong_answers + 1

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