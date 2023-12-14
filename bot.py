from modules import data_handler
import logging
import os
import matplotlib.pyplot as plt


from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

with open('data/token.txt', 'r') as file:
    # Read a single line from the file
    token = file.readline()
# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    data_handler.create_user_file(user.id)
    await update.message.reply_text("Этот бот помогает избавиться от плохой привычки. \n\n"
                                    "Каждый раз, когда вы делаете что-то, чего не хотите делать: "
                                    "например, выкуриваете сигарету или съедаете булочку, нажимайте команду /add. \n\n"
                                    "Бот будет записывать эту информацию, а также писать, сколько раз вы это уже "
                                    "сделали за сегодня. Когда проходит день, бот финализирует статистику, "
                                    "и вы можете получить её в виде календаря, выполнив комамнду /stats. \n\n"
                                    "Бот не позволяет отслеживать несколько привычек одновременно, потому "
                                    "что автор считает, что лучше бороться с одной привычкой за раз. "
                                    "Если вы хотите переиспользовать бота для другой привычки, просто нажмите "
                                    "/clear, и ваши данные очистятся. Если вы хотите посмотреть пример календаря, "
                                    "нажмите /demo \n\n")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Этот бот позволяет избавиться от плохой привычки. "
                                    "Каждый раз, когда вы делаете что-то, чего не хотите делать: "
                                    "например, выкуриваете сигарету или съедаете булочку, нажимайте команду /add. "
                                    "Бот будет записывать эту информацию, а также писать, сколько раз вы это уже "
                                    "сделали за сегодня. Когда проходит день, бот финализирует статистику, "
                                    "и вы можете получить её в виде календаря, выполнив комамнду /stats- "
                                    "Бот не позволяет отслеживать несколько привычек одновременно, потому "
                                    "что автор считает, что лучше бороться с одной привычкой за раз. "
                                    "Если вы хотите переиспользовать бота для другой привычки, просто нажмите "
                                    "/clear, и ваши данные очистятся. Если вы хотите посмотреть пример календаря, "
                                    "нажмите /demo ")


#async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#    """Echo the user message."""
#    await update.message.reply_text(update.message.text)

async def add_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    id = update.effective_user.id
    n = data_handler.update_or_create_entry(id)
    await update.message.reply_text(f"Добавили. За сегодня это {n}-е проявление"
                                    f" вашей вредной привычки. Не ругайте себя, скоро будет лучше!")

async def demo_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a heatmap image when the command /stats is issued."""
    user_id = "demo"
    n = data_handler.update_or_create_entry(id)
    # print("stats_command")
    # Generate the heatmap
    #fig = data_handler.create_heatmap(user_id)
    fig, num_entries, max_val, min_val, avg_val, num_zeros = data_handler.create_heatmap(user_id)

    txt = (f"Это статистика демо-пользователя за {num_entries} дней. За это время результаты таковы: \n"
           f"Максимальное потребление: {max_val} \n"
           f"Минимальное потребление: {min_val} \n"
           f"Среднее потребление: {avg_val} \n"
           f"Полных дней отказа от привычки: {num_zeros} \n")
    # Save the heatmap as an image file
    temp_image_path = f"temp_{user_id}.png"
    fig.savefig(temp_image_path)

    # Close the figure to release memory
    plt.close(fig)

    # Send the image file
    with open(temp_image_path, 'rb') as image_file:
        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=image_file)
    await update.message.reply_text(txt)
    # Optionally, remove the image file after sending
    os.remove(temp_image_path)


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a heatmap image when the command /stats is issued."""
    user_id = update.effective_user.id
    data_handler.update_or_create_entry(user_id, 0)
    # Generate the heatmap
    #fig = data_handler.create_heatmap(user_id)
    fig, num_entries, max_val, min_val, avg_val, num_zeros = data_handler.create_heatmap(user_id)
    if fig == None:
        await update.message.reply_text("У вас пока что нет статистики. Нажмите /start, чтобы создать новую привычку"
                                        ", и нажимайте /add, когда добавили привычку.")
    else:
        txt = (f"Мы ведём вашу статистику за {num_entries} дней. За это время результаты таковы: \n"
               f"Максимальное потребление: {max_val} \n"
               f"Минимальное потребление: {min_val} \n"
               f"Среднее потребление: {avg_val} \n"
               f"Полных дней отказа от привычки: {num_zeros} \n")

        # Save the heatmap as an image file
        temp_image_path = f"temp_{user_id}.png"
        fig.savefig(temp_image_path)

        # Close the figure to release memory
        plt.close(fig)

        # Send the image file
        if (num_entries >= 7):
            with open(temp_image_path, 'rb') as image_file:
                await context.bot.send_photo(chat_id=update.effective_chat.id, photo=image_file)
        else:
            txt += ("\n Мы не присылаем график в течение первых 7 дней использования бота, чтобы собрать данные. "
                    "Если вы хотите посмотреть пример графика, используйте функцию /demo")
        await update.message.reply_text(txt)

        # Optionally, remove the image file after sending
        os.remove(temp_image_path)

async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Воу-воу-воу! Вы действительно хотите удалить свои данные? Если это так, напишите нам:"
                                    " фразу: Я подтверждаю удаление данных\n"
                                    "``` Я подтверждаю удаление данных```",  parse_mode= "MARKDOWN")

async def delete_data (update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if "Я подтверждаю удаление данных" in update.message.text:
        user_id = update.effective_user.id
        data_handler.remove_user_data(user_id)
        await update.message.reply_text("все объекты класса кетер\n"
                                        "подросли на целый метер\n"
                                        "и какой сейчас длины?\n"
                                        ""
                                        "ДАННЫЕ УДАЛЕНЫ"
                                        "\n \n"
                                        "Поздравляем, теперь мы ничего не знаем о вашей старой привычке, а вы можете начать избавляться от новой!")
def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(token).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("add", add_command))
    application.add_handler(CommandHandler("demo", demo_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("clear", clear_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, delete_data))
    # on non command i.e message - echo the message on Telegram
    #application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()