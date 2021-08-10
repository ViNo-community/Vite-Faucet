# Import discord.py. Allows access to Discord's API.
import discord
import dotenv
from common import Common
from question import Question

# Import the os,time,random module.
import os
import time
import random

# Import load_dotenv function from dotenv module.
from dotenv import load_dotenv

# Import commands from the discord.ext module.
from discord.ext import commands

import send_vite

class ViteFaucetBot(commands.Bot):

    # Default values
    initialized = False
    online = True
    discord_token = ""
    greylist_timeout = 0.0
    token_amount = 0
    max_questions_amount = 0.0
    rpc_url = ""
    command_prefix = "!"
    permission = 0
    timeout = 5.0
    # List of questions
    questions = []
    # List of greylisted accounts
    limits = {}

    def __init__(self):
        # Loads the .env file that resides on the same level as the script.
        load_dotenv()
        # Grab the API token from the .env file.
        self.discord_token = os.getenv('DISCORD_TOKEN')
        self.greylist_timeout = float(os.getenv('GREYLIST_TIMEOUT') or 0.0)
        self.token_amount = float(os.getenv('TOKEN_AMOUNT'))
        self.max_questions_amount = float(os.getenv('MAX_QUESTIONS_AMOUNT') or 0.0) 
        self.command_prefix = os.getenv('COMMAND_PREFIX') or "!"
        # Assert that DISCORD_TOKEN is not blank
        assert self.discord_token is not None, 'DISCORD_TOKEN must be set in .env.'
        assert not self.discord_token.isspace(), 'DISCORD_TOKEN must not be blank in .env.'
        # Load questions from questions.txt
        self.load_questions("questions.txt")
        # Init set command prefix and description
        commands.Bot.__init__(self, command_prefix=self.command_prefix,description="Vite Faucet Bot")

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
        # Show questions [for debugging - will remove before release]
        for q in self.questions:
            question = q.get_question()
            answers = q.get_anwers()
            random.shuffle(answers)
            print(question)
            i = 1
            for answer in answers:
                print(str(i) + ") " + answer)
                i = i + 1 

    def run(self):
        # Run bot
        super().run(self.discord_token)        

    @commands.command(name='set_prefix', help='Set bot prefix')
    async def set_prefix(self, ctx, *args):
        try:
            # Validate that the user entered a new prefix
            if len(args) != 1:
                await ctx.reply("Incorrect prefix. Usage: !set_prefix <new_prefix>")
                return
            # Grab the new prefix
            new_prefix = args[0]
            # Update the .env file
            dotenv.set_key(".env","command_prefix", new_prefix)
            # Update the internal bot prefix
            self.command_prefix = new_prefix
            # Update the bot status
            await self.bot.update_status()
            # Alert user of successful command prefix update
            await ctx.send(f"Set new command prefix to \"{new_prefix}\"")
        except Exception as e:
            raise Exception(f"Could not change command prefix to \"{new_prefix}\"", e)  

    @commands.command(name='question', help="!question <vite address>", brief="Displays a randomly chosen question.")
    async def question(self, ctx, *args):
        # Validate that address is correct
        if len(args) != 1:
            await ctx.reply("Incorrect vite address. Usage: !question <vite address>")
            return
        vite_address = args[0]
        if(vite_address.startswith("vite_") == False):
            await ctx.reply("Please only use vite addresses. Usage: !question <vite address>")
            return
        try:
            # Check if this address is grey-listed
            if vite_address in self.limits:
                if self.limits[vite_address] > int(time.time()):
                    await ctx.reply("You are greylisted for another " +
                        str(int((self.limits[vite_address] - time.time()) /
                            self.greylist_timeout)) + " minutes.")
                    return
            self.limits[vite_address] = time.time() + 60 * self.greylist_timeout
            # Grab a random trivia question 
            index = random.randint(0,len(self.questions))
            q = self.questions[index]
            # Print out question as multiple-choice
            question = q.get_question()
            answers = q.get_anwers()
            # Randomly shuffle answers
            random.shuffle(answers)
            response = question + "\n"
            i = 1
            for answer in answers:
                label = str(i) + ") " + answer
                response += label + "\n"
                i = i + 1
            await ctx.message.author.send(response)
            # TODO: Grab users answer, check it against correct answer
            # If correct send_vite else next questions
            # Grab users answer
            user_answer = ""
            if(user_answer == question.get_correct_answer()):
                send_vite(vite_address)
            else:
                await ctx.message.author.send("Wrong answer!")
        except Exception as e:
            raise Exception(f"Error processing question request", e)  

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
            await ctx.send(f"I do not know what \"{ctx.invoked_with}\" means.")
        elif isinstance(error, ConnectionError):
            Common.logger.error(f"Connection Error: {error}", exc_info=True)
            await ctx.send(f"Connection Error executing command \"{ctx.invoked_with}\". Please check logs")
        else:
            Common.logger.error(f"Error: {error}", exc_info=True)
            await ctx.send(f"Error executing command \"{ctx.invoked_with}\". Please check logs.")

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
        print(f"ERROR: {ex}")
        exit(0)