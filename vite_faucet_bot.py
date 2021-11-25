# Import discord.py. Allows access to Discord's API.
import discord
from common import Common
from question import Question
import traceback
import sys

# Import the os,time,random module.
import os
import random
import traceback
import datetime
from pathlib import Path

# Import load_dotenv function from dotenv module.
from dotenv import load_dotenv
from vite_functions import send_transaction

# Import commands from the discord.ext module.
from discord.ext import commands

class ViteFaucetBot(commands.Bot):

    # Default values
    initialized = False
    online = True
    discord_token = ""
    rpc_url = ""
    logging_level = 0
    greylist_duration = 0.0
    answer_timeout = 20.0
    token_amount = 0
    token_id = ""
    faucet_address = ""
    max_rewards_amount = 0.0
    rpc_url = ""
    command_prefix = "!"
    permission = 0
    timeout = 5.0
    # statistics
    total_distributed = 0.0
    # Disabled or not
    disabled = False
    # List of questions
    questions = []
    # Data tracked per user [vite address]
    player_data = {}
    # List of greylisted accounts
    greylist = {}
    # Transactions file
    transdir = Path(__file__).parent / "transactions"
    transactions_filename = ""
    transactions_file = ""

    def __init__(self):
        # Loads the .env file that resides on the same level as the script.
        load_dotenv()
        # Grab the API token from the .env file.
        self.rpc_url = os.getenv('rpc_url')
        self.faucet_address = os.getenv('faucet_address')
        self.logging_level = os.getenv("logging_level")
        self.discord_token = os.getenv('discord_token')
        self.greylist_duration = float(os.getenv('greylist_duration') or 0.0)
        self.answer_timeout = float(os.getenv('answer_timeout') or 20.0)
        self.token_amount = float(os.getenv('token_amount'))
        self.token_id = os.getenv('token_id')
        self.max_rewards_amount = float(os.getenv('max_rewards_amount') or 0.0) 
        self.low_balance_alert = float(os.getenv('low_balance_alert') or 0.0) 
        self.command_prefix = os.getenv('command_prefix') or "!"
        # Assert that DISCORD_TOKEN is not blank
        assert self.discord_token is not None, 'DISCORD_TOKEN must be set in .env.'
        assert not self.discord_token.isspace(), 'DISCORD_TOKEN must not be blank in .env.'
        # Make transaction directory if it doesn't already exist
        if not os.path.exists(self.transdir):
            Common.log(f"Transactions directory does not exist. Creating new directory: {self.transdir}")
            try:
                os.makedirs(self.transdir)
            except Exception as e:
                print(f"Error creating {self.transdir} :", e)
                Common.logger.error(f"Error creating transactions directory: {e}", exc_info=True)   
                return
        # Open or create todays transactions CSV file - YYYYMMDD_transactions.csv
        filename = datetime.datetime.now().strftime("%Y%m%d") + "_transactions.csv"
        self.transactions_filename = self.transdir / filename
        # Create file if it does not exist
        if not os.path.exists(self.transactions_filename):
            Common.log(f"Transactions file does not exist. Creating new file: {self.transactions_filename}")
            # Open transactions file
            self.transactions_file = open(self.transactions_filename, "w")
            # Write header
            self.transactions_file.write(f"\"Time\",\"Name\",\"Vite Address\",\"Amount\",\n")
        else:
            Common.log(f"Transactions file does exist. Opening file in append mode: {self.transactions_filename}")
            # File exists. Open in append mode
            self.transactions_file = open(self.transactions_filename, "a")
        # Load questions from questions.txt
        self.load_questions("questions.txt")
        # Init set command prefix and description
        commands.Bot.__init__(self, command_prefix=self.command_prefix,description="Vite Faucet Bot")
        # Automatically load cogs
        for file in os.listdir('./cogs'):
            if file.endswith(".py"):
                try:
                    self.load_extension(f"cogs.{file[:-3]}")
                    Common.log(f"Loaded Cog: {file}")
                    print(f"Loaded: {file}")
                except Exception as e:
                    Common.log_error(f"Could not load Cog: {file}: {e}")
                    print(f"Could not load: {file}:", e)

    def load_questions(self, questions_file):    
        # Load questions from questions_file file
        # Format for each question is:
        # <Question Text>
        # <Answer #1 - Always Correct Answer>
        # <Answer #2>
        # <Answer #3>
        # <Answer #4>
        # \n
        f = open(questions_file, "r")
        # Read file until EOF
        while True:
            # Read in question text
            question = f.readline().strip()
            # Read in answers
            answers = [f.readline().strip(),
                    f.readline().strip(),
                    f.readline().strip(),
                    f.readline().strip()]
            if(not f.readline()): 
                break
            # Append new Question object to questions
            self.questions.append(Question(question,answers))
        # Randomly shuffle questions
        random.shuffle(self.questions)
        # Show questions for debugging
        '''
        for q in self.questions:
            question = q.get_question()
            answers = q.get_answers()
            print(question)
            i = 1
            for answer in answers:
                print(str(i) + ") " + answer)
                i = i + 1 
            print("Correct answer: " + q.get_correct_answer())
        '''

    def run(self):
        # Run bot
        super().run(self.discord_token)        

    # This is called when the bot has logged on and set everything up
    async def on_ready(self):
        # Set bot as initialized
        self.initialized = True
        # Log successful connection
        Common.log(f"{self.user.name} connected")
        print(f"{self.user.name} connected")
        # Update bot status
        await self.update_status()

    async def update_status(self):
        status = f" say {self.command_prefix}help"
        # Update bot status
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name=status))
       
    # Bot encounters an error during command execution
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            Common.logger.error(f"{ctx.message.author} tried unknown command \"{ctx.invoked_with}\" Error: {error}", exc_info=True)
            command = ctx.invoked_with.replace('@','@\u200b')
            await ctx.reply(f"I do not know what \"{command}\" means.")
        elif isinstance(error, ConnectionError):
            Common.logger.error(f"Connection Error: {error}", exc_info=True)
            await ctx.reply(f"Connection Error executing command \"{ctx.invoked_with}\". Please try again. Check logs for error details")
        elif isinstance(error, commands.CheckFailure):
            Common.logger.error(f"Check Failure Error: {error} ", exc_info=True)
            await ctx.reply(f"Sorry, you do not have permission to execute \"{ctx.invoked_with}\".")      
        else:
            Common.logger.error(f"Error: {error} ", exc_info=True)
            await ctx.reply(f"Error executing command \"{ctx.invoked_with}\". Please check logs.")

    # This is called when the bot disconnects
    async def on_disconnect(self):
        print("Bot disconnected")
        # Log successful connection
        Common.log_error(f"{self.user.name} disconnected.")  

    # Helper function to send tokens to the address
    async def send_vite(self,account_name,vite_address,amount):

        try:
            Common.log(f"Sending {amount} to {account_name} wallet: {vite_address}")
            # Send vite from faucet to wallet address
            res = await send_transaction(self.faucet_address, vite_address, amount)
            if res.returncode == 1:
                return res
            else:
                hash = res.stdout
                Common.log(f"Transaction Hash: {hash}")
                # Check date if we need to move to a transaction file
                new_filename = datetime.datetime.now().strftime("%Y%m%d") + "_transactions.csv"
                full_new_filename = self.transdir / new_filename
                if(full_new_filename != self.transactions_filename):
                    Common.log(f"Closing old transactions file {self.transactions_filename}")
                    # Close old file
                    self.transactions_file.close()
                    # Open new file
                    self.transactions_filename = full_new_filename
                    self.transactions_file = open(self.transactions_filename, "w")
                    # Write header as first line
                    self.transactions_file.write(f"\"Time\",\"Name\",\"Vite Address\",\"Amount\",\n")
                    Common.log(f"Opening new transaction file {self.transactions_filename}")
                # Record transaction in spreadsheet
                current_time = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
                self.transactions_file.write(f"\"{current_time}\",\"{account_name}\",\"{vite_address}\",{amount:.2f}\n")
                self.transactions_file.flush() 
                # Return transaction hash
                return res
        except Exception as ex:
            Common.logger.error(f"Error in send_vite: {ex}", exc_info=True)
            print(traceback.format_exc(), file=sys.stderr)
            print(f"Error in send_vite {ex}")
            raise ex

if __name__=='__main__':
    # Initiate Discord bot
    try:
        bot = ViteFaucetBot()
        print("Vite Faucet Bot is now running with prefix " + bot.command_prefix)
        # Run the bot loop
        bot.run()
    except Exception as ex:
        Common.logger.error(f"Error starting program: {ex}", exc_info=True)
        print(traceback.format_exc(), file=sys.stderr)
        print(f"Error starting program: {ex}")
        exit(0)