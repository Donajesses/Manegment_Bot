from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from data import load_events, load_sorted_events


main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="/new_event")],
    [KeyboardButton(text="/all_events")],
    [KeyboardButton(text="/delete_event")]
], 
resize_keyboard=True, input_field_placeholder="Choose the button..."

)


def events_keyboard(prefix: str = "event:"):
    builder = InlineKeyboardBuilder()
    events = load_sorted_events()

    if not events:
        builder.add(
            InlineKeyboardButton(text="Нет событий", callback_data="no_events")
        )
    else:
        for ev in events:
            name = ev.get("name", "Без названия")
            builder.add(
                InlineKeyboardButton(
                    text=name,
                    callback_data=f"{prefix}{name}"   
                )
            )

    builder.adjust(1) 
    return builder.as_markup()


def delete_keyboard():
    events = load_events()
    if not events:
        return None
    buttons = []
    for e in events:
        buttons.append([InlineKeyboardButton(text=f"❌ {e['name']}", callback_data=f"delete:{e['name']}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def sorted_events_keyboard():
    builder = InlineKeyboardBuilder()
    events = load_sorted_events()

    if not events:
        builder.add(InlineKeyboardButton(text="Нет событий", callback_data="no_events"))
    else:
        for ev in events:
            name = ev.get("name", "Без названия")
            builder.add(
                InlineKeyboardButton(
                    text=name,
                    callback_data=f"event:{name}"
                )
            )

    builder.adjust(1)
    return builder.as_markup()