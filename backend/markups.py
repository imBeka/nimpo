from telebot import types
import db

# main menu
setupBtn = types.InlineKeyboardButton('Setup Chat', callback_data='__setup__')
codeBtn = types.InlineKeyboardButton('Get Code', callback_data='__code__')
operatorsBtn = types.InlineKeyboardButton("Operators", callback_data='__operators__')

mainMenuMarkup = types.InlineKeyboardMarkup(row_width=2).add(setupBtn, operatorsBtn, codeBtn)

def createKeyboardMenu():
    menuBtn = types.InlineKeyboardButton('Menu', callback_data="__menu__")
    helpBtn = types.InlineKeyboardButton('Help', callback_data="__help__")
    keyboardMenu = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True).add(menuBtn, helpBtn)
    return keyboardMenu

def createOperatorsMarkup(chatId, operators):
    operatorsMarkup = types.InlineKeyboardMarkup(row_width=1)
    for operatorId in operators.keys():
        operatorTmp = types.InlineKeyboardButton(f'{operators[operatorId]["operator_name"]} (@{operators[operatorId]["operator_username"]})', callback_data=f"__operator__{operatorId}__{chatId}")
        operatorsMarkup.add(operatorTmp)
    
    addOperatorBtn = types.InlineKeyboardButton("Add operator", callback_data="__add__")
    backBtn = types.InlineKeyboardButton("Back", callback_data="__back__menu__")
    operatorsMarkup.add(addOperatorBtn, backBtn)

    return operatorsMarkup

def createManageOperatorMarkup(chatId, operator_id):
    mngOperatorMarkup = types.InlineKeyboardMarkup(row_width=1)

    delOperator = types.InlineKeyboardButton("Remove", callback_data=f"__remove__{operator_id}")
    editName = types.InlineKeyboardButton("Edit", callback_data=f"__edit__{operator_id}")
    backBtn = types.InlineKeyboardButton("Back", callback_data="__back__operators__")

    mngOperatorMarkup.add(delOperator, editName, backBtn)

    return mngOperatorMarkup
