const { ViteAPI } = require('@vite/vitejs');
const Discord = require('discord.js');
const client = new Discord.Client();



 //declaring messages in variables
  const msg1 = ("You begged Elon for digicoins. You received" + vite_amount + "Vite to the moon.")
  const msg2 = ("You're walking outside and Vite falls from the sky" + vite_amount)
  const msg3 = ("You run into a wild Shiba Inu, he gifts you the almighty Vite token. You received" + vite_amount)



client.on('start', () =>{
console.log("vite faucet is online")


})

// for help
client.on('message', message =>{
if(message === "*help"){
  message.channel.send("")

}
})

//for demanding vite
client.on('message', message =>{
  //find user in database, if not found, don't continue
  



//putting options into an array
  var msgs = [msg1, msg2, msg3];

//if demand
if(message === "*demand"){

//random message
var msg = msgs[Math.floor(Math.random() * msgs.length)];

//random viteValue
let faucetValue = Math.random();
let vite_amount = faucetValue;
//find user address



//send user vite_amount
 



}



})
