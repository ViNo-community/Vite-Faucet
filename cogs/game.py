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

    @commands.command(name='play', help="Play the trivia game. Private message f!play [vite address] to the bot.")
    async def play(self, ctx, vite_address=""):
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
        
            question_number = 1

            # Check if we have an entry yet
            if ctx.message.author in self.bot.user_data:
                # Grab the entry
                my_user_data = self.bot.user_data[ctx.message.author]
                print(f"Grabbing entry for {vite_address}")
                question_number = my_user_data.get_question_count()
            else:
                # Create an entry in the user_data dictionary
                print(f"Creating new UserData with {ctx.message.author} and address {vite_address}")
                my_user_data = UserData(ctx.message.author,vite_address)
                self.bot.user_data[ctx.message.author] = my_user_data

            print(f"Question # {question_number}")
            # Check if we are maxxing out at questions per this user
            if question_number > self.bot.max_rewards_amount:
                await ctx.reply(f"You have reached the maximum number of rewards " + \
                    f"per time period [{self.bot.max_rewards_amount}]")
                return

            # Grab a random trivia question 
            q = random.choice(self.bot.questions)
            # Print out question as multiple-choice
            question = q.get_question()
            correct_answer = q.get_correct_answer().strip()
            answers = q.get_answers().copy()
            # Randomly shuffle answers
            random.shuffle(answers)
            correct_index = 0
            response = f"**{question_number}) {question}**\n"
            i = 'A'
            for answer in answers:
                if(answer == q.get_correct_answer()): correct_index = ord(i) - ord('A') + 1
                label = "**" + str(i) + ")** " + answer
                response += label + "\n"
                i = chr(ord(i) + 1)
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
                        index = ord(msg.content) - ord('A') + 1

                        if(index == correct_index):
                            correct = True
                    except ValueError:
                        correct = False
                # If correct send vite
                if(correct):
                    await ctx.message.author.send(f"Correct. Congratulations! The correct answer was {correct_answer}.\n" + 
                        f"Sending {self.bot.token_amount} vite to {vite_address}.")
                    # Increment quesetion count
                    my_user_data.next_question_count()
                    self.bot.send_vite(vite_address)
                else:
                    await ctx.message.author.send(f"I'm sorry, that answer was wrong. The correct answer was {correct_answer}")
            except asyncio.TimeoutError:
                await ctx.message.author.send(f"Sorry, you took too much time to answer! The correct answer was {correct_answer}")

        except Exception as e:
            Common.logger.error(f"Error in game: {e}", exc_info=True)      
            raise Exception(f"Error processing question request", e)   
                    

# Plug-in function to add cog
def setup(bot):
    bot.add_cog(GameCog(bot))