
from datetime import datetime 
from pathlib import Path


from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State


import app.keyboards as kb 
from data import save_event, load_events, save_events, load_sorted_events
from app.keyboards import events_keyboard, delete_keyboard, sorted_events_keyboard


router = Router()
now = datetime.now()
BOT_PASSWORD = "1234"
authorized_users = set()



class Auth(StatesGroup):
    waiting_for_password = State()

class NewEvent(StatesGroup):
    name = State()
    date = State()
    time = State()
    description = State()


class EditEvent(StatesGroup):
    select_event = State()  # выбор события для редактирования
    select_field = State()  # выбор поля для редактирования (name, date, time, description)
    new_value = State()     # ввод нового значения


#Старт бота


@router.message(CommandStart())
async def start_bot(message: Message, state: FSMContext):
    if message.from_user.id in authorized_users:
        await message.answer("✅ Ты уже авторизован.", reply_markup=kb.main)
    else:
        await message.answer("🔒 Введи пароль для доступа к боту:")
        await state.set_state(Auth.waiting_for_password)


@router.message(Auth.waiting_for_password)
async def check_password(message: Message, state: FSMContext):
    if message.text == BOT_PASSWORD:
        authorized_users.add(message.from_user.id)
        await message.answer("✅ Пароль верный! Доступ разрешён.", reply_markup=kb.main)
        await state.clear()
    else:
        await message.answer("❌ Неверный пароль. Попробуй ещё раз.")

        
#рандомна команда
@router.message(Command("help"))
async def get_help(message: Message):
    await message.reply(
    "This bot can:\n"
    "New event:\n"
    "All events:\n"
    "Delete event:\n"
    "Filter events:\n"
    "Current time:"
    )
#время сейчас
@router.message(Command("time"))
async def get_time(message: Message):
    await message.answer(f"Now is {now.strftime('%H:%M')}")

#новый евент
@router.message(Command("new_event"))
async def new_event_1(message: Message, state: FSMContext):
    await state.set_state(NewEvent.name)
    await message.answer("Name of the event:")


@router.message(NewEvent.name)
async def new_event_2(message: Message, state: FSMContext):
    name = message.text.strip()
    events = load_events()
    if any(ev.get("name") == name for ev in events):
        await message.answer("Event with this name already exists. Please enter another name:")
        return  
    await state.update_data(name=name)
    await state.set_state(NewEvent.date)
    await message.answer("Date of the event:")


@router.message(NewEvent.date)
async def new_event_3(message: Message, state: FSMContext):
    await state.update_data(date=message.text)
    await state.set_state(NewEvent.time)
    await message.answer("Time of the event:")


@router.message(NewEvent.time)
async def new_event_4(message: Message, state: FSMContext):
    await state.update_data(time=message.text)
    await state.set_state(NewEvent.description)
    await message.answer("Description of the event:")


@router.message(NewEvent.description)
async def new_event_5(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    data = await state.get_data()
    save_event(data)
    await message.answer(f"The new event was created! \nName: {data['name']} \n\nDate: {data['date']} \n\nTime: {data['time']} \n\nDescription: {data['description']}")


    await state.clear()


@router.message(Command("all_events"))
async def all_events(message: Message):
    await message.answer(
        "All events: ",
        reply_markup=events_keyboard()
    )


@router.callback_query(lambda c: c.data.startswith("event:"))
async def event_detail(callback: CallbackQuery):
    event_name = callback.data.split(":", 1)[1]
    events = load_events()

    for e in events:
        if e["name"] == event_name:
            text = (
                f"📌 Name: {e['name']}\n"
                f"📅 Date: {e['date']}\n"
                f"⏰ Time: {e['time']}\n"
                f"📝 Description: {e['description']}"
            )
            await callback.message.answer(text)
            break

    await callback.answer()


@router.message(F.text == "/delete_event")
async def delete_event_cmd(message: Message):
    kb = delete_keyboard()
    if kb:
        await message.answer("Выбери событие для удаления:", reply_markup=kb)
    else:
        await message.answer("❌ Нет событий для удаления.")


@router.callback_query(lambda c: c.data.startswith("delete:"))
async def delete_event(callback: CallbackQuery):
    event_name = callback.data.split(":", 1)[1]
    events = load_events()  # загружаем список
    updated = [e for e in events if e["name"] != event_name]  # удаляем выбранное событие
    save_events(updated)  # сохраняем весь список обратно
    await callback.message.answer("Событие удалено!")


@router.message(Command("edit_event"))
async def edit_event_cmd(message: Message):
    events = load_events()
    if not events:
        await message.answer("❌ Нет событий для редактирования.")
        return

    keyboard = events_keyboard(prefix="edit:")  # кнопки с callback_data "edit:NAME"
    await message.answer("Выберите событие для редактирования:", reply_markup=keyboard)


# Шаг 2: Пользователь выбирает событие через callback
@router.callback_query(lambda c: c.data.startswith("edit:"))
async def edit_event_callback(callback: CallbackQuery, state: FSMContext):
    event_name = callback.data.split(":", 1)[1]
    await state.update_data(event_name=event_name)
    await state.set_state(EditEvent.select_field)
    await callback.message.answer(
        f"Вы выбрали событие: {event_name}\n"
        f"Какое поле хотите изменить? (name, date, time, description)"
    )
    await callback.answer()


# Шаг 3: Пользователь вводит поле, которое хочет изменить
@router.message(EditEvent.select_field)
async def select_field(message: Message, state: FSMContext):
    field = message.text.strip().lower()
    if field not in ["name", "date", "time", "description"]:
        await message.answer("❌ Неверное поле. Введите: name, date, time или description")
        return
    await state.update_data(field=field)
    await state.set_state(EditEvent.new_value)
    await message.answer(f"Введите новое значение для {field}:")


# Шаг 4: Пользователь вводит новое значение
@router.message(EditEvent.new_value)
async def set_new_value(message: Message, state: FSMContext):
    data = await state.get_data()
    event_name = data["event_name"]
    field = data["field"]
    new_value = message.text.strip()

    events = load_events()
    for e in events:
        if e["name"] == event_name:
            e[field] = new_value
            break

    save_events(events)
    await message.answer(f"✅ Событие обновлено: {field} = {new_value}")
    await state.clear()


@router.message(Command("sorted_events"))
async def sorted_events_cmd(message: Message):
    events = load_sorted_events()
    if not events:
        await message.answer("❌ Событий нет.")
        return

    await message.answer(
        "📅 События по дате:",
        reply_markup=sorted_events_keyboard()
    )
