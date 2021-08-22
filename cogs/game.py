import asyncio
import datetime

import discord
from player import Player
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

    @commands.command(name='score', alias=['data','player'], help="Show your current score and account balance.")
    async def score(self, ctx):
        try:
            # Check if we have an entry yet
            if ctx.message.author in self.bot.player_data:
                # Grab the entry
                my_player_data = self.bot.player_data[ctx.message.author]
                # Make wallet address something because god damn stupid piece of shit
                # crashes on empty values
                wallet_address = "Not Set"
                if(my_player_data.get_wallet_address() != ""):
                    wallet_address = my_player_data.get_wallet_address()
                # Shower user info as embed
                embed=discord.Embed(title="Score Data", color=discord.Color.dark_blue())
                embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
                embed.add_field(name="Points", value=my_player_data.get_points(), inline=True)
                embed.add_field(name="Total User Balance", value=round(my_player_data.get_balance(),2), inline=True)
                embed.add_field(name="Unsent Balance", value=round(my_player_data.get_unsent_balance(),2), inline=True)
                embed.add_field(name="Sent Balance", value=round(my_player_data.get_sent_balance(),2), inline=True)
                embed.add_field(name="Period Total", value=round(my_player_data.get_daily_limit(),2), inline=True)
                embed.add_field(name="Period Limit", value=round(self.bot.max_rewards_amount,2), inline=True)
                embed.add_field(name="Right Answers", value=my_player_data.get_right_answers(), inline=True)
                embed.add_field(name="Total Answers", value=my_player_data.get_total_answers(), inline=True)
                embed.add_field(name="Score", value=str(round(my_player_data.get_score(),2)) + "%", inline=True)
                embed.add_field(name="Greylist", value=my_player_data.get_greylist_as_string(), inline=True)
                embed.add_field(name="Wallet Address", value=wallet_address, inline=True)
                await ctx.send(embed=embed)
            else:
                response = f"No player information yet for {ctx.message.author}"
                await ctx.send(response)
        except Exception as e:
            Common.logger.error(f"Error showing scoreboard: {e}", exc_info=True)   
            raise Exception("Exception showing score", e)       

    @commands.command(name='withdraw', help="Withdraw your balance to an external vite wallet.")
    async def deposit(self, ctx, vite_address=""):
        # Check the bot is not disabled
        if(self.bot.disabled):
            Common.log(f"Cannot process withdraw. Bot is currently disabled")
            await ctx.send(f"Trivia game has been temporarily disabled") 
            return
            
        # Check if we have an entry yet
        if ctx.message.author in self.bot.player_data:
            # Grab the entry
            my_player_data = self.bot.player_data[ctx.message.author]
            send_balance = my_player_data.get_unsent_balance()
            if(send_balance == 0):
                Common.log(f"Could not withdraw because empty unsent balance for {ctx.message.author}") 
                response = f"Your unsent balance is empty"
                await ctx.send(response)
                return
        else:
            Common.log(f"Could not withdraw because no info for {ctx.message.author}")
            response = f"No score information yet for {ctx.message.author}"
            await ctx.send(response)
            return
        # Check that vite_address is not blank
        if(vite_address == ""):
            # See if a wallet address is saved in our player data
            if(my_player_data.get_wallet_address() != ""):
                vite_address = my_player_data.get_wallet_address()
            else:
                await ctx.send(f"Usage: {self.bot.command_prefix}withdraw [vite address]")
                return    
        # Make sure that address is for vite
        if(vite_address.startswith("vite") == False):
            await ctx.send(f"Please only use vite addresses. Usage: {self.bot.command_prefix}start <vite address>")
            return
        try:
            # Deposit the balance to the vite address
            self.bot.send_vite(ctx.message.author,vite_address,send_balance)
            # Clear the balance
            my_player_data.clear_unsent_balance()
            # Grab wallet address of user for future reference
            my_player_data.set_wallet_address(vite_address)
            # Alert user of successful withdraw
            await ctx.send(f"You have successfully sent {send_balance} tokens to {vite_address}")
            my_player_data.add_sent_balance(send_balance)
        except Exception as e:
            Common.logger.error(f"Error withdrawing funds: {e}", exc_info=True)   
            raise Exception(f"Exception with withdrawal to {vite_address}", e)   

    @commands.command(name='play', help="Play the trivia game.")
    async def play(self, ctx):

        # Check if bot is disabled
        if(self.bot.disabled):
            Common.log(f"Cannot play. Bot is currently disabled")
            await ctx.send(f"Trivia game has been temporarily disabled") 
            return

        try:
            day_limit = 0
            # Check if we have an entry yet
            if ctx.message.author in self.bot.player_data:
                # Grab the entry
                my_player_data = self.bot.player_data[ctx.message.author]
                # Grab daily total to check against max reward
                day_limit = my_player_data.get_daily_limit()
                # User data found
                Common.log(f"Found user data {my_player_data}")
            else:
                # Create an entry in the player_data dictionary
                Common.log(f"Creating new Player entry with {ctx.message.author}")
                my_player_data = Player(ctx.message.author)
                self.bot.player_data[ctx.message.author] = my_player_data

            # Check if we are maxxing out at questions per this user
            if round(day_limit,2) >= round(self.bot.max_rewards_amount,2):
                Common.log(f"{ctx.message.author} has maxxed out with daily rewards of {day_limit:.2f}")
                response = f"You have reached the maximum rewards [{day_limit:.2f}] allowed for this time period."
                # If not greylisted yet
                if(my_player_data.get_greylist() == 0):
                    Common.log(f"No greylist detected")
                    # Greylist. Record future time greylist_timeout minutes in the future
                    my_player_data.set_greylist(self.bot.greylist_duration)
                    minutes_left = (my_player_data.get_greylist() - time.time()) / 60.0
                    response = response + f" You have been added to the greylist for a period of {minutes_left:.4f} minutes."
                    await ctx.send(response)
                    return
                elif(my_player_data.get_greylist() > int(time.time())):
                    # If greylist is still in future
                    Common.log(f"Greylist is in future : {my_player_data.get_greylist()}")
                    minutes_left = (my_player_data.get_greylist() - time.time()) / 60.0
                    response = response + f" You are greylisted for another {minutes_left:.4f} minutes."
                    await ctx.send(response)
                    return
                else:
                    Common.log(f"Clear greylist for {ctx.message.author}")
                    # Time is past greylist. Clear greylist
                    my_player_data.clear_daily_limit()
                    my_player_data.clear_greylist()

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
                if(msg.content == (self.bot.command_prefix + "play")):
                    return

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
                    my_player_data.add_win()
                    # Add reward amount to balance
                    my_player_data.add_balance(self.bot.token_amount)
                    await ctx.message.author.send(f"Correct. Congratulations! Your balance for this quiz period is now " +
                        f"{my_player_data.get_daily_limit():.2f}")
                else:
                    # Record loss
                    my_player_data.add_loss()
                    await ctx.message.author.send(f"I'm sorry, that answer was wrong. The correct " + 
                         f"answer was \"{correct_answer}\"")
            except asyncio.TimeoutError:
                # User took too long to answer question
                await ctx.message.author.send(f"Sorry, you took too much time to answer! The correct answer " +
                    f"was \"{correct_answer}\"")

        except Exception as e:
            Common.logger.error(f"Error in game: {e}", exc_info=True)      
            return
           # raise Exception(f"Error processing question request", e)   
                    
    @commands.command(name='export', help="Export CSV file to channel. [Admin Only]")
    @commands.has_any_role('Core','Dev')
    async def export(self, ctx, date=""):
        try:
             # If no date provided use todays date
            filename = datetime.datetime.now().strftime("%Y%m%d") + "_transactions.csv"
            if(date != ""):
                filename = date + "_transactions.csv"

        except Exception as e:
            Common.logger.error(f"Error exporting file to channel {e}", exc_info=True)      
            raise Exception(f"Error generating output file ", e)   

    @commands.command(name='scoreboard', alias=['scores','board'], help="Show the trivia game scoreboard")
    async def scoreboard(self, ctx):
        if(len(self.bot.player_data) == 0):
            await ctx.send("No score data yet.")
            return
        try: 
            # Show scoreboard info as embed
            embed=discord.Embed(title="Scoreboard", description="Current player scores", color=discord.Color.dark_blue())
            for key in self.bot.player_data:
                my_player_data = self.bot.player_data[key]
                embed.add_field(name="Name", value=my_player_data.get_name(), inline=True)
                embed.add_field(name="Points", value=my_player_data.get_points(), inline=True)
                embed.add_field(name="Score", value=str(round(my_player_data.get_score(),2)) + "%", inline=True)
            await ctx.send(embed=embed)  
        except Exception as e:
            Common.logger.error(f"Error generating scoreboard: {e}", exc_info=True)      
            raise Exception(f"Error generating scoreboard ", e)   

# Plug-in function to add cog
def setup(bot):
    bot.add_cog(GameCog(bot))