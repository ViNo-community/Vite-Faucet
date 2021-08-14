import asyncio
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
        if(vite_address.startswith("vite_") == False):
            await ctx.reply(f"Please only use vite addresses. Usage: {self.bot.command_prefix}start <vite address>")
            return
        try:
            # Check if this address is grey-listed
            if vite_address in self.bot.limits:
                if self.bot.limits[vite_address] > int(time.time()):
                    await ctx.reply("You are greylisted for another " +
                        str(int((self.bot.limits[vite_address] - time.time()) /
                            self.bot.greylist_timeout)) + " minutes.")
                    return
            self.bot.limits[vite_address] = time.time() + 60 * self.bot.greylist_timeout
            # Grab a random trivia question 
            q = random.choice(self.bot.questions)
            # Print out question as multiple-choice
            question = q.get_question()
            correct_answer = q.get_correct_answer().strip()
            answers = q.get_answers().copy()
            # Randomly shuffle answers
            random.shuffle(answers)
            correct_index = 0
            response = "**" + question + "**\n"
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
                    await ctx.message.author.send(f"Correct. Congratulations! The correct answer was {correct_answer}.\n" + 
                        f"Sending {self.bot.token_amount} vite to {vite_address}.")
                    self.bot.send_vite(vite_address)
                else:
                    await ctx.message.author.send(f"I'm sorry, that answer was wrong. The correct answer was {correct_answer}")
            except asyncio.TimeoutError:
                await ctx.message.author.send(f"Sorry, you took too much time to answer! The correct answer was {correct_answer}")

        except Exception as e:
            raise Exception(f"Error processing question request", e)          

# Plug-in function to add cog
def setup(bot):
    bot.add_cog(GameCog(bot))