import asyncio
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
                reward_count = my_user_data.get_total_rewards()
                right_answers = my_user_data.get_right_answers()
                wrong_answers = my_user_data.get_wrong_answers()
                total_answers = right_answers + wrong_answers
                balance = my_user_data.get_balance()
                right_pct = (float)(right_answers / total_answers) * 100
                wrong_pct = (float)(wrong_answers / total_answers) * 100
                # Show ALL information
                response = f"**Right Answers:** {right_answers}/{total_answers}\t{right_pct}%" + \
                    f"\n**Wrong Answers:** {wrong_answers}/{total_answers}\t{wrong_pct}%" + \
                    f"\n**Balance:** {balance}" + \
                    f"\n**Reward Count:** {reward_count} / {self.bot.max_rewards_amount}"
                await ctx.reply(response)
            else:
                response = f"No score information yet for {ctx.message.author}"
                await ctx.reply(response)
        except Exception as e:
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
            raise Exception(f"Exception with withdrawal to {vite_address}", e)   

    @commands.command(name='play', help="Play the trivia game.")
    async def play(self, ctx):

        try:
            total_rewards = 0
            # Check if we have an entry yet
            if ctx.message.author in self.bot.user_data:
                # Grab the entry
                my_user_data = self.bot.user_data[ctx.message.author]
                total_rewards = my_user_data.get_total_rewards()
            else:
                # Create an entry in the user_data dictionary
                print(f"Creating new UserData with {ctx.message.author}")
                my_user_data = UserData(ctx.message.author)
                self.bot.user_data[ctx.message.author] = my_user_data

            # Check if we are maxxing out at questions per this user
            if total_rewards > self.bot.max_rewards_amount:
                await ctx.reply(f"You have reached the maximum number of rewards " + \
                    f"per time period [{self.bot.max_rewards_amount}]")
                # If not greylisted yet
                if(my_user_data.get_greylist_future() == 0):
                    # Greylist. Record future time greylist_timeout minutes in the future
                    my_user_data.start_greylist(self.bot.greylist_timeout)
                    return
                # If greylist is still in future
                elif(my_user_data.get_greylist_future() > int(time.time())):
                    wait_period = str(int((my_user_data.get_greylist_future() - time.time()) /
                            self.bot.greylist_timeout)) + " minutes."
                    await ctx.reply(f"You are greylisted for another {wait_period}")
                    return
                # Time is past greylist. Clear greylist
                else:
                    my_user_data.clear_total_rewards()
                    my_user_data.clear_greylist()

            # Grab a random trivia question 
            q = random.choice(self.bot.questions)
            # Print out question as multiple-choice
            question = q.get_question()
            correct_answer = q.get_correct_answer().strip()
            answers = q.get_answers().copy()
            # Randomly shuffle answers
            random.shuffle(answers)

            correct_index = 0
            response = f"**{question}**\n"
            i = 1
            for answer in answers:
                if(answer == q.get_correct_answer()): correct_index = i
                label = "**" + str(i) + ")** " + answer
                response += label + "\n"
                i = i + 1
            await ctx.message.author.send(response)

            # Check that the message is from the right user and on the right channel
            def check(message):
                return message.author == ctx.message.author and message.channel == ctx.message.channel

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
                    my_user_data.add_win_to_score()
                    my_user_data.set_balance(my_user_data.get_balance() + self.bot.token_amount)
                    my_user_data.add_total_rewards(self.bot.token_amount)
                    await ctx.message.author.send(f"Correct. Congratulations! Your balance is now {my_user_data.get_balance()}")
                else:
                    my_user_data.add_loss_to_score()
                    await ctx.message.author.send(f"I'm sorry, that answer was wrong. The correct " + 
                         f"answer was \"{correct_answer}\"")
            except asyncio.TimeoutError:
                my_user_data.add_loss_to_score()
                await ctx.message.author.send(f"Sorry, you took too much time to answer! The correct answer " +
                    f"was \"{correct_answer}\"")

        except Exception as e:
            Common.logger.error(f"Error in game: {e}", exc_info=True)      
            raise Exception(f"Error processing question request", e)   
                    

# Plug-in function to add cog
def setup(bot):
    bot.add_cog(GameCog(bot))