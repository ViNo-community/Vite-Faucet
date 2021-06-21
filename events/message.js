module.exports{
  name: 'message',
  execute(message, client) {
    if(messsage.author.bot) return;
    if(message.channel.type =='dm') return;
    if(!message.content.startswith(client.prefix));
  
    const args = message.content.slice(client.prefix.length).trim().split(/ +/);
    if (!client.commands.has(commandName)) return;
    const command = client.commands.get(commandName);

    try{
      command.execute(message, args, client);


    } catch(err) {
      console.log(err)
    }
  
  
  
  },








}
