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

# Import load_dotenv function from dotenv module.
from dotenv import load_dotenv

# Import commands from the discord.ext module.
from discord.ext import commands

#import send_vite

class ViteFaucetBot(commands.Bot):

    # Default values
    initialized = False
    online = True
    discord_token = ""
    logging_level = 0
    greylist_timeout = 0.0
    answer_timeout = 20.0
    token_amount = 0
    token_id = ""
    faucet_address = ""
    faucet_private_key = ""
    max_questions_amount = 0.0
    rpc_url = ""
    command_prefix = "!"
    permission = 0
    timeout = 5.0
    # Disabled or not
    disabled = False
    # List of questions
    questions = []
    # List of greylisted accounts
    limits = {}

    def __init__(self):
        # Loads the .env file that resides on the same level as the script.
        load_dotenv()
        # Grab the API token from the .env file.
        self.faucet_address = os.getenv('faucet_address')
        self.faucet_private_key = os.getenv('faucet_private_key')
        self.logging_level = os.getenv("logging_level")
        self.discord_token = os.getenv('discord_token')
        self.greylist_timeout = float(os.getenv('greylist_timeout') or 0.0)
        self.answer_timeout = float(os.getenv('answer_timeout') or 20.0)
        self.token_amount = float(os.getenv('token_amount'))
        self.token_id = os.getenv('token_id')
        self.max_questions_amount = float(os.getenv('max_questions_amount') or 0.0) 
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
        else:
            Common.logger.error(f"Error: {error}", exc_info=True)
            await ctx.reply(f"Error executing command \"{ctx.invoked_with}\". Please check logs.")

    # This is called when the bot disconnects
    async def on_disconnect(self):
        print("Bot disconnected")
        # Log successful connection
        Common.log_error(f"{self.user.name} disconnected.")   

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