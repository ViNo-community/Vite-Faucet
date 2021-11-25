import subprocess
import discord
from discord.ext import commands
import dotenv
from common import Common
import traceback

from vite_functions import get_account_balance, get_account_quota

class BotCog(commands.Cog, name="Bot"):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='set_prefix', help='Set bot prefix [Admin Only]')
    @commands.has_any_role('Core','Dev','VINO Team')
    async def set_prefix(self, ctx, new_prefix=""):
        # Check that new prefix is valid
        if(new_prefix == ""):
            await ctx.send(f"Usage: {self.bot.command_prefix}set_prefix <new_prefix>")
            return
        if('@' in new_prefix):
            await ctx.send(f"Prefix cannot contain @")
            return
        try:
            # Update command prefix
            self.bot.command_prefix = new_prefix
            # Update the .env file
            dotenv.set_key(".env","command_prefix", new_prefix)
            # Update the bot status
            await self.bot.update_status()
            # Alert user of successful command prefix update
            Common.log(f"{ctx.message.author} set new command prefix to \"{new_prefix}\"")
            await ctx.send(f"Set new command prefix to \"{new_prefix}\"")
        except Exception as e:
            raise Exception(f"Could not change command prefix to \"{new_prefix}\"", e)  

    # Shows all current bot settings
    @commands.command(name='balance', aliases=['bal','balances','b'], help="Show the current faucet account balance")
    async def balance(self,ctx):
        try:
            pending_transactions = 0.0
            # Grab current balance
            balance = await get_account_balance(self.bot.faucet_address)
            # Sum all unsent balances
            for player_name, player in self.bot.player_data.items():
                my_player_data = self.bot.player_data[player_name]
                pending_transactions = pending_transactions + my_player_data.get_unsent_balance()
            # Calculate balance minus pending withdrawals
            pending = balance - pending_transactions
            # If disabled, show in Red. If enabled, show in Green
            showColor = discord.Color.green()
            if(self.bot.disabled): showColor = discord.Color.red()
            # Show account balances as embed
            embed=discord.Embed(title="Account Balance", color=showColor)
            embed.add_field(name="Balance", value=f"{balance:,.2f}", inline=True)
            embed.add_field(name="Available Balance", value=f"{pending:,.2f}", inline=True)
            embed.add_field(name="Low Balance Alert", value=f"{self.bot.low_balance_alert:,.2f}", inline=True)
            await ctx.send(embed=embed)
        except Exception as e:
            traceback.print_exc()
            raise Exception("Exception showing info summary", e)   

    # Shows faucet statistics
    @commands.command(name='statistics', aliases=['stat','stats'], help="Show faucet statistics")
    async def statistics(self,ctx):
        try:
            lusers = len(self.bot.player_data)
            distributed = self.bot.total_distributed
            # If disabled, show in Red. If enabled, show in Green
            showColor = discord.Color.green()
            if(self.bot.disabled): showColor = discord.Color.red()
            # Show account balances as embed
            embed=discord.Embed(title="Faucet Statistics", color=showColor)
            embed.add_field(name="Number of Users", value=lusers, inline=True)
            embed.add_field(name="Vite Distributed in Total", value=f"{distributed:,.2f}", inline=True)
            await ctx.send(embed=embed)
        except Exception as e:
            traceback.print_exc()
            raise Exception("Exception showing info summary", e)   

    # Shows all current bot settings
    @commands.command(name='show_config', aliases=['config','botconfig','bot_config'], help="Show the current bot config")
    async def show_config(self,ctx):
        try:
            balance = await get_account_balance(self.bot.faucet_address)
            quota = await get_account_quota(self.bot.faucet_address)
            # If disabled, show in Red. If enabled, show in Green
            showColor = discord.Color.green()
            if(self.bot.disabled): showColor = discord.Color.red()
            # Show config info as embed
            embed=discord.Embed(title="Config", description="Current bot configuration", color=showColor)
            embed.add_field(name="Disabled", value=self.bot.disabled, inline=True)
            embed.add_field(name="Command Prefix", value=self.bot.command_prefix, inline=True)
            embed.add_field(name="RPC URL", value=self.bot.rpc_url, inline=True)
            embed.add_field(name="Faucet Address", value=self.bot.faucet_address, inline=True)
            embed.add_field(name="Faucet Balance", value=f"{balance:,.2f}", inline=True)
            embed.add_field(name="Faucet Quota", value=f"{quota} UT", inline=True)
            embed.add_field(name="Low Balance Alert", value=f"{self.bot.low_balance_alert:,.2f}", inline=True)
            embed.add_field(name="Token Type ID (TTI)", value=self.bot.token_id, inline=True)
            embed.add_field(name="Token Reward per Correct Answer", value=self.bot.token_amount, inline=True)
            embed.add_field(name="Max Rewards per Quiz Period", value=self.bot.max_rewards_amount, inline=True)
            embed.add_field(name="Quiz Period [Minutes]", value=self.bot.greylist_duration, inline=True)
            embed.add_field(name="Answer Timeout [Seconds]", value=self.bot.answer_timeout, inline=True)
            embed.add_field(name="Logging Level", value=self.bot.logging_level, inline=True)
            await ctx.send(embed=embed)
        except Exception as e:
            traceback.print_exc()
            raise Exception("Exception showing info summary", e)   
           

    # Set logging level for the bot
    @commands.command(name='set_logging', aliases=['set_logging_level'], help="Set logging level [Admin Only]")
    @commands.has_any_role('Core','Dev','VINO Team')
    async def set_logging(self,ctx,new_level):
        new_level = new_level.replace('@','@\u200b') # Kaffin-proof user input
        try:
            new_logging_level = int(new_level)
            # Update logging level
            Common.logger.setLevel(new_logging_level)
            self.bot.logging_level = new_logging_level
            # Save in .env file
            dotenv.set_key(".env","logging_level", new_level)
            # Report successful logging level update to user
            Common.log(f"{ctx.message.author} set new logging level to \"{new_logging_level}\"")
            await ctx.send(f"Set logging level to {new_logging_level}")
        except Exception as e:
            raise Exception(f"Could not change logging level to {new_level}", e)    

    # Set the greylist duration period [Admin Only]
    @commands.command(name='set_greylist', help='Set greylist time period in minutes [Admin Only]')
    @commands.has_any_role('Core','Dev','VINO Team')
    async def set_greylist(self, ctx, param=""):
        param = param.replace('@','@\u200b') # Kaffin-proof user input
        try:
            new_greylist = float(param)
            if(new_greylist < 0):
                await ctx.send(f"Greylist duration must be positive")
                return
            self.bot.greylist_duration = new_greylist
            # Save in .env file
            dotenv.set_key(".env","greylist_duration", param)
            Common.log(f"{ctx.message.author} set new greylist time to \"{new_greylist}\"")
            await ctx.send(f"Greylist time period has been updated to {self.bot.greylist_duration} minutes")
        except ValueError:
            await ctx.send(f"Greylist duration must be a valid number")
            return
        except Exception as e:
            errorMsg = f"Error in set_greylist {e}"
            Common.logger.error(errorMsg, exc_info=True)
            await ctx.send(errorMsg)
            raise Exception(errorMsg, e)   

    # Start the bot
    @commands.command(name='receive', aliases=['pending'], help="Receive pending transactions [Admin Only]")
    @commands.has_any_role('Core','Dev','VINO Team')
    async def receive(self,ctx):
        try:
            # Call send_vite.js script
            command = ['node','scripts/pending_transactions.js']
            res = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if(res.returncode == 0):
                count = res.stdout.rstrip()
                message = f"{count} pending transactions were received"
                await ctx.send(message)
                Common.log(message)  
            elif(res.returncode == 1):
                e = res.stderr
                errorMsg = f"Error receiving pending transactions {e}. Please try again."
                Common.logger.error(errorMsg, exc_info=True) 
                await ctx.send(errorMsg)
        except Exception as e:
            errorMsg = f"Error in pending: {e}"
            Common.logger.error(errorMsg, exc_info=True)
            await ctx.send(errorMsg)
            raise Exception(errorMsg, e)   

    # Set reward amount per correct answer (Admin only)
    @commands.command(name='set_token_reward', help='Set reward size for one correct answer [Admin Only]')
    @commands.has_any_role('Core','Dev','VINO Team')
    async def set_token_reward(self, ctx, param=""):
        param = param.replace('@','@\u200b') # Kaffin-proof user input
        try:
            new_token_amount = float(param)
            if(new_token_amount < 0):
                await ctx.send(f"Token reward must be positive")
                return
            if(new_token_amount >= self.bot.max_rewards_amount):
                await ctx.send(f"Max_rewards amount must be greater than token_reward amount")
                return
            self.bot.token_amount = new_token_amount
            # Save in .env file
            dotenv.set_key(".env","token_amount", param)
            Common.log(f"{ctx.message.author} set new token reward amount to \"{new_token_amount}\"")
            await ctx.send(f"Token reward has been updated to {self.bot.token_amount}")
        except ValueError:
            await ctx.send(f"Token reward be a valid number")
            return
        except Exception as e:
            Common.logger.error(f"Error in set_token_reward {e}", exc_info=True)   
            raise Exception(f"Exception in set_token_reward", e)   

    # Set max reward amount per greylist period (Admin only)
    @commands.command(name='set_max_reward', help='Set max rewards allowed per time period [Admin Only]')
    @commands.has_any_role('Core','Dev','VINO Team')
    async def set_max_reward(self, ctx, param=""):
        param = param.replace('@','@\u200b') # Kaffin-proof user input
        try:
            amount = float(param)
            if(amount < 0):
                await ctx.send(f"Max rewards amount must be positive")
                return
            if(amount <= self.bot.token_amount):
                await ctx.send(f"Max_rewards amount must be greater than token_reward amount")
                return
            self.bot.max_rewards_amount = amount
            # Save in .env file
            dotenv.set_key(".env","max_rewards_amount",param)
            Common.log(f"{ctx.message.author} set new max rewards amount to \"{amount}\"")
            await ctx.send(f"Max rewards amount has been updated to {self.bot.max_rewards_amount}")
        except ValueError:
            await ctx.send(f"Maximum reward amount must be a valid number")
            return
        except Exception as e:
            Common.logger.error(f"Error in set_max_reward {e}", exc_info=True)   
            raise Exception(f"Exception in set_max_reward", e)   

    # Set low balance alert amount per greylist period (Admin only)
    @commands.command(name='set_low_balance_alert', help='Set low balance alert amount [Admin Only]')
    @commands.has_any_role('Core','Dev','VINO Team')
    async def set_low_balance_alert(self, ctx, param=""):
        param = param.replace('@','@\u200b') # Kaffin-proof user input
        try:
            amount = float(param)
            if(amount < 0):
                await ctx.send(f"Low balance alert amount must be positive")
                return
            self.bot.low_balance_alert = amount
            # Save in .env file
            dotenv.set_key(".env","low_balance_alert",param)
            Common.log(f"{ctx.message.author} set new low balance alert amount to \"{amount}\"")
            await ctx.send(f"Low balance alert amount has been updated to {self.bot.low_balance_alert}")
        except ValueError:
            await ctx.send(f"Low balance alert amount must be a valid number")
            return
        except Exception as e:
            Common.logger.error(f"Error in set_low_balance_alert {e}", exc_info=True)   
            raise Exception(f"Exception in set_low_balance_alert", e)   

    # Start the bot
    @commands.command(name='start', help="Start the bot [Admin Only]")
    @commands.has_any_role('Core','Dev','VINO Team')
    async def start(self,ctx):
        self.bot.disabled = False
        await ctx.send("Trivia game has been enabled")

    # Start the bot
    @commands.command(name='stop', help="Stop the bot [Admin Only]")
    @commands.has_any_role('Core','Dev','VINO Team')
    async def stop(self,ctx):
        self.bot.disabled = True     
        await ctx.send(f"Trivia game has been disabled") 
 
# Plug-in function to add cog
def setup(bot):
    bot.add_cog(BotCog(bot))