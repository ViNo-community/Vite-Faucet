# Henlo
## Get it running
```sh
git clone https://github.com/JeanOUINA/vite-send-server
cd vite-send-server
npm install
cp ./config.example.json ./config.json
```
And then, edit your config.json.
```js
{
    // Put the api key, only you should be able to send vite
    // Only for server
    "API_KEY": "Your api key",
    // Your vite credentials
    "VITE_LOGIN": {
        // Possible options are: seed, mnemonic and private key
        "type": "seed",
        // The account index. Should be 0 for private key
        "index": 0,
        // The mnemonic/seed/private key
        "credentials": "spare lawn border inner they genre ethics tide curious wire bus bike need leave decrease focus pepper lamp use recall black faint brisk tent"
    },
    // The RPC node you're going to use
    // Websockets and Https nodes are supported
    "VITE_NODE": "https://vitanode.lightcord.org/http",
    // the port of the server
    // Only for server
    "PORT": 1337
}
```
### Normal script
Usage:
```sh
node send_vite vite_aa8e76ea53c8f96bccadfc9819ae1da60b5c74a304e538d870 10
```
to send 10 vite to vite_aa8e76ea53c8f96bccadfc9819ae1da60b5c74a304e538d870
### Server
And then, launch it with `node send_vite_server`

That's it !

## Use it
> I'm going to assume that the server is running on http://[::1]:1337/
### NodeJS
```js
const fetch = require("node-fetch")
const res = fetch("http://[::1]:1337", {
    headers: {
        Authorization: "YOUR_API_KEY"
    },
    method: "post",
    body: JSON.stringify({
        action: "send",
        params: [TOKEN_ID, AMOUNT, DESTINATION]
    })
})

const body = await res.json()
console.log(body)
if(res.status === 200){
    // success
}else{
    // error
}
```
