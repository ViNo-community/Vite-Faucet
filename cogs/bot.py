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
            await ctx.send(f"Usage: {self.bot.command_prefix}set_prefix <new_prefix>")
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
    @commands.command(name='show_all', help="Show all bot settings")
    async def show_all(self,ctx):
        try:
            # Show ALL information
            response = f"Command prefix: {self.bot.command_prefix}" + \
                f"\nLogging Level: {Common.logger.level}" + \
                f"\nGreylist Time Period: {self.bot.greylist_timeout}" + \
                f"\nToken Amount Per Correct Answer: {self.bot.token_amount}" + \
                f"\nMax Questions Per Time Period: {self.bot.max_questions_amount}"
            await ctx.send(response)
        except Exception as e:
            raise Exception("Exception showing info summary", e)   

    # Set logging level for the bot
    @commands.command(name='set_logging', help="Set logging level")
    async def set_logging(self,ctx,new_level):
        try:
            new_logging_level = int(new_level)
            # Update logging level
            Common.logger.setLevel(new_logging_level)
            # Save in .env file
            dotenv.set_key(".env","logging_level", new_level)
            # Report successful logging level update to user
            await ctx.send(f"Set logging level to {new_logging_level}")
        except Exception as e:
            raise Exception(f"Could not change logging level to {new_logging_level}", e)    

# Plug-in function to add cog
def setup(bot):
    bot.add_cog(BotCog(bot))