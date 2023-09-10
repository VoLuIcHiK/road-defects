from fastapi import FastAPI, UploadFile, File
import sqlite3
import tempfile
import shutil


def db_init():
    # Создаем базу данных SQLite
    conn = sqlite3.connect(f"{temp_dir}/{db_filename}")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS ProcessingUnit"
                   "(id INTEGER PRIMARY KEY AUTOINCREMENT, fileInput TEXT, textOutput TEXT)")
    conn.commit()
    conn.close()

    # Создаем объект базы данных


# Создаем временную папку для сохранения загруженного файла
temp_dir = tempfile.mkdtemp()
db_filename = f"db.sqlite3"
db_init()
app = FastAPI()

# Функция для обработки загруженного файла
async def process_db3_file(file: UploadFile):
    # Сохраняем загруженный файл во временной папке
    with open(f"{temp_dir}/{file.filename}", "wb") as temp_file:
        shutil.copyfileobj(file.file, temp_file)

    # Подключаемся к базе данных SQLite и читаем текст
    conn = sqlite3.connect(f"{temp_dir}/{db_filename}")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ProcessingUnit")  # Замените 'your_table_name' на имя вашей таблицы
    data = cursor.fetchall()
    conn.close()

    # Преобразуем данные в текст
    text = "\n".join(" ".join(map(str, row)) for row in data)

    return text

@app.post("/upload/")
async def upload_db3_file(file: UploadFile):
    text = await process_db3_file(file)
    return {"text_from_db3": text}
