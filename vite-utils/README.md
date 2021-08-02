Vite Trivia Faucet game

To run, load questions.txt with questions in format of:
[Question]
[Answer #1 - Right Answer]
[Answer #2]
[Answer #3]
[Answer #4]

Copy .env.example file to .env and put in the Vite account of your faucet along with the private key.
IMPORTANT: KEEP THIS INFORMATION PRIVATE!
Fill in how much you want to reward per correct answer in TOKEN_AMOUNT
Fill in how long you want the greylist period to be in GREYLIST_TIMEOUT

To run the faucet bot, run $ python discord-bot.py