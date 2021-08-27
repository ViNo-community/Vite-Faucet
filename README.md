Vite Trivia Faucet game

The questions for the Trivia Game are located in questions.txt and have the following format:

[Question]

[Answer #1 - Right Answer]

[Answer #2]

[Answer #3]

[Answer #4]

questions.txt currently has about 50 questions related to cryptocurrency, particularly Nano, Banano, and Vite, with the intention of educating users about them while also providing free Vite tokens for them to play around with. questions.txt can be loaded with any kind of questions, however. If you wanted to make an animal based Trivia Bot, for example, you could replace questions.txt with a list of animal questions. The questions and their answers will be randomly shuffled when asked. 

Copy .env.example file to .env and fill in the fields given.

Set your DISCORD_TOKEN and CLIENT_ID to the values found in your Discord developer account associated with the bot. You can find these fields in https://discord.com/developers/applications . DISCORD_TOKEN is a unique identifier associated with this particular bot that lets your code identify itself as the authentic Trivia Bot. If this token gets leaked people can create fraudalent Discord bots. In the event that your token does get leaked, re-generate it immediately. CLIENT_ID is used to identify the Discord application and in the generation of the invite link. 

Fill FAUCET_ADDRESS with the address of your faucet wallet, and FAUCET_PRIVATE_KEY with your wallet's private key.

IMPORTANT: KEEP THIS INFORMATION PRIVATE! RESTRICT READ PERMISSIONS ON .ENV. ANYONE WHO SEES YOUR FAUCET'S PRIVATE KEY WILL BE ABLE TO DRAIN ALL THE FUNDS FROM YOUR FAUCET. ANYONE WHO SEES YOUR DISCORD_TOKEN WILL BE ABLE TO RUN A FRAUDALENT BOT UNDER THE TRIVIA BOT NAME. BE VERY CAREFUL WITH WHO HAS ACCESS TO THE .ENV FILE!

rpc_url is the url used to send RPC (Remote Procedure Calls) to interact with the Vite network. Test net (test tokens) and main net (real tokens) use different URLs. 
rpc_timeout is how many seconds a RPC has before it times out.


Fill in how much you want to reward per correct answer in TOKEN_AMOUNT

Fill in how long you want the greylist period to be in GREYLIST_DURATION

Fill in how many tokens you want a user to be able to win before hitting greylist in MAX_REWARDS_AMOUNT

While the Trivia Bot was made to dispense Vite tokens, it can be configured to reward any kind of token on the Vite chain by modifying the token_id field with the TTI (Token Type ID) of the token type that you desire. To use Vite, set token_id  to "tti_5649544520544f4b454e6e40"



To run the faucet bot, run $ python discord-bot.py

Type f!help for a list of commands.

Type or DM f!play to the Trivia Bot to start a trivia game. You will be asked a question with four multiple choice answers, and be asked to pick the correct one. If you answer correctly, you will win TOKEN_AMOUNT amount of tokens. If you answer incorrectly you will not gain any tokens. If you do not answer within a certain amount of time, then the question is automatically marked wrong. This duration is settable in the .env file under ANSWER_TIMEOUT. You can keep winning Vite for answering questions correctly until you reach the MAX_REWARDS_AMOUNT. Once this amount is reached you will be put on a greylist for GREYLIST_DURATION minutes and won't be able to answer any more questions until this period has passed. Once the greylist is cleared, you can continue winning more tokens until you hit it once again.

To see your current score and balance information, type f!score.

To withdraw your balance into an external wallet, type f!withdraw [vite address] where vite_address is the address of your Vite wallet. If you attempt to use any other type of wallet, the bot will throw an error. Once you withdraw once the bot will remember your address, so you can just type f!withdraw from then on.

To see the current bot configuration, type f!config. The will show you all the settings the bot is currently running under, such as TOKEN_AMOUNT and GREYLIST_DURATION.

To show the scoreboard with all the player's scores sorted from highest to lowest, type f!scoreboard.

Log files are placed in the logs directory where each log file is in the format YYYYMMDD_faucet.log where the date is the day the bot has been run. f!set_logging is used to set the logging sensitivity where lower numbers mean more logging. This is the same concept as used in the Nano Node and Vite Node bots and is the standard for Python's logging module.

The bot records every withdraw transaction in a comma separated (CSV) spreadsheet placed in the transactions directory. Transactions are grouped by day. To grab a spreadsheet file to open in Excel, type f!export YYYYMMDD and it will export the file to the channel you typed the command in. You can enter any date and it will return the file if it exists, or alert you if there were no transactions that day. If no date is specified then it defaults to today.

There are several administrator commands that are only accesible to Core and Dev ViNo team members. These are to emergency stop the Trivia Bot in the event of raiding or hacking, or being able to change settings like MAX_REWARDS_AMOUNT or GREYLIST_DURATION dynamically. Changing these values also changes them in the .env file so that they are saved for the next execution.

f!stop stops the trivia bot indefinitely until someone issues a f!start. While the bot is stopped, users cannot f!play to answer new questions, or f!withdraw to withdraw their balances. This is useful in case the server ever becomes raided by bots trying to automatically drain the faucet. f!stop lets moderators stop the trivia bot without direct access to the server that the bot code is being run on.

f!start starts the trivia bot again after it's been stopped. Users will once again be able to f!play and f!withdraw.

f!set_greylist lets moderators set the greylist timeout value in minutes. A common value for this is 1440 which is 60 * 24 or one day. This can be set to 0 to disable the greylist entirely. 

f!set_max_reward sets the amount of tokens available to be won until the greylist is activated. This can also be set to 0 to disable it. If both greylist and max_reward are set to 0 then there are effectively no limits to how much Vite players can win.

f!set_prefix sets the bots command prefix, similar to Nano Node Bot and Vite Node Bot.

f!set_token_reward sets how many tokens are won for each correct answer.

f!invite generates an invite URL for moderators to be able to move the Trivia Bot to a new server.

When these settings are changed, they are saved in the .env file so that they are remembered between runs.

