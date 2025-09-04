from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from data import load_events, load_sorted_events

#початкова клавiатура
main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="/new_event")],
    [KeyboardButton(text="/all_events")],
    [KeyboardButton(text="/delete_event")],
    [KeyboardButton(text="/sorted_events")],
    [KeyboardButton(text="/edit_event")],
], 
resize_keyboard=True, input_field_placeholder="Choose the button..."
)

#Вивiд Iвентiв
def events_keyboard(prefix: str = "event:"):
    builder = InlineKeyboardBuilder()
    events = load_sorted_events()
    if not events:
        builder.add(
            InlineKeyboardButton(text="No events", callback_data="no_events"))
    else:
        for ev in events:
            name = ev.get("name", "Without a name")
            builder.add(
                InlineKeyboardButton(
                    text=name,
                    callback_data=f"{prefix}{name}"))
    builder.adjust(1) 
    return builder.as_markup()


#Клавiатура для видалення
def delete_keyboard():
    events = load_events()
    if not events:
        return None
    buttons = []
    for e in events:
        buttons.append([InlineKeyboardButton(text=f"❌ {e['name']}", callback_data=f"delete:{e['name']}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


#Клавiатура для вiдсортованих iвентiв
def sorted_events_keyboard():
    builder = InlineKeyboardBuilder()
    events = load_sorted_events()

    if not events:
        builder.add(InlineKeyboardButton(text="No events", callback_data="no_events"))
    else:
        for ev in events:
            name = ev.get("name", "Without a name")
            builder.add(
                InlineKeyboardButton(
                    text=name,
                    callback_data=f"event:{name}"
                )
            )
    builder.adjust(1)
    return builder.as_markup()