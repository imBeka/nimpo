import threading
from api import start_flask_server
from bot import start_telegram_bot

if __name__ == '__main__':
    flask_thread = threading.Thread(target=start_flask_server)
    bot_thread = threading.Thread(target=start_telegram_bot)

    flask_thread.start()
    bot_thread.start()

    flask_thread.join()
    bot_thread.join()
