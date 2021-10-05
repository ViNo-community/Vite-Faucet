from common import Common
import time

POINTS_PER_ANSWER = 50

class Player:

    # Username on Discord
    name = ""
    # Wallet address
    wallet_address = ""

    # Number of questions answered correctly
    right_answers = 0
    total_answers = 0
    score = 0
    # Number of points
    points = 0
    # Balance of the account
    balance = 0
    # Balance during this quiz period
    unsent_balance = 0
    # Total balance sent to external wallet
    sent_balance = 0
    # Rewards won during this "day" 
    # To be counted against max_rewards_amount
    daily_limit = 0

    # Timestamp of when the greylist period will clear
    greylist = 0

    def __init__(self, name):
        Common.log(f"Making new user data for {name}")
        self.name = name
        self.balance = self.unsent_balance = self.sent_balance = 0
        self.right_answers = self.total_answers = 0
        self.score = 0
        self.greylist = 0
        self.wallet_address = ""

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

    # Get username on Discord
    def get_name(self):
        return self.name
    def get_wallet_address(self):
        return self.wallet_address
    def set_wallet_address(self,address):
        self.wallet_address = address

    # Get points
    def get_points(self):
        return self.points

    # Grab user balance
    def get_balance(self):
        return self.balance
    def get_unsent_balance(self):
        return self.unsent_balance
    def get_sent_balance(self):
        return self.sent_balance
    # What to check against max_rewards_amount
    def get_daily_limit(self):
        return self.daily_limit
    # Add to balance
    def add_balance(self,amount):
        self.balance = self.balance + amount
        self.unsent_balance = self.unsent_balance + amount
        self.daily_limit = self.daily_limit + amount
    # Track amount sent to external wallet
    def add_sent_balance(self,amount):
        self.sent_balance = self.sent_balance + amount
    # Clear balance
    def clear_unsent_balance(self):
        self.unsent_balance = 0
    # A greylist period is over, so clear daily limits
    def clear_daily_limit(self):
        self.daily_limit = 0

    # Handle answering correctly
    def add_win(self):
        self.right_answers = self.right_answers + 1
        self.total_answers = self.total_answers + 1
        # Add points
        self.points = self.points + POINTS_PER_ANSWER
        # Record score
        self.score = self.get_score()
    # Add a wrong answer to the score
    def add_loss(self):
        self.total_answers = self.total_answers + 1
        # Record score
        self.score = self.get_score()

    # Get number of correct answers
    def get_right_answers(self):
        return self.right_answers
    # Get total number of questions
    def get_total_answers(self):
        return self.total_answers
    # Get score as %
    def get_score(self):
        if(self.total_answers != 0):
            return float(self.right_answers / self.total_answers) * 100.0
        else:
            return 0

    # Get greylist timer [0 = none set] when greylist limit will clear
    def get_greylist(self):
        return self.greylist
    # Get greylist info as human readable
    def get_greylist_as_string(self):
        greylist_string = ""
        if self.greylist <= 0:
            greylist_string = "Not Set"
        else:
            minutes_left = (self.greylist - time.time()) / 60.0
            if(minutes_left <= 0):
                greylist_string = "Not Set"
            else:
                greylist_string = f"{minutes_left:.4f} minutes left."
        return greylist_string
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
        return f"**Player Name:** {self.name} **Points:**: {self.points}\n" + \
            f"**Balance:** {self.balance:.2f} **Unsent Balance:** {self.unsent_balance:.2f}\n" + \
            f"**Correct Answers:** {self.right_answers}\t**Total Questions:** {self.total_answers}\t**Score:** {self.score}%\n" + \
            f"**Greylist:** {self.get_greylist_as_string()}"