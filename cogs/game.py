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

    @commands.command(name='start', help="Start the trivia game")
    async def start(self, ctx, vite_address=""):
        # Check that vite_address is not blank
        if(vite_address == ""):
            await ctx.send(f"Usage: {self.bot.command_prefix}start <new_prefix>")
            return    
        # Make sure that address is for vite
        if(vite_address.startswith("vite_") == False):
            await ctx.reply(f"Please only use vite addresses. Usage: {self.bot.command_prefix}start <vite address>")
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
                print("Sending to " + vite_address)
                #send_vite(vite_address)
            else:
                await ctx.message.author.send("Wrong answer!")
        except Exception as e:
            raise Exception(f"Error processing question request", e)          

# Plug-in function to add cog
def setup(bot):
    bot.add_cog(GameCog(bot))