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

    @commands.command(name='play', help="Play the trivia game")
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
            index = random.randint(0,len(self.bot.questions))
            q = self.bot.questions[index]
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

            answer = q.get_correct_answer()
            def check(message):
                print(f"Message: {message.content.strip()}")
                if(message.content.strip() == answer):
                    return True
                else:
                    return False

            try:
                correct = await self.bot.wait_for("message", timeout=20.0, check=check)
                if(correct):
                    await ctx.message.author.send("Correct. Congratulations!")
                    #send_vite(vite_address)
                else:
                    await ctx.message.author.send(f"I'm sorry, that answer was wrong. The correct answer was {answer}")
            except asyncio.TimeoutError:
                await ctx.message.author.send(f"Sorry, you took too much time to answer! The correct answer was {answer}")

        except Exception as e:
            raise Exception(f"Error processing question request", e)          

# Plug-in function to add cog
def setup(bot):
    bot.add_cog(GameCog(bot))