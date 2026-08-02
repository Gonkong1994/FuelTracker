import telebot
from storage import Session, FuelUpDB
from datetime import date
import matplotlib.pyplot as plt
import io

TOKEN = "8910430449:AAEf5yLqORYFtHpzLaXVBfzUkmOCKUEVbK0"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands = ['start'])
def start(message):
    bot.reply_to(message, "Привет! Я бот для учёта заправок.\nКоманды: /help")
    
@bot.message_handler(commands = ['help'])
def help(message):
    bot.reply_to(message, "/fuelups - последние 5 заправок\n/stats - общая статистикаn\n/add - добавить заправку\n /chart - график по заправкам\n/Today - Заправлено сегодня\n/plate - Поиск заправок по госномеру\n /summary - Сводка по машинам\n/undo - Удалить последнюю заправку")
    
@bot.message_handler(commands = ['fuelups'])
def fuelups(message):
    session = Session()
    fuelups = session.query(FuelUpDB).order_by(FuelUpDB.id.desc()).limit(5).all()
    session.close()
    
    if not fuelups:
        bot.reply_to(message, "Заправок пока нет")
        return
    
    text = "Последние заправки:\n\n"
    for f in fuelups:
        text += f"🚛 {f.car} ({f.plate_number})\n"
        text += f"⛽ {f.liters} л × {f.price_per_liter} руб = {f.liters * f.price_per_liter:.2f} руб\n"
        text += f"📅 {f.date}\n\n"
        
    bot.reply_to(message, text)
    
@bot.message_handler(commands = ['stats'])
def stats(message):
    session = Session()
    fuelups = session.query(FuelUpDB).all()
    session.close()
    
    total_liters = sum(f.liters for f in fuelups)
    total_spent = sum (f.liters * f.price_per_liter for f in fuelups)
    
    text = f"📊 Статистика:\n"
    text += f"Заправок: {len(fuelups)}\n"
    text += f"Всего литров: {total_liters:.1f}\n"
    text += f"Всего потрачено: {total_spent:.2f} руб"
    
    bot.reply_to(message, text)
    
@bot.message_handler(func=lambda message: not message.text.startswith('/'))
def add_by_text(message):
    args = message.text.split(',')
    
    if len(args) < 5:
        bot.reply_to(message, "Формат: /add Машина, литры, цена, пробег, госномер\nПример: /add Volvo, 500, 1.85, 150000, А123БВ177")
        return
    
    car = args[0].strip()
    liters = float(args[1].strip())
    price_per_liter = float(args[2].strip())
    kilometrs = int(args[3].strip())
    plate_number = args[4].strip()
    
    session = Session()
    db_fuelup = FuelUpDB(
        plate_number = plate_number,
        car = car,
        liters = liters,
        price_per_liter = price_per_liter,
        kilometrs = kilometrs,
        date = str(date.today())
    ) 
    session.add(db_fuelup)
    session.commit()
    session.close()
    bot.reply_to(message, f"✅ Заправка добавлена: {car}, {liters} л, {liters * price_per_liter:.2f} руб")
    
@bot. message_handler(commands = ["chart"])
def chart(message):
    session = Session()
    db_fuelups = session.query(FuelUpDB).order_by(FuelUpDB.id.asc()).all()
    session.close()
    
    if len(db_fuelups) < 2:
        bot.reply_to(message, "Недостаточно данных для графика (нужно минимум 2 заправки)")
        return
    
    labels = [f"#{f.id}" for f in db_fuelups]
    liters = [f.liters for f in db_fuelups]
    
    plt.figure(figsize=(10, 5))
    plt.bar(labels, liters, color='steelblue')
    plt.xlabel('Заправки')
    plt.ylabel('Литры')
    plt.title('Расход топлива по заправкам')
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    
    bot.send_photo(message.chat.id, buf)
    
@bot.message_handler(commands = ["Today"])
def by_today(message):
    today_str = str(date.today())
    session = Session()
    db_fuelups = session.query(FuelUpDB).filter(FuelUpDB.date == today_str).all()
    session.close()
    
    if not db_fuelups:
        bot.reply_to(message, f"Заправок за сегодня ({today_str}) нет")
        return
    
    total_liters = sum(f.liters for f in db_fuelups)
    total_spent = sum(f.liters * f.price_per_liter for f in db_fuelups)
    
    text = f"📅 Заправки за сегодня ({today_str}):\n\n"
    
    for f in db_fuelups:
        text += f"🚛 {f.car} ({f.plate_number}): {f.liters} л — {f.liters * f.price_per_liter:.2f} руб\n"
    text += f"\nВсего литров: {total_liters:.1f}\nВсего потрачено: {total_spent:.2f} руб"
    bot.reply_to(message, text)
    
@bot.message_handler(commands=['plate'])
def plate(message):
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "Формат: /plate А123БВ177")
        return
    
    plate = args[1]
    session = Session()
    fuelups = session.query(FuelUpDB).filter(FuelUpDB.plate_number == plate).all()
    session.close()
    
    if not fuelups:
        bot.reply_to(message, f"Заправок для {plate} не найдено")
        return
    
    total_liters = sum(f.liters for f in fuelups)
    total_spent = sum(f.liters * f.price_per_liter for f in fuelups)
    
    text = f"🚛 {plate}:\n\n"
    for f in fuelups:
        text += f"📅 {f.date}: {f.liters} л × {f.price_per_liter} = {f.liters * f.price_per_liter:.2f} руб\n"
    text += f"\nВсего: {len(fuelups)} заправок, {total_liters:.1f} л, {total_spent:.2f} руб"
    
    bot.reply_to(message, text)
    
@bot.message_handler(commands=['summary'])
def summary(message):
    session = Session()
    fuelups = session.query(FuelUpDB).order_by(FuelUpDB.date.desc()).all()
    session.close()
    
    if not fuelups:
        bot.reply_to(message, "Данных нет")
        return
    
    summary_dict = {}
    for f in fuelups:
        plate = f.plate_number
        if plate not in summary_dict:
            summary_dict[plate] = {"liters": 0, "spent": 0, "records": []}
        summary_dict[plate]["liters"] += f.liters
        summary_dict[plate]["spent"] += f.liters * f.price_per_liter
        summary_dict[plate]["records"].append(f"{f.date}: {f.liters} л × {f.price_per_liter} = {f.liters * f.price_per_liter:.2f} руб")
    
    text = "📊 Сводка по машинам:\n\n"
    for plate, data in summary_dict.items():
        text += f"🚛 {plate}:\n"
        text += f"   Всего заправок: {len(data['records'])}\n"
        text += f"   Литров: {data['liters']:.1f}\n"
        text += f"   Потрачено: {data['spent']:.2f} руб\n"
        text += f"   Заправки:\n"
        for record in data['records']:
            text += f"      📅 {record}\n"
        text += "\n"
    
    bot.reply_to(message, text)
    
@bot.message_handler(commands=['undo'])
def undo(message):
    session = Session()
    last = session.query(FuelUpDB).order_by(FuelUpDB.id.desc()).first()
    if last:
        plate_number = last.plate_number
        session.delete(last)
        session.commit()
        session.close()
        bot.reply_to(message, f"❌ Удалена заправка: {plate_number}")
    else:
        session.close()
        bot.reply_to(message, "Нечего удалять")
    
bot.polling()