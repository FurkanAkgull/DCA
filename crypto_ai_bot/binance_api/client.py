from binance.client import Client
import yaml

def load_config():
    with open("config.yaml", "r") as f:
        return yaml.safe_load(f)

def get_client():
    config = load_config()
    api_key = config["binance"]["api_key"]
    api_secret = config["binance"]["api_secret"]
    return Client(api_key, api_secret)
