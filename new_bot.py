import logging
import mysql.connector
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# Подключение к базе
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",
        database="university_schedule"
    )

# Получить расписание по преподавателю на день
def get_schedule_by_teacher_day(teacher_name, day_name):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT g.name AS student_groups, d.name AS day, t.start_end_time AS time, s.name AS subject, c.type_info AS class_type, l.location_info AS location
        FROM schedule sch
        JOIN student_groups g ON sch.group_id = g.id
        JOIN days d ON sch.day_id = d.id
        JOIN time_slots t ON sch.time_slot_id = t.id
        JOIN subjects s ON sch.subject_id = s.id
        JOIN teachers te ON sch.teacher_id = te.id
        JOIN class_types c ON sch.class_type_id = c.id
        JOIN locations l ON sch.location_id = l.id
        WHERE te.full_name = %s AND d.name = %s
        ORDER BY t.start_end_time
    """
    cursor.execute(query, (teacher_name, day_name))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def get_schedule_by_group_week(group_name):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT d.name AS day, t.start_end_time AS time, s.name AS subject, te.full_name AS teacher, c.type_info AS class_type, l.location_info AS location
        FROM schedule sch
        JOIN student_groups g ON sch.group_id = g.id
        JOIN days d ON sch.day_id = d.id
        JOIN time_slots t ON sch.time_slot_id = t.id
        JOIN subjects s ON sch.subject_id = s.id
        JOIN teachers te ON sch.teacher_id = te.id
        JOIN class_types c ON sch.class_type_id = c.id
        JOIN locations l ON sch.location_id = l.id
        WHERE g.name = %s
        ORDER BY d.id, t.start_end_time
    """
    cursor.execute(query, (group_name,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def get_schedule_by_group_day(group_name, day_name):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT d.name AS day, t.start_end_time AS time, s.name AS subject, te.full_name AS teacher, c.type_info AS class_type, l.location_info AS location
        FROM schedule sch
        JOIN student_groups g ON sch.group_id = g.id
        JOIN days d ON sch.day_id = d.id
        JOIN time_slots t ON sch.time_slot_id = t.id
        JOIN subjects s ON sch.subject_id = s.id
        JOIN teachers te ON sch.teacher_id = te.id
        JOIN class_types c ON sch.class_type_id = c.id
        JOIN locations l ON sch.location_id = l.id
        WHERE g.name = %s AND d.name = %s
        ORDER BY d.id, t.start_end_time
    """
    cursor.execute(query, (group_name,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows
# Получить расписание на всю неделю
def get_schedule_by_teacher_week(teacher_name):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT g.name AS student_group, d.name AS day, t.start_end_time AS time, s.name AS subject, c.type_info AS class_type, l.location_info AS location
        FROM schedule sch
        JOIN student_groups g ON sch.group_id = g.id
        JOIN days d ON sch.day_id = d.id
        JOIN time_slots t ON sch.time_slot_id = t.id
        JOIN subjects s ON sch.subject_id = s.id
        JOIN teachers te ON sch.teacher_id = te.id
        JOIN class_types c ON sch.class_type_id = c.id
        JOIN locations l ON sch.location_id = l.id
        WHERE te.full_name = %s
        ORDER BY d.id, t.start_end_time
    """
    cursor.execute(query, (teacher_name,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def get_schedule_by_location(location_info):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT g.name AS student_group, d.name AS day, t.start_end_time AS time, s.name AS subject,
               c.type_info AS class_type, te.full_name AS teacher
        FROM schedule sch
        JOIN student_groups g ON sch.group_id = g.id
        JOIN days d ON sch.day_id = d.id
        JOIN time_slots t ON sch.time_slot_id = t.id
        JOIN subjects s ON sch.subject_id = s.id
        JOIN teachers te ON sch.teacher_id = te.id
        JOIN class_types c ON sch.class_type_id = c.id
        JOIN locations l ON sch.location_id = l.id
        WHERE l.location_info = %s
        ORDER BY d.id, t.start_end_time
    """
    cursor.execute(query, (location_info,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


# Команда /day
async def teacher_day_command(query, teacher, day):
    
    schedule = get_schedule_by_teacher_day(teacher, day)
    if not schedule:
        await query.message.reply_text("Нет занятий на этот день.")
        return

    text = f"📅 Расписание для {teacher} на {day}:\n\n"
    for row in schedule:
        text += f"{row['time']} — {row['subject']} ({row['class_type']}) в {row['location']}\n"
    await query.message.reply_text(text)

# Команда /week
async def teacher_week_command(update, teacher):
    
    schedule = get_schedule_by_teacher_week(teacher)
    if not schedule:
        await update.message.reply_text("Нет расписания на неделю.")
       
    text = f"📅 Расписание для {teacher} на неделю:\n\n"
    current_day = ""
    for row in schedule:
        if row['day'] != 'Воскресенье':
            current_day = row['day']
            text += f"\n🔸 {current_day}:\n"
        text += f"{row['time']} — {row['subject']} ({row['class_type']}) в {row['location'] } {row['student_group']} \n"
    await update.message.reply_text(text)

async def group_week_command(query, group):
    schedule = get_schedule_by_group_week(group)
    if not schedule:
        await query.message.reply_text("Нет расписания на неделю.")
        return

    text = f"📅 Расписание для {group} на неделю:\n\n"
    current_day = ""
    for row in schedule:
        if row['day'] != current_day:
            current_day = row['day']
            text += f"\n🔸 {current_day}:\n"
        text += f"{row['time']} — {row['subject']} {row['teacher']} ({row['class_type']}) в {row['location'] } \n"
    await query.message.reply_text(text)

async def group_day_command(query, group, day):
    schedule = get_schedule_by_group_day(group, day)
    if not schedule:
        await query.message.reply_text("Нет расписания на неделю.")
        return

    text = f"📅 Расписание для {group} на неделю:\n\n"
    current_day = ""
    for row in schedule:
        if row['day'] != current_day:
            current_day = row['day']
            text += f"\n🔸 {current_day}:\n"
        text += f"{row['time']} — {row['subject']} {row['teacher']} ({row['class_type']}) в {row['location'] } \n"
    await query.message.reply_text(text)

async def place_command(update, location):
    schedule = get_schedule_by_location(location)
    if not schedule:
        await update.message.reply_text("Нет занятий в этом месте.")
        return
    
    text = f"📍 Расписание для аудитории: {location}\n"
    current_day = ""
    for row in schedule:
        if row["day"] != current_day:
            current_day = row["day"]
            text += f"\n🔸 {current_day}:\n"
        text += f"{row['time']} — {row['subject']} ({row['class_type']}) — {row['teacher']} {row['student_group']}\n"
    await update.message.reply_text(text)


# Запуск бота
faculties = ["ФМФИ", "ФНО", "ФПСО", "ИФ", "ФКИ", "ФФ", "ФФКС", "ФИЯ", "ЕГФ", "ФЭУС"]  # список ваших факультетов
DAY_WEEK_CHOICE, DAY_SELECTION = range(2)

async def start(update: Update, context):
    """Обрабатывает стартовую команду"""
    keyboard = [
        [KeyboardButton('Группа')],
        [KeyboardButton('Преподаватель')],
        [KeyboardButton('Аудитория')]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=False, resize_keyboard=True)
    await update.message.reply_text('Выберете, для кого вы хотите получить расписание:', reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    choice = query.data
    if choice == 'group':
        await show_faculties(query)
    elif choice == 'teacher':
        await teacher_button_clicked(update, context)
    elif choice == 'room':
        await classroom_button_clicked(update, context)

async def show_faculties(query):
    faculties = ['ФМФИ', 'ЕГФ', 'ИФ', 'ФПСО', 'ФФ', 'ФФКС', 'ФКИ', 'ФНО', 'ФЭУС', 'ФИЯ']
    buttons = [[InlineKeyboardButton(faculty, callback_data=f'g_{faculty}')] for faculty in faculties]
    reply_markup = InlineKeyboardMarkup(buttons)
    await query.edit_message_text(text='Выберите факультет:', reply_markup=reply_markup)

async def select_group(query, faculty):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM student_groups WHERE name LIKE  %s", (f"{faculty}%",))
    rows = cursor.fetchall()
    groups = [row[0] for row in rows]
    
    buttons = [[InlineKeyboardButton(group, callback_data=f'schedule_{group}')] for group in groups]
    reply_markup = InlineKeyboardMarkup(buttons)
    await query.edit_message_text(text='Выберите группу:', reply_markup=reply_markup)

async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Команда не найдена. Используйте /help")

async def main_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Проверяем, была ли введена команда
    if update.message.entities and any(entity.type == 'bot_command' for entity in update.message.entities):
        await unknown_command(update, context)
async def group_button_clicked(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Формируем клавиатуру с кнопками факультетов
    keyboard = []
    row = []
    for i, faculty in enumerate(faculties):
        row.append(InlineKeyboardButton(faculty, callback_data=f'faculty_{faculty}'))
        if len(row) == 3 or i + 1 == len(faculties):  # добавляем максимум 3 кнопки в ряд
            keyboard.append(row)
            row = []
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Выберите факультет:', reply_markup=reply_markup)


async def group_select_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Реакция на выбор конкретной учебной группы"""
    query = update.callback_query
    await query.answer()
    selected_group = query.data.split('_')[1]
    await query.edit_message_text(text=f"Ваша группа: {selected_group}")
    await group_week_command(query, selected_group)

async def faculty_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    selected_faculty = query.data.split('_')[1]
    await query.edit_message_text(text=f'Вы выбрали {selected_faculty}.')
    await select_group(query, selected_faculty)
    

# Добавление функций для преподавателя и аудитории (должны быть реализованы самостоятельно)
async def teacher_button_clicked(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Введите имя преподавателя в формате Фамилия И.О.:', reply_markup=None)
    

async def teacher_sch_show(update, context):
    teacher = update.message.text
    await teacher_week_command(update, teacher)

async def classroom_button_clicked(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(text='Введите номер корпуса и аудитории в формате 100, корпус №1: ', reply_markup=None)
    


async def class_sch_show(update: Update, context):
    class_name  = update.message.text
    await place_command(update, class_name)

def main():
    TOKEN = "" 
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(faculty_selected, pattern='^faculty_'))
    app.add_handler(CallbackQueryHandler(group_select_callback, pattern='^schedule_'))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex('^Группа$'), group_button_clicked))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex('^Преподаватель$'), teacher_button_clicked))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex('^Аудитория$'), classroom_button_clicked))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND)&(~filters.Regex(r'\d'))&(~filters.Regex('ЭИОС СГСПУ')), teacher_sch_show))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), class_sch_show))
    app.add_handler(MessageHandler(filters.ALL, main_handler))
    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
