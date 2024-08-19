import os
import logging
from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import aiohttp
import asyncio

# Load environment variables from a .env file
load_dotenv()

# Configuration from environment variables
BOT_TOKEN = os.getenv('BOT_TOKEN')
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///telegram_backup.db')
MEDIA_BACKUP_DIR = os.getenv('MEDIA_BACKUP_DIR', 'telegram_media_backup')

# Validate configuration
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN must be set in the .env file")

# Setup logging
logging.basicConfig(filename='telegram_backup_bot.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Setup database
engine = create_engine(DATABASE_URL, echo=False)
Base = declarative_base()

class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer)
    user_id = Column(Integer)
    username = Column(String, nullable=True)
    full_name = Column(String, nullable=True)
    text = Column(Text, nullable=True)
    date = Column(DateTime)
    message_id = Column(Integer, unique=True)
    reply_to_message_id = Column(Integer, nullable=True)
    chat_type = Column(String, nullable=True)
    is_group = Column(Boolean, default=False)

class Media(Base):
    __tablename__ = 'media'
    id = Column(Integer, primary_key=True)
    message_id = Column(Integer)
    media_type = Column(String)
    file_name = Column(String)
    file_path = Column(String)

# Create database tables
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

# Ensure media backup directory exists
os.makedirs(MEDIA_BACKUP_DIR, exist_ok=True)

# Asynchronous file download
async def download_media_file(session, url, file_path):
    try:
        async with session.get(url) as response:
            response.raise_for_status()  # Check for HTTP errors
            with open(file_path, 'wb') as f:
                while True:
                    chunk = await response.content.read(1024)
                    if not chunk:
                        break
                    f.write(chunk)
        return file_path
    except Exception as e:
        logger.error(f"Failed to download file from {url}: {e}")
        return None

# Backup function
async def backup_message(update: Update, context: CallbackContext) -> None:
    try:
        message = update.message
        chat_id = message.chat_id
        user_id = message.from_user.id
        username = message.from_user.username
        full_name = message.from_user.full_name
        text = message.text
        date = message.date
        message_id = message.message_id
        reply_to_message_id = message.reply_to_message.message_id if message.reply_to_message else None
        chat_type = message.chat.type
        is_group = chat_type in ['group', 'supergroup']

        # Save message to database
        with Session() as session:
            db_message = Message(
                chat_id=chat_id,
                user_id=user_id,
                username=username,
                full_name=full_name,
                text=text,
                date=date,
                message_id=message_id,
                reply_to_message_id=reply_to_message_id,
                chat_type=chat_type,
                is_group=is_group
            )
            session.add(db_message)

            # Handle media files
            media_file = None
            media_type = None
            if message.photo:
                media_file = await message.photo[-1].get_file()
                media_type = 'photo'
            elif message.video:
                media_file = await message.video.get_file()
                media_type = 'video'
            elif message.document:
                media_file = await message.document.get_file()
                media_type = 'document'
            elif message.voice:
                media_file = await message.voice.get_file()
                media_type = 'voice'
            elif message.audio:
                media_file = await message.audio.get_file()
                media_type = 'audio'
            elif message.animation:
                media_file = await message.animation.get_file()
                media_type = 'animation'
            elif message.sticker:
                media_file = await message.sticker.get_file()
                media_type = 'sticker'

            if media_file:
                file_name = f'{message_id}_{media_file.file_id}'
                file_path = os.path.join(MEDIA_BACKUP_DIR, file_name)
                # Download media file asynchronously
                file_url = media_file.file_path
                async with aiohttp.ClientSession() as session:
                    downloaded_path = await download_media_file(session, file_url, file_path)

                if downloaded_path:
                    db_media = Media(
                        message_id=message_id,
                        media_type=media_type,
                        file_name=file_name,
                        file_path=downloaded_path
                    )
                    session.add(db_media)

            session.commit()

    except Exception as e:
        logger.error(f"Error while processing message: {e}")

# Setup and run bot
async def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(MessageHandler(Filters.text | Filters.photo | Filters.video | Filters.document | Filters.voice | Filters.audio | Filters.animation | Filters.sticker, backup_message))

    # Start polling
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    asyncio.run(main())