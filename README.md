
# Backup Telegram with bot token

This is a Telegram bot designed to back up messages and media files from Telegram chats to a local file system and a SQLite database. It handles various types of media including photos, videos, documents, voice messages, and more.

## Features

- Backups text messages and various media types (photos, videos, documents, etc.)
- Stores message details and media file paths in a SQLite database
- Asynchronously downloads media files to a specified directory
- Configurable via environment variables

## Requirements

- Python 3.7 or later
- Dependencies specified in `requirements.txt`

## Setup

### 1. Clone the Repository

### 2. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Create a `.env` File

Create a `.env` file in the project root with the following content:

```
BOT_TOKEN=your_telegram_bot_token
DATABASE_URL=sqlite:///telegram_backup.db
MEDIA_BACKUP_DIR=telegram_media_backup
```

Replace `your_telegram_bot_token` with your actual Telegram bot token. The `DATABASE_URL` specifies the SQLite database file location (you can change this if you use a different database). `MEDIA_BACKUP_DIR` is the directory where media files will be stored.

### 5. Run the Bot

```bash
python bot.py
```

The bot will start polling for new messages and will back up messages and media to the specified directory and database.

## Code Overview

- **`bot.py`**: Main bot logic, including message handling and media backup.
- **`requirements.txt`**: Python package dependencies.
- **`.env`**: Configuration file for environment variables.
- **`telegram_backup_bot.log`**: Log file for bot activities and errors.

## Logging

The bot logs information and errors to `telegram_backup_bot.log`. Make sure this file is writable and check it for troubleshooting.

## Contributing

Feel free to submit issues or pull requests. Contributions are welcome!

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
