from common import Common
import random
import datetime as dt
import time

POINTS_PER_ANSWER = 50

class Player:

    # Username on Discord
    name = ""

    # Number of questions answered correctly
    right_answers = 0
    total_answers = 0
    # Number of points
    points = 0
    # Balance of the account
    balance = 0
    # Rewards won during this "day" 
    # To be counted against max_rewards_amount
    daily_total = 0

    # Timestamp of when the greylist period will clear
    greylist = 0

    def __init__(self, name):
        Common.log(f"Making new user data for {name}")
        self.name = name
        self.balance = 0
        self.right_answers = self.total_answers = 0
        self.score = 0
        self.greylist = 0

    # Load from data
    def load(self, name, balance, right_answers, total_answers, score, greylist):
        Common.log(f"Loading data for {self.name} with balance: {balance} right answers: {right_answers}" + 
            f"total answers: {total_answers} score: {score} greylist: {greylist}")
        self.name = name
        self.balance = balance
        self.right_answers = right_answers
        self.total_answers = total_answers
        self.score = score
        self.greylist = greylist

    # Grab user balance
    def get_balance(self):
        return self.balance
    # GOD DAMN STUPID PIECE OF SHIT LANGUAGE!!
    def get_daily_balance(self):
        return self.balance
    # Add to balance
    def add_balance(self,amount):
        self.balance = self.balance + amount
        self.daily_total = self.daily_total + amount
    # Clear balance
    def clear_balance(self):
        self.balance = 0

    # Handle answering correctly
    def add_win(self):
        self.right_answers = self.right_answers + 1
        self.total_answers = self.total_answers + 1
        # Add points
        self.points = self.points + POINTS_PER_ANSWER
    # Add a wrong answer to the score
    def add_loss(self):
        self.total_answers = self.total_answers + 1

    # Get number of correct answers
    def get_right_answers(self):
        return self.right_answers
    # Get total number of questions
    def get_total_answers(self):
        return self.total_answers
    # Get score as %
    def get_score(self):
        return float(self.right_answers / self.total_answers) * 100.0

    # Get greylist timer [0 = none set] when greylist limit will clear
    def get_greylist(self):
        return self.greylist
    # Set greylist to minutes minutes in the future
    def set_greylist(self,minutes):
        self.greylist = time.time() + 60 * minutes
        Common.log(f"{self.name} is greylisted until {self.greylist}")
    # Clear the greylist timeout
    def clear_greylist(self):
        self.greylist = 0
        Common.log(f"{self.name} has greylist cleared")

    # To string. Used for debugging purposes
    def __str__(self):
        greylist_string = ""
        print(f"Grey list is {self.greylist}")
        if self.greylist <= 0:
            greylist_string = "Not Set"
        else:
            minutes_left = (self.greylist - time.time()) / 60.0
            greylist_string = f"{minutes_left:.4f} minutes left."

        return f"**Player Name:** {self.name} **Points:**: {self.points}\n" + \
            f"**Balance:** {self.balance:.2f}\n" + \
            f"**Correct Answers:** {self.right_answers}\t**Total Questions:** {self.total_answers}\t**Score:** {self.score}%\n" + \
            f"**Greylist:** {greylist_string}"