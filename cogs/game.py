import asyncio

import discord
from userData import UserData
from discord.ext import commands
import dotenv
from common import Common

# Import the os,time,random module.
import os
import time
import random

class GameCog(commands.Cog, name="Game"):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='score', help="Show your current score and account balance.")
    async def score(self, ctx):
        try:
            # Check if we have an entry yet
            if ctx.message.author in self.bot.user_data:
                # Grab the entry
                my_user_data = self.bot.user_data[ctx.message.author]
                # Show user data information
                response = str(my_user_data)
                await ctx.reply(response)
            else:
                response = f"No score information yet for {ctx.message.author}"
                await ctx.reply(response)
        except Exception as e:
            Common.logger.error(f"Error showing scoreboard: {e}", exc_info=True)   
            raise Exception("Exception showing score", e)       

    @commands.command(name='withdraw', help="Withdraw your balance to an external vite wallet.")
    async def deposit(self, ctx, vite_address=""):
        if(self.bot.disabled):
            await ctx.reply("The trivia bot is currently disabled.")
            return
         # Check that vite_address is not blank
        if(vite_address == ""):
            await ctx.reply(f"Usage: {self.bot.command_prefix}start <new_prefix>")
            return    
        # Make sure that address is for vite
        if(vite_address.startswith("vite") == False):
            await ctx.reply(f"Please only use vite addresses. Usage: {self.bot.command_prefix}start <vite address>")
            return
        try:
            # Check if we have an entry yet
            if ctx.message.author in self.bot.user_data:
                # Grab the entry
                my_user_data = self.bot.user_data[ctx.message.author]
                balance = my_user_data.get_balance()
            else:
                response = f"No score information yet for {ctx.message.author}"
                await ctx.reply(response)
                return
            # Deposit the balance to the vite address
            self.bot.send_vite(vite_address,balance)
            # Subtract from balance
            my_user_data.set_balance(0)
            # Alert user of successful withdraw
            await ctx.reply(f"Your withdrawal was processed!")
        except Exception as e:
            Common.logger.error(f"Error withdrawing funds: {e}", exc_info=True)   
            raise Exception(f"Exception with withdrawal to {vite_address}", e)   

    @commands.command(name='play', help="Play the trivia game.")
    async def play(self, ctx):

        try:
            day_rewards = 0
            # Check if we have an entry yet
            if ctx.message.author in self.bot.user_data:
                # Grab the entry
                my_user_data = self.bot.user_data[ctx.message.author]
                # Grab daily rewards
                day_rewards = my_user_data.get_daily_balance()
            else:
                # Create an entry in the user_data dictionary
                Common.log(f"Creating new UserData entry with {ctx.message.author}")
                my_user_data = UserData(ctx.message.author,self.bot.max_rewards_amount)
                self.bot.user_data[ctx.message.author] = my_user_data

            # Check if we are maxxing out at questions per this user
            if day_rewards >= self.bot.max_rewards_amount:
                Common.log(f"{ctx.message.author} has maxxed out with daily rewards of {day_rewards}")
                await ctx.reply(f"You have reached the maximum rewards [{day_rewards:.2f}] allowed for per " + \
                    f"{self.bot.greylist_timeout} minute period.")
                # If not greylisted yet
                if(my_user_data.get_greylist() == 0):
                    # Greylist. Record future time greylist_timeout minutes in the future
                    my_user_data.set_greylist(self.bot.greylist_timeout)
                    minutes_left = (my_user_data.get_greylist_future() - time.time()) / 60.0
                    await ctx.reply(f"You are greylisted for another {minutes_left} minutes.")
                    return
                elif(my_user_data.get_greylist() > int(time.time())):
                    # If greylist is still in future
                    minutes_left = (my_user_data.get_greylist_future() - time.time()) / 60.0
                    await ctx.reply(f"You are greylisted for another {minutes_left} minutes.")
                    return
                else:
                    # Time is past greylist. Clear greylist
                    my_user_data.clear_daily_rewards()
                    my_user_data.clear_greylist()
                    await ctx.reply(f"You are no longer greylist.")

            # Grab a random trivia question 
            q = random.choice(self.bot.questions)
            # Print out question as multiple-choice
            question = q.get_question()
            correct_answer = q.get_correct_answer().strip()
            answers = q.get_answers().copy()
            # Randomly shuffle answers
            random.shuffle(answers)
            # Which # the correct answer is
            correct_index = 0
            # Formulate the question with randomly shuffled multiple choice answers
            response = f"**{question}**\n"
            i = 1
            for answer in answers:
                if(answer == q.get_correct_answer()): correct_index = i
                label = "**" + str(i) + ")** " + answer
                response += label + "\n"
                i = i + 1
            await ctx.message.author.send(response)

            # Check that the message is from the right user and a DM
            def check(message):
                return message.author == ctx.message.author and message.guild is None

            try:
                msg = await self.bot.wait_for("message", timeout=self.bot.answer_timeout, check=check)
                correct = False
                # Check by text answer
                if(msg.content.strip() == correct_answer):
                    correct = True
                else:
                    # Check by index
                    try: 
                        index = int(msg.content)
                        if(index == correct_index):
                            correct = True
                    except ValueError:
                        correct = False
                # If correct send vite
                if(correct):
                    # Record win
                    my_user_data.add_win()
                    # Add reward amount to balance
                    my_user_data.add_daily_balance(self.bot.token_amount)
                    await ctx.message.author.send(f"Correct. Congratulations! Your balance is now " +
                        f"{my_user_data.get_daily_balance():.2f}")
                else:
                    # Record loss
                    my_user_data.add_loss()
                    await ctx.message.author.send(f"I'm sorry, that answer was wrong. The correct " + 
                         f"answer was \"{correct_answer}\"")
            except asyncio.TimeoutError:
                # User took too long to answer question
                my_user_data.add_loss()
                await ctx.message.author.send(f"Sorry, you took too much time to answer! The correct answer " +
                    f"was \"{correct_answer}\"")

        except Exception as e:
            Common.logger.error(f"Error in game: {e}", exc_info=True)      
            raise Exception(f"Error processing question request", e)   
                    

# Plug-in function to add cog
def setup(bot):
    bot.add_cog(GameCog(bot))