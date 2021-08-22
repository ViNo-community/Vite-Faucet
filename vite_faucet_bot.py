# Import discord.py. Allows access to Discord's API.
import asyncio
import discord
import dotenv
from common import Common
from question import Question
import traceback
import sys

# Import the os,time,random module.
import os
import time
import random
import traceback
import datetime

# Import load_dotenv function from dotenv module.
from dotenv import load_dotenv
from send_vite import _send_vite

# Import commands from the discord.ext module.
from discord.ext import commands

#import send_vite

class ViteFaucetBot(commands.Bot):

    # Default values
    initialized = False
    online = True
    discord_token = ""
    client_id = ""
    rpc_url = ""
    logging_level = 0
    greylist_duration = 0.0
    answer_timeout = 20.0
    token_amount = 0
    token_id = ""
    faucet_address = ""
    faucet_private_key = ""
    max_rewards_amount = 0.0
    rpc_url = ""
    command_prefix = "!"
    permission = 0
    timeout = 5.0
    # Disabled or not
    disabled = False
    # List of questions
    questions = []
    # Data tracked per user [vite address]
    user_data = {}
    # List of greylisted accounts
    greylist = {}
   

    def __init__(self):
        # Loads the .env file that resides on the same level as the script.
        load_dotenv()
        # Grab the API token from the .env file.
        self.rpc_url = os.getenv('rpc_url')
        self.faucet_address = os.getenv('faucet_address')
        self.faucet_private_key = os.getenv('faucet_private_key')
        self.logging_level = os.getenv("logging_level")
        self.discord_token = os.getenv('discord_token')
        self.client_id = os.getenv('client_id')
        self.greylist_duration = float(os.getenv('greylist_duration') or 0.0)
        self.answer_timeout = float(os.getenv('answer_timeout') or 20.0)
        self.token_amount = float(os.getenv('token_amount'))
        self.token_id = os.getenv('token_id')
        self.max_rewards_amount = float(os.getenv('max_rewards_amount') or 0.0) 
        self.command_prefix = os.getenv('command_prefix') or "!"
        # Assert that DISCORD_TOKEN is not blank
        assert self.discord_token is not None, 'DISCORD_TOKEN must be set in .env.'
        assert not self.discord_token.isspace(), 'DISCORD_TOKEN must not be blank in .env.'
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
            await ctx.reply(f"I do not know what \"{ctx.invoked_with}\" means.")
        elif isinstance(error, ConnectionError):
            Common.logger.error(f"Connection Error: {error}", exc_info=True)
            await ctx.reply(f"Connection Error executing command \"{ctx.invoked_with}\". Please check logs")
        elif isinstance(error, commands.CheckFailure):
            Common.logger.error(f"Check Failure Error: {error} {error.args}", exc_info=True)
            await ctx.reply(f"Sorry, you do not have permission to execute \"{ctx.invoked_with}\".")      
        else:
            Common.logger.error(f"Error: {error} {error.args}", exc_info=True)
            await ctx.reply(f"Error executing command \"{ctx.invoked_with}\". Please check logs.")

    # This is called when the bot disconnects
    async def on_disconnect(self):
        print("Bot disconnected")
        # Log successful connection
        Common.log_error(f"{self.user.name} disconnected.")  

    def get_client_id(self):
        return self.client_id 

    # Helper function to send tokens to the address
    def send_vite(self,to_address,balance):

        try:
            print(f"send_vite to {to_address}")
            Common.log(f"Sending {balance} tokens to {to_address}")

            _send_vite(self.faucet_address, 
                to_address, 
                balance, 
                '', 
                self.token_id,
                self.faucet_private_key)

        except Exception as ex:
            Common.logger.error(f"Error in send_vite: {ex}", exc_info=True)
            print(traceback.format_exc(), file=sys.stderr)
            print(f"Error in send_vite {ex}")

    # Export transactions data to a CSV file
    def export_to_csv(self,filename):
        try:
            # Generate transactions file
            transactions_file = open(filename, "w")
            # Header
            transactions_file.write(f"\"Name\",\"Score\",\"Daily Balance\",\"Total Balance\"\n")
            # For each player
            for key in self.user_data:
                userinfo = self.user_data[key]
                score = userinfo.score * 100
                name = userinfo.discord_name
                daily_balance = userinfo.get_daily_balance()
                total_balance = userinfo.get_total_balance()
                # Show user name - score - daily balance - total balance
                transactions_file.write(f"{name},{score:.4}%,{daily_balance:.2f},{total_balance:.2f}\n")
            transactions_file.close()
        except Exception as ex:
            Common.logger.error(f"Error in export CSV file: {ex}", exc_info=True)
            print(traceback.format_exc(), file=sys.stderr)
            print(f"Error in export to CSV file {ex}")    

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