const fs = require('fs');
const { ViteAPI } = require('@vite/vitejs');
const Discord = require('discord.js');
const client = new Discord.Client();

require('dotenv').config(); 
client.commands = mew Discord.Collection();

const commandFiles = fs.readdirSync('./commands').filter(file => file.endsWith('.js'));
const eventFiles = fs.readdirSync('./events').filter(file => file.endsWith('.js'));


for (const file of commandFiles) {
	const command = require(`./commands/${file}`);
	// set a new item in the Collection
	// with the key as the command name and the value as the exported module
	client.commands.set(command.name, command);
}

for (const file of eventFiles) {
	const event = require(`./events/${file}`);
	if (event.once) {
		client.once(event.name, (...args, client) => event.execute(...args));
	} else {
		client.on(event.name, (...args, client) => event.execute(...args));
	}
}






