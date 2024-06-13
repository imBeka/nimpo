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

def createOperatorsMarkup(operators):
    operatorsMarkup = types.InlineKeyboardMarkup(row_width=1)
    for operator in operators:
        operatorTmp = types.InlineKeyboardButton(f'@{operator}', callback_data=f"__operator__{operator}")
        operatorsMarkup.add(operatorTmp)
    
    addOperatorBtn = types.InlineKeyboardButton("Add operator", callback_data="__add__")
    backBtn = types.InlineKeyboardButton("Back", callback_data="__back__menu__")
    operatorsMarkup.add(addOperatorBtn, backBtn)

    return operatorsMarkup

def createManageOperatorMarkup(operator):
    mngOperatorMarkup = types.InlineKeyboardMarkup(row_width=1)

    delOperator = types.InlineKeyboardButton("Remove", callback_data=f"__remove__{operator}")
    backBtn = types.InlineKeyboardButton("Back", callback_data="__back__operators__")

    mngOperatorMarkup.add(delOperator, backBtn)

    return mngOperatorMarkup
