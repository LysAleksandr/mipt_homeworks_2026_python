import sys
from config_loader import load_config
from chat import Chat

def main() -> None:
    config = load_config()
    if not config:
        print('No configuration found. Set environment variables or create config.yaml')
        sys.exit(1)
    chat = Chat(config)
    chat.run()

if __name__ == '__main__':
    main()