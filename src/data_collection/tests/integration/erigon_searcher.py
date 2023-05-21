from web3 import Web3, HTTPProvider
import web3

w3 = Web3(provider=HTTPProvider(endpoint_uri="http://192.168.178.100:8545"))

#0x6C8f2A135f6ed072DE4503Bd7C4999a1a17F824B eth alarm clock contract

logs = w3.eth.get_logs({
    'from_block': 1, 
    'to_block': 1400100, 
    'address': '0x398eC7346DcD622eDc5ae82352F02bE94C62d119', # ERC20, compound
    #'topics': ['0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'] # Transfer
    })



logs = w3.eth.get_logs({
    'from_block': 1000000, 
    'to_block': 1600100, 
    'address': '0xE6C78983b07a07e0523b57E18AA23d3Ae2519E05', # Uniswap
    })

logs = w3.eth.get_logs({
    'from_block': 1, 
    'to_block': 1600100, 
    'address': '0xdAC17F958D2ee523a2206206994597C13D831ec7', # USDT
    'topics': ['0xcb8241adb0c3fdb35b70c24ce35c5eb0c17af7431c99f827d44a445ca624176a'] #
    })

