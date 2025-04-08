import logging

# Налаштування логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def media(message):
    if message.content_type == "photo":
        # Тут обробка фото
        # В photo кілька розмірів, беремо останню (найбільшу)
        photo = message.photo[-1]
        logger.info(f"Отримали фото з file_id={photo.file_id} від користувача {message.from_user.id}")
        await message.reply(
            f"Отримано фото!\n"
            f"Унікальний ідентифікатор: {photo.file_unique_id}\n"
            f"Розмір (байт): {photo.file_size}\n"
            f"Ширина: {photo.width}\n"
            f"Висота: {photo.height}"
        )
    elif message.content_type == "document":
        # Тут обробка документів (PDF тощо)
        doc = message.document
        logger.info(f"Отримали документ з file_id={doc.file_id} від користувача {message.from_user.id}")
        await message.reply(
            f"Отримано документ!\n"
            f"Назва файлу: {doc.file_name}\n"
            f"Унікальний ідентифікатор: {doc.file_unique_id}\n"
            f"Розмір (байт): {doc.file_size}\n"
            f"MIME-тип: {doc.mime_type}"
        )
    elif message.content_type == "audio":
        # Аудіо (формат mp3 тощо). Не плутати з voice (голосове повідомлення)!
        audio = message.audio
        await message.reply(
            f"Отримано аудіофайл!\n"
            f"Назва треку: {audio.title}\n"
            f"Виконавець: {audio.performer}\n"
            f"Тривалість (сек): {audio.duration}\n"
            f"Унікальний ID: {audio.file_unique_id}\n"
            f"Розмір (байт): {audio.file_size}"
        )
    elif message.content_type == "video":
        # Відеофайл (mp4 тощо). Не плутати з video_note (кружечок).
        vid = message.video
        await message.reply(
            f"Отримано відео!\n"
            f"Унікальний ID: {vid.file_unique_id}\n"
            f"Розмір (байт): {vid.file_size}\n"
            f"Ширина x Висота: {vid.width} x {vid.height}\n"
            f"Тривалість (сек): {vid.duration}"
        )
