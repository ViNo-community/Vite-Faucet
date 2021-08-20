from discord.ext import commands
import dotenv
from common import Common

class BotCog(commands.Cog, name="Bot"):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='set_prefix', help='Set bot prefix [Admin Only]')
    @commands.has_any_role('Core','Dev')
    async def set_prefix(self, ctx, new_prefix=""):
        # Check that new prefix is valid
        if(new_prefix == ""):
            await ctx.reply(f"Usage: {self.bot.command_prefix}set_prefix <new_prefix>")
            return
        try:
            # Update command prefix
            self.bot.command_prefix = new_prefix
            # Update the .env file
            dotenv.set_key(".env","command_prefix", new_prefix)
            # Update the bot status
            await self.bot.update_status()
            # Alert user of successful command prefix update
            await ctx.send(f"Set new command prefix to \"{new_prefix}\"")
        except Exception as e:
            raise Exception(f"Could not change command prefix to \"{new_prefix}\"", e)  

    # Shows all current bot settings
    @commands.command(name='show_config', aliases=['config','botconfig','bot_config'], help="Show the current bot config")
    async def show_config(self,ctx):
        try:
            # Show ALL information
            response = f"**Disabled:** {self.bot.disabled}" + \
                f"\n**Command Prefix:** {self.bot.command_prefix}" + \
                f"\n**Logging Level:** {self.bot.logging_level}" + \
                f"\n**RPC URL:** {self.bot.rpc_url}" + \
                f"\n**Faucet Address:** {self.bot.faucet_address}" + \
                f"\n**Answer Timeout:** {self.bot.answer_timeout}" + \
                f"\n**Greylist Time Period:** {self.bot.greylist_timeout}" + \
                f"\n**Token Type ID (TTI):** {self.bot.token_id}" + \
                f"\n**Token Amount Per Correct Answer:** {self.bot.token_amount}" + \
                f"\n**Max Rewards Per Time Period:** {self.bot.max_rewards_amount}"
            await ctx.send(response)
        except Exception as e:
            raise Exception("Exception showing info summary", e)   

    # Set logging level for the bot
    @commands.command(name='set_logging', help="Set logging level [Admin Only]")
    @commands.has_any_role('Core','Dev')
    async def set_logging(self,ctx,new_level):
        try:
            new_logging_level = int(new_level)
            # Update logging level
            Common.logger.setLevel(new_logging_level)
            self.bot.logging_level = new_logging_level
            # Save in .env file
            dotenv.set_key(".env","logging_level", new_level)
            # Report successful logging level update to user
            await ctx.reply(f"Set logging level to {new_logging_level}")
        except Exception as e:
            raise Exception(f"Could not change logging level to {new_logging_level}", e)    

    # Start the bot
    @commands.command(name='start', help="Start the bot [Admin Only]")
    @commands.has_any_role('Core','Dev')
    async def start(self,ctx):
        self.bot.disabled = False
        await ctx.reply("Trivia game has been enabled")

    # Start the bot
    @commands.command(name='stop', help="Stop the bot [Admin Only]")
    @commands.has_any_role('Core','Dev')
    async def stop(self,ctx):
        self.bot.disabled = True     
        await ctx.reply(f"Trivia game has been disabled") 

    @commands.command(name='invite', help="Displays invite link [Admin Only]")
    @commands.has_any_role('Core','Dev')
    async def invite(self,ctx):
        try:
            client_id = self.bot.get_client_id()
            response = f"Open a browser and go to https://discord.com/oauth2/authorize?client_id={client_id}&permissions=247872&scope=bot"
            await ctx.send(response)
        except Exception as e:
            raise Exception("Exception generating invite link", e)   

# Plug-in function to add cog
def setup(bot):
    bot.add_cog(BotCog(bot))