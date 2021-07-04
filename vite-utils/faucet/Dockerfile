FROM python:3.7.0

WORKDIR /app

RUN pip3 install requests discord.py python-dotenv

COPY ./ /app

CMD [ "python3", "discord-bot.py" ]