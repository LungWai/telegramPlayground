from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler

# Replace 'YOUR_API_TOKEN' with your actual bot token
API_TOKEN = '7707713222:AAFe67WL_wbx-ci6wEWf3DX4poDUA2oPCdA'

# States for the conversation
ASK_BUTTON_COUNT, ASK_BUTTON_TEXT, ASK_BUTTON_URL, CONFIRM = range(4)

# Global variables to store button details
button_count = 0
buttons = []
current_button = 0

def start(update, context):
    update.message.reply_text('How many buttons do you want to create?')
    return ASK_BUTTON_COUNT

def ask_button_text(update, context):
    global button_count
    button_count = int(update.message.text)
    context.user_data['buttons'] = []
    update.message.reply_text(f'Please provide the text for button:')
    return ASK_BUTTON_TEXT

def ask_button_url(update, context):
    button_text = update.message.text
    context.user_data['buttons'].append({'text': button_text})
    update.message.reply_text(f'Please provide the URL for button:')
    return ASK_BUTTON_URL

def next_button(update, context):
    button_url = update.message.text
    context.user_data['buttons'][-1]['url'] = button_url
    current_button = len(context.user_data['buttons'])
    
    if current_button < button_count:
        update.message.reply_text(f'Please provide the text for button {current_button + 1}:')
        return ASK_BUTTON_TEXT
    else:
        button_texts = [f"Button {i+1}: {btn['text']} - {btn['url']}" for i, btn in enumerate(context.user_data['buttons'])]
        update.message.reply_text('You have created the following buttons:\n' + '\n'.join(button_texts) + '\n\nDo you want to send this message? (yes/no)')
        return CONFIRM

def confirm(update, context):
    if update.message.text.lower() == 'yes':
        keyboard = [[InlineKeyboardButton(btn['text'], url=btn['url'])] for btn in context.user_data['buttons']]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text('Z girl 是日菜單:', reply_markup=reply_markup)
    else:
        update.message.reply_text('Operation cancelled.')
    return ConversationHandler.END

def cancel(update, context):
    update.message.reply_text('Operation cancelled.')
    return ConversationHandler.END

def main():
    updater = Updater(API_TOKEN, use_context=True)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            ASK_BUTTON_COUNT: [MessageHandler(Filters.text & ~Filters.command, ask_button_text)],
            ASK_BUTTON_TEXT: [MessageHandler(Filters.text & ~Filters.command, ask_button_url)],
            ASK_BUTTON_URL: [MessageHandler(Filters.text & ~Filters.command, next_button)],
            CONFIRM: [MessageHandler(Filters.text & ~Filters.command, confirm)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
