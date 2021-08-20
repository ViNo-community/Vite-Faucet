from common import Common
import random
import datetime as dt
import time

class UserData:

    # Username on Discord
    discord_name = ""

    # Score board
    right_answers = 0
    total_answers = 0
    score = 0

    # Timestamp of when the greylist period will clear
    greylist = 0

    # Balance of the account
    daily_balance = 0
    total_balance = 0

    # Max rewards allowed per time period
    max_daily_rewards = 0

    def __init__(self, discord_name, max_rewards):
        self.discord_name = discord_name
        self.max_daily_rewards = max_rewards
        self.daily_balance = 0
        self.right_answers = self.wrong_answers = 0
        self.greylist = 0
        Common.log(f"Making user data for {self.discord_name}")

    # Grab user balance
    def get_total_balance(self):
        return self.total_balance

    # Grab user daily balance ("daily" = within a greylist period)
    def get_daily_balance(self):
        return self.daily_balance
    # Set user daily balance
    def add_daily_balance(self,amount):
        self.daily_balance = self.daily_balance + amount
        self.total_balance = self.total_balance + amount
    # Clear daily balance
    def clear_daily_balance(self):
        self.daily_balance = 0

    # Add a correct answer to the score
    def add_win(self):
        self.right_answers = self.right_answers + 1
        self.total_answers = self.total_answers + 1
        self.score = self.right_answers / self.total_answers
    # Add a wrong answer to the score
    def add_loss(self):
        self.total_answers = self.total_answers + 1
        self.score = self.right_answers / self.total_answers

    def get_right_answers(self):
        return self.right_answers
    def get_total_answers(self):
        return self.total_answers

    # Get greylist timer [0 = none set] when greylist limit will clear
    def get_greylist(self):
        return self.greylist

    # Set greylist to minutes minutes in the future
    def set_greylist(self,minutes):
        self.greylist = time.time() + 60 * minutes
        Common.log(f"{self.discord_name} has greylist set to {self.greylist}")

    # Clear the greylist timeout
    def clear_greylist(self):
        self.greylist = 0
        Common.log(f"{self.discord_name} has greylist cleared")

    def __str__(self):
        greylist_string = ""
        print(f"Grey list is {self.greylist}")
        if self.greylist == 0:
            greylist_string = "Not Set"
        else:
            minutes_left = (self.greylist - time.time()) / 60.0
            greylist_string = f"{minutes_left:.4f} minutes left."

        return f"**Discord Name:** {self.discord_name}\n" + \
            f"**Daily Balance:** {self.daily_balance:.2f}\t**Max Daily:** {self.max_daily_rewards}\n" + \
            f"**Total Balance:** {self.total_balance:.2f}\n" + \
            f"**Correct Answers:** {self.right_answers} / {self.total_answers}\t**Score:** {self.score * 100:.2f}%\n" + \
            f"**Greylist:** {greylist_string}"