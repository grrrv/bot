import pandas as pd
import mysql.connector

# Подключение к MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1234"
)
cursor = conn.cursor()

# Создание БД
cursor.execute("DROP DATABASE IF EXISTS university_schedule")
cursor.execute("CREATE DATABASE university_schedule")
cursor.execute("USE university_schedule")

# Таблицы
table_queries = ["""
    CREATE TABLE student_groups (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
    )""",
    """
    CREATE TABLE days (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(20) NOT NULL UNIQUE
    )
    """,
    """
    CREATE TABLE time_slots (
        id INT AUTO_INCREMENT PRIMARY KEY,
        start_end_time VARCHAR(20) NOT NULL UNIQUE
    )
    """,
    """
    CREATE TABLE subjects (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100) NOT NULL UNIQUE
    )
    """,
    """
    CREATE TABLE teachers (
        id INT AUTO_INCREMENT PRIMARY KEY,
        full_name VARCHAR(100) UNIQUE
    )
    """,
    """
    CREATE TABLE class_types (
        id INT AUTO_INCREMENT PRIMARY KEY,
        type_info VARCHAR(100)
    )
    """,
    """
    CREATE TABLE locations (
        id INT AUTO_INCREMENT PRIMARY KEY,
        location_info VARCHAR(100)
    )
    """,
    """
    CREATE TABLE schedule (
        id INT AUTO_INCREMENT PRIMARY KEY,
        group_id INT,
        day_id INT,
        time_slot_id INT,
        subject_id INT,
        teacher_id INT,
        class_type_id INT,
        location_id INT,
        FOREIGN KEY (group_id) REFERENCES student_groups(id),
        FOREIGN KEY (day_id) REFERENCES days(id),
        FOREIGN KEY (time_slot_id) REFERENCES time_slots(id),
        FOREIGN KEY (subject_id) REFERENCES subjects(id),
        FOREIGN KEY (teacher_id) REFERENCES teachers(id),
        FOREIGN KEY (class_type_id) REFERENCES class_types(id),
        FOREIGN KEY (location_id) REFERENCES locations(id)
    )
    """
]

for query in table_queries:
    cursor.execute(query)

# Загрузка Excel


# Хелп-функция для вставки с возвратом id
def get_or_insert(table, column, value):
    if pd.isna(value): return None
    cursor.execute(f"SELECT id FROM {table} WHERE {column} = %s", (value,))
    result = cursor.fetchone()
    if result:
        return result[0]
    cursor.execute(f"INSERT INTO {table} ({column}) VALUES (%s)", (value,))
    conn.commit()
    return cursor.lastrowid

# Заполнение таблиц и расписания

df = pd.read_excel("4 курс Пи4.xlsx", sheet_name=0)
df.columns = [col.replace('\n', ' ').strip() for col in df.columns]
print(df.columns.tolist())  # ← временно добавь для отладки

# Удалим пустые строки
#df = df.dropna(subset=["Дата, день недели", "Время", "Наименование дисциплины"])

# Удалим пробелы и \n
df.columns = [col.replace('\n', ' ').strip() for col in df.columns]
df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
for _, row in df.iterrows():
    group_id = get_or_insert("student_groups", "name", row["Группа"])
    day_id = get_or_insert("days", "name", row["Дата, день недели"])
    time_id = get_or_insert("time_slots", "start_end_time", row["Время"])
    subj_id = get_or_insert("subjects", "name", row["Наименование дисциплины"])
    teacher_id = get_or_insert("teachers", "full_name", row["Преподаватель"])
    class_type_id = get_or_insert("class_types", "type_info", row["Вид учебных занятий"])
    location_id = get_or_insert("locations", "location_info", row["Место проведения"])

    # Вставка в расписание
    cursor.execute("""
    INSERT INTO schedule (group_id, day_id, time_slot_id, subject_id, teacher_id, class_type_id, location_id)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (group_id, day_id, time_id, subj_id, teacher_id, class_type_id, location_id))


print(df.columns)
conn.commit()
cursor.close()
conn.close()
print("База данных успешно создана и заполнена!")
