import telebot
from telebot import types

# Bot tokeningizni kiriting
TOKEN = '6659893832:AAE7YVtOuGnTH_QhmB0D-TMn020kX7D1jxo'
# Admin ID sini kiriting (o'zingizning Telegram ID)
ADMIN_ID = 1063577925  # Bu yerga o'z ID ingizni qo'ying

bot = telebot.TeleBot(TOKEN)

# Foydalanuvchi ma'lumotlarini saqlash
user_data = {}

# BO'LIMLAR VA MAHSULOTLAR MA'LUMOTLARI
# Bu yerga o'z mahsulotlaringizni qo'shing
CATEGORIES = {
    '🍕 Taomlar': {
        'Pizza': {
            'photo': 'https://example.com/pizza.jpg',  # Yoki file_id
            'description': 'Ajoyib italyan pitsasi\nNarxi: 50,000 so\'m',
            'price': '50,000'
        },
        'Lavash': {
            'photo': 'https://example.com/lavash.jpg',
            'description': 'Mazali lavash\nNarxi: 25,000 so\'m',
            'price': '25,000'
        }
    },
    '🥤 Ichimliklar': {
        'Coca Cola': {
            'photo': 'https://example.com/cola.jpg',
            'description': 'Sovuq Coca Cola 1L\nNarxi: 10,000 so\'m',
            'price': '10,000'
        },
        'Choy': {
            'photo': 'https://example.com/tea.jpg',
            'description': 'Issiq choy\nNarxi: 5,000 so\'m',
            'price': '5,000'
        }
    },
    '🍰 Shirinliklar': {
        'Tort': {
            'photo': 'https://example.com/cake.jpg',
            'description': 'Shokoladli tort\nNarxi: 80,000 so\'m',
            'price': '80,000'
        }
    }
}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_data[message.chat.id] = {}
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = [types.KeyboardButton(cat) for cat in CATEGORIES.keys()]
    markup.add(*buttons)
    
    bot.send_message(
        message.chat.id,
        f"Assalomu aleykum, {message.from_user.first_name}! 👋\n\n"
        "Xush kelibsiz! Bo'limni tanlang:",
        reply_markup=markup
    )

@bot.message_handler(func=lambda message: message.text in CATEGORIES.keys())
def show_category(message):
    category = message.text
    user_data[message.chat.id]['category'] = category
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    products = list(CATEGORIES[category].keys())
    buttons = [types.KeyboardButton(prod) for prod in products]
    buttons.append(types.KeyboardButton('🔙 Orqaga'))
    markup.add(*buttons)
    
    bot.send_message(
        message.chat.id,
        f"{category} bo'limidan tanlang:",
        reply_markup=markup
    )

@bot.message_handler(func=lambda message: message.text == '🔙 Orqaga')
def go_back(message):
    send_welcome(message)

@bot.message_handler(func=lambda message: message.text == '📞 Telefon raqamni yuborish')
def request_phone(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button = types.KeyboardButton('📱 Raqamni yuborish', request_contact=True)
    markup.add(button)
    
    bot.send_message(
        message.chat.id,
        "Iltimos, telefon raqamingizni yuboring:",
        reply_markup=markup
    )

@bot.message_handler(content_types=['contact'])
def handle_contact(message):
    phone = message.contact.phone_number
    user_data[message.chat.id]['phone'] = phone
    
    # Buyurtmani adminga yuborish
    product_name = user_data[message.chat.id].get('product', 'Noma\'lum')
    category = user_data[message.chat.id].get('category', 'Noma\'lum')
    user_name = message.from_user.first_name
    username = f"@{message.from_user.username}" if message.from_user.username else "Username yo'q"
    
    admin_message = f"""
🔔 YANGI BUYURTMA!

👤 Mijoz: {user_name} ({username})
📞 Telefon: {phone}
📂 Bo'lim: {category}
🛍 Mahsulot: {product_name}

Mijoz bilan bog'laning!
"""
    
    try:
        bot.send_message(ADMIN_ID, admin_message)
        
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton('🏠 Bosh menyu'))
        
        bot.send_message(
            message.chat.id,
            "✅ Buyurtmangiz qabul qilindi!\n\n"
            "Tez orada admin siz bilan bog'lanadi.",
            reply_markup=markup
        )
    except:
        bot.send_message(
            message.chat.id,
            "❌ Xatolik yuz berdi. Iltimos qaytadan urinib ko'ring."
        )

@bot.message_handler(func=lambda message: message.text == '🏠 Bosh menyu')
def main_menu(message):
    send_welcome(message)

@bot.message_handler(func=lambda message: True)
def handle_product(message):
    chat_id = message.chat.id
    product_name = message.text
    
    # Mahsulotni topish
    if chat_id in user_data and 'category' in user_data[chat_id]:
        category = user_data[chat_id]['category']
        
        if product_name in CATEGORIES[category]:
            product = CATEGORIES[category][product_name]
            user_data[chat_id]['product'] = product_name
            
            # Inline tugmalar
            markup = types.InlineKeyboardMarkup(row_width=1)
            order_btn = types.InlineKeyboardButton('🛒 Buyurtma berish', callback_data=f'order_{product_name}')
            markup.add(order_btn)
            
            # Rasmni yuborish
            try:
                bot.send_photo(
                    chat_id,
                    product['photo'],
                    caption=f"📦 {product_name}\n\n{product['description']}",
                    reply_markup=markup
                )
            except:
                # Agar rasm yuborilmasa, matn yuboriladi
                bot.send_message(
                    chat_id,
                    f"📦 {product_name}\n\n{product['description']}",
                    reply_markup=markup
                )

@bot.callback_query_handler(func=lambda call: call.data.startswith('order_'))
def process_order(call):
    product_name = call.data.replace('order_', '')
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton('📞 Telefon raqamni yuborish'))
    
    bot.send_message(
        call.message.chat.id,
        f"Siz {product_name} buyurtma qildingiz.\n\n"
        "Buyurtmani tasdiqlash uchun telefon raqamingizni yuboring:",
        reply_markup=markup
    )
    bot.answer_callback_query(call.id)

# Botni ishga tushirish
print("Bot ishga tushdi...")
bot.polling(none_stop=True)
