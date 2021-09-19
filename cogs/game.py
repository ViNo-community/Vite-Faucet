from vite_functions import get_account_balance
import asyncio
import datetime
import requests
from bs4 import BeautifulSoup

import discord
from player import Player
from discord.ext import commands
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

        # Validate withdrawal address
        try:
            if(Common.isValidAddress(vite_address) == False):
                Common.log(f"Invalid withdrawal adress \"{vite_address}\"")
                response = f"Invalid withdrawal adress \"{vite_address}\""
                await ctx.send(response)
        except Exception as e:
            Common.logger.error(f"Invalid withdrawal address \"{vite_address}\": {e}", exc_info=True)   
            response = f"Invalid withdrawal address \"{vite_address}\": {e}"
            await ctx.send(response)
            return

        try:
            # Deposit the balance to the vite address
            hash = await self.bot.send_vite(ctx.message.author,vite_address,send_balance)
            print(hash)
            # Clear the balance
            my_player_data.clear_unsent_balance()
            # Grab wallet address of user for future reference
            my_player_data.set_wallet_address(vite_address)
            # Alert user of successful withdraw
            await ctx.send(f"You have successfully sent {send_balance} tokens to {vite_address}: {hash}")
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

        # Check account balance
        balance = await get_account_balance(self.bot.faucet_address)
        # Check if balance can cover any more correct answers
        if(balance <= self.bot.token_amount):
            Common.log(f"Cannot play. Bot is currently disabled due to low account balance: {balance}")
            await ctx.send(f"Trivia game has been temporarily disabled due to low account balance") 
            return
        # Check if balance is below low balance alert
        elif(balance <= self.bot.low_balance_alert):
            message = f"Faucet balance {balance:,.4f} is below low balance alert {self.bot.low_balance_alert:,.4f}"
            Common.log(message)
            # Temporarily disable game
            self.bot.disabled = True    
            # Alert mods of low balance
            channel = self.bot.get_channel(855044743964000256)
            await channel.send(f"<@&842978912518668309> <@&842979377456218123> : {message}")
            await ctx.send(f"Trivia game has been temporarily disabled due to low account balance") 
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
                Common.logger.debug(f"Found user data {my_player_data}")
            else:
                # Create an entry in the player_data dictionary
                Common.log(f"Creating new Player data entry with {ctx.message.author}")
                my_player_data = Player(ctx.message.author)
                self.bot.player_data[ctx.message.author] = my_player_data

            # Check if user is grey-listed
            # Then check if grey-list has expired or not
            if(my_player_data.get_greylist() != 0):
                if(my_player_data.get_greylist() > int(time.time())):
                    # If greylist is still in future
                    Common.log(f"Greylist is in future : {my_player_data.get_greylist()}")
                    minutes_left = (my_player_data.get_greylist() - time.time()) / 60.0
                    response = f" You are greylisted for another {minutes_left:.4f} minutes."
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
                    day_limit = my_player_data.get_daily_limit()
                    await ctx.message.author.send(f"Correct. Congratulations! Your balance for this quiz period is now " +
                        f"{day_limit:.2f}")
                    
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
    @commands.has_any_role('Core','Dev','VINO Team')
    async def export(self, ctx, date=""):
        try:
             # If no date provided use todays date
            if(date == ""):
                # Grab current transactions file
                filename = self.bot.transactions_filename
                # Date is today
                date = datetime.datetime.now().strftime("%Y%m%d") 
            else:
                # Check that date is in proper format YYYYMMDD
                try:
                    newDate = datetime.datetime.strptime(date, "%Y%m%d")
                    print(f"{date} => {newDate}")
                except ValueError:
                    await ctx.send(f"Invalid date \"{date}\". Usage: {self.bot.command_prefix}export YYYYMMDD")
                    return
                # Grab file for date provided
                filename = self.bot.transdir / f"{date}_transactions.csv"
            # Check if file exists
            if not os.path.exists(filename):
                # Alert user data doesn't exist for that day
                Common.logger.error(f"Could not export transactions file \"{filename}\" for {date} because it doesn't exist")
                await ctx.send(f"Could not export. Transactions file for {date} do not exist.")
                return
            else:
                # Upload file
                Common.log(f"Exporting transactions CSV file {filename} for {date} to channel")
                await ctx.send(file=discord.File(filename))
        except Exception as e:
            Common.logger.error(f"Error exporting file to channel {e}", exc_info=True)      
            raise Exception(f"Error exporting file to channel ", e)   

    @commands.command(name='scoreboard', alias=['scores','board'], help="Show the trivia game scoreboard")
    async def scoreboard(self, ctx):
        if(len(self.bot.player_data) == 0):
            await ctx.send("No score data yet.")
            return
        try: 
            # For some dumb reason, Discord.py doesn't allow embeds without the name field. 
            # So, to create a table where the headers only show up on the first row, we need 
            # to cram all the data into the value of the first row, separated by newlines. 
            name_string = ""
            points_string = ""
            score_string = ""
            i = 0
            # Generate the data strings from player score data 
            for player_name, player in sorted(self.bot.player_data.items(), key=lambda x: x[1].points, reverse = True):
                my_player_data = self.bot.player_data[player_name]
                # Show trophy emojis
                if(i == 0):
                    name_string = name_string + ":first_place:"
                    i = i + 1
                elif(i == 1):
                    name_string = name_string + ":second_place:"
                    i = i + 1
                elif(i == 2):
                    name_string = name_string + ":third_place:"
                    i = i + 1
                name_string = name_string + f"{my_player_data.get_name()}\n"
                points_string = points_string + f"{my_player_data.get_points()}\n"
                score_string = score_string + f"{str(round(my_player_data.get_score(),2))}%\n"
            # Construct the table
            embed=discord.Embed(title="Scoreboard", color=discord.Color.dark_blue())
            embed.add_field(name="Name", value=name_string, inline=True)
            embed.add_field(name="Points", value=points_string, inline=True)
            embed.add_field(name="Score", value=score_string, inline=True)
            await ctx.send(embed=embed)  
        except Exception as e:
            Common.logger.error(f"Error generating scoreboard: {e}", exc_info=True)      
            raise Exception(f"Error generating scoreboard ", e) 


    # Hidden Easter Egg command - !meow - shows a random image of a cat
    @commands.command(name='woof',hidden=True)
    async def woof(self,ctx):
        try:
            # Grab google image search results for cat
            page= requests.get('http://www.google.com/search?q=dogs&source=lnms&tbm=isch', headers={'User-Agent': 'Mozilla/5.0'})
            # Parse through and grab all the non-gif image links
            soup = BeautifulSoup(page.text, 'html.parser')
            dog_images = []
            for link in soup.find_all('img'):
                src=link.get('src')
                if(not src.endswith('gif')):    # Exclude gifs
                    dog_images.append(src)
            # Grab a random image from the list
            idx = random.randint(0,len(dog_images))
            # Embed the image and share with chat
            imageURL = dog_images[idx]
            embed = discord.Embed()
            embed.set_image(url=imageURL)
            await ctx.send(embed=embed)
        except Exception as e:
            raise Exception("Could not process meow request", e)  


# Plug-in function to add cog
def setup(bot):
    bot.add_cog(GameCog(bot))