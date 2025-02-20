import json
import os
from eth_account import Account
from eth_account.hdaccount import generate_mnemonic

Account.enable_unaudited_hdwallet_features()


def generate_accountdddddd(num=50, default_name="auto_wallet.json"):
    wallet_path = os.path.join("wallet", default_name)
    if os.path.exists(wallet_path):
        raise FileExistsError("钱包文件已存在")
    wallets = []
    for i in range(num):
        mnemonic = generate_mnemonic(num_words=12, lang="english")
        name = f"AutoAccount{i}"
        account = Account.from_mnemonic(mnemonic)
        private_key = account._key_obj
        public_key = private_key.public_key
        address = public_key.to_checksum_address()
        wallet_info = dict(
            name=name,
            private_key=str(private_key),
            public_key=str(public_key),
            address=str(address),
            mnemonic=mnemonic,
        )
        wallets.append(wallet_info)
    with open(wallet_path, "w") as f:
        json.dump(wallets, f)


def evm_generate_account():
    seed = generate_mnemonic(num_words=12, lang="english")
    # logger.info(f"seed: {seed}")
    # account = Account.from_mnemonic(seed)
    # private_key = account._key_obj
    # logger.info(f"private_key: {private_key}")
    # public_key = private_key.public_key
    # logger.info(f"public_key: {public_key}")
    return seed


def generate_seed_12():
    return generate_mnemonic(num_words=12, lang="english")
