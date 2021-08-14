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
            answer = q.get_correct_answer()
            answers = q.get_answers().copy()
            # Randomly shuffle answers
            print("Correct answer " + q.get_correct_answer())
            random.shuffle(answers)
            correct = 0
            print("Correct answer " + q.get_correct_answer())
            response = question + "\n"
            i = 1
            for answer in answers:
                if(answer == q.get_correct_answer()):
                    correct = i
                    print(f"Corret answer is {correct}")
                label = str(i) + ") " + answer
                response += label + "\n"
                i = i + 1
            await ctx.message.author.send(response)

            def check(message):
                print(f"Author: {message.author.name} Ctx.author: {ctx.author.name}")
                # Check that the message is from the right user
                if(message.author.name == ctx.author.name):
                    print(f"Message: {message.content.strip()} Answer: {answer}")
                    # Check by text answer
                    if(message.content.strip() == answer):
                        return True
                    else:
                        # Check by index
                        try: 
                            index = int(message.content)
                            if(index == correct):
                                return True
                        except ValueError:
                            return False
                        return False

            try:
                correct = await self.bot.wait_for("message", timeout=self.bot.answer_timeout, check=check)
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