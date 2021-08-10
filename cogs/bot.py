from discord.ext import commands
import dotenv
from common import Common

class BotCog(commands.Cog, name="Bot"):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='set_prefix', help='Set bot prefix')
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
            await ctx.reply(f"Set new command prefix to \"{new_prefix}\"")
        except Exception as e:
            raise Exception(f"Could not change command prefix to \"{new_prefix}\"", e)  

    # Shows all current bot settings
    @commands.command(name='show_config', aliases=['config','botconfig','bot_config'], help="Show the current bot config")
    async def show_config(self,ctx):
        try:
            # Show ALL information
            response = f"**Command Prefix:** {self.bot.command_prefix}" + \
                f"\n**Logging Level:** {self.bot.logging_level}" + \
                f"\n**Faucet Address:** {self.bot.faucet_address}" + \
                f"\n**Greylist Time Period:** {self.bot.greylist_timeout}" + \
                f"\n**Token Type ID (TTI):** {self.bot.token_id}" + \
                f"\n**Token Amount Per Correct Answer:** {self.bot.token_amount}" + \
                f"\n**Max Questions Per Time Period:** {self.bot.max_questions_amount}"
            await ctx.reply(response)
        except Exception as e:
            raise Exception("Exception showing info summary", e)   

    # Set logging level for the bot
    @commands.command(name='set_logging', help="Set logging level")
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

# Plug-in function to add cog
def setup(bot):
    bot.add_cog(BotCog(bot))