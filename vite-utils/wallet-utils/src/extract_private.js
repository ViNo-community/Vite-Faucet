const { wallet } = require('@vite/vitejs');

MNEMONIC_WORD = process.env.MNEMONIC_WORD
const args = process.argv.splice(2);

var index = 0;
if (args.length > 1) {
	index = args[0]
}

if (MNEMONIC_WORD) {
	const { originalAddress, publicKey, privateKey, address } = wallet.deriveAddress({
		mnemonics: MNEMONIC_WORD,
		index: index
	});
	console.log('address: ', address);
	console.log('public key: ', publicKey);
	console.log('private key: ', privateKey);
} else {
	console.error('environment variable[MNEMONIC_WORD] must be set');
}