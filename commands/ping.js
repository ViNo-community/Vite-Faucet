module.exports = {
  name: 'ping',
  description: 'ping!',
  execute(message, args, client){
    messsage.channel.send('Pong!');
  }


}
