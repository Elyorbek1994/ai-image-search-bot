import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from icrawler.builtin import BingImageCrawler

# Loglarni terminalda ko'rish
logging.basicConfig(level=logging.INFO)

API_TOKEN = '8937913725:AAE2blcJBgLOpiunNqK1hDdwiW25DF3LK9M'

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer(
        "🤖 **Salom! Men Kuchli Rasm Qidiruv botiman.**\n\n"
        "Menga xohlagan so'zingizni yozib yuboring (masalan: `Minecraft`, `Real Madrid`), "
        "men esa sizga unga tegishli 3 ta rasmlarni albom qilib topib beraman! 🤩"
    )

@dp.message()
async def search_and_send_images(message: types.Message):
    status_message = await message.answer("🔎 Rasmlar qidirilmoqda, iltimos kuting...")
    
    # Har bir foydalanuvchi uchun alohida vaqtinchalik papka
    folder_name = f"downloads_{message.from_user.id}_{message.message_id}"
    
    try:
        # Bing tizimidan barqaror qidirish (Maksimal 3 ta rasm)
        bing_crawler = BingImageCrawler(storage={'root_dir': folder_name})
        bing_crawler.crawl(keyword=message.text, max_num=3)
        
        # Papka ichidagi barcha yuklangan rasmlarni tekshiramiz
        if os.path.exists(folder_name):
            files = [f for f in os.listdir(folder_name) if os.path.isfile(os.path.join(folder_name, f))]
        else:
            files = []
            
        if files:
            media_group = []
            opened_files = []
            
            # Rasmlarni albom holatiga keltiramiz
            for index, file in enumerate(files):
                file_path = os.path.join(folder_name, file)
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                    f = open(file_path, 'rb')
                    opened_files.append(f)
                    
                    # Faqat birinchi rasmga sarlavha qo'shamiz
                    caption = f"✨ `{message.text}` bo'yicha topilgan rasmlar" if index == 0 else None
                    media_group.append(types.InputMediaPhoto(
                        media=types.BufferedInputFile(f.read(), filename=file), 
                        caption=caption
                    ))
            
            if media_group:
                # Albomni bittada yuborish
                await message.answer_media_group(media=media_group)
                await status_message.delete()
            else:
                await status_message.edit_text("❌ Yaroqli rasm formati topilmadi.")
                
            # Ochiq fayllarni yopish
            for f in opened_files:
                f.close()
                
            # Fayllarni va papkani o'chirish
            for file in os.listdir(folder_name):
                os.remove(os.path.join(folder_name, file))
            os.rmdir(folder_name)
            
        else:
            await status_message.edit_text("❌ Afsuski, ushbu so'z bo'yicha rasm topilmadi.")
            if os.path.exists(folder_name):
                os.rmdir(folder_name)
                
    except Exception as e:
        logging.error(f"Xatolik: {e}")
        await status_message.edit_text("⚠️ Rasmlarni yuklashda xatolik yuz berdi.")
        if os.path.exists(folder_name):
            for file in os.listdir(folder_name):
                try: os.remove(os.path.join(folder_name, file))
                except: pass
            try: os.rmdir(folder_name)
            except: pass

async def main():
    logging.info("Bot muvaffaqiyatli ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())