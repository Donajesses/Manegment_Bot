import logging
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


# Налаштування логів
logging.basicConfig(
    level=logging.INFO,  
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="bot.log",  
    filemode="a"         
)
logger = logging.getLogger(__name__)


#Необхiднi змiннi  та параметри
router = Router()
now = datetime.now()
BOT_PASSWORD = "1234"
authorized_users = set()

#Пароль для бота
class Auth(StatesGroup):
    waiting_for_password = State()

#класс для нового Iвенту
class NewEvent(StatesGroup):
    name = State()
    date = State()
    time = State()
    description = State()

#змiнювання Iвенту
class EditEvent(StatesGroup):
    select_event = State()  # выбор события для редактирования
    select_field = State()  # выбор поля для редактирования (name, date, time, description)
    new_value = State()     # ввод нового значения


#Старт бота
@router.message(CommandStart())
async def start_bot(message: Message, state: FSMContext):
    if message.from_user.id in authorized_users:
        await message.answer("✅ You are already autorised.", reply_markup=kb.main)
    else:
        await message.answer("🔒 Enter the password to use this Bot:")
        await state.set_state(Auth.waiting_for_password)


#Запит пароля при стартi
@router.message(Auth.waiting_for_password)
async def check_password(message: Message, state: FSMContext):
    if message.text == BOT_PASSWORD:
        authorized_users.add(message.from_user.id)
        await message.answer("✅ Correct password! ", reply_markup=kb.main)
        await state.clear()
    else:
        await message.answer("❌ Wrong password, try again")

        
#время сейчас
@router.message(Command("time"))
async def get_time(message: Message):
    await message.answer(f"Now is {now.strftime('%H:%M')}")


#новый евент
@router.message(Command("new_event"))
async def new_event_1(message: Message, state: FSMContext):
    await state.set_state(NewEvent.name)
    await message.answer("Name of the event:")


#питаемо Iм´я
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


#питаемо дату
@router.message(NewEvent.date)
async def new_event_3(message: Message, state: FSMContext):
    await state.update_data(date=message.text)
    await state.set_state(NewEvent.time)
    await message.answer("Time of the event:")


#питаемо час
@router.message(NewEvent.time)
async def new_event_4(message: Message, state: FSMContext):
    await state.update_data(time=message.text)
    await state.set_state(NewEvent.description)
    await message.answer("Description of the event:")


# питаемо опис ивенту
@router.message(NewEvent.description)
async def new_event_5(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    data = await state.get_data()
    save_event(data)
    logger.info(f"New event created by {message.from_user.id}: {data}")
    await message.answer(
        f"The new event was created! \nName: {data['name']} \n\nDate: {data['date']} \n\nTime: {data['time']} \n\nDescription: {data['description']}"
    )
    await state.clear()


#виводить всi Iвенти
@router.message(Command("all_events"))
async def all_events(message: Message):
    await message.answer(
        "All events: ",
        reply_markup=events_keyboard()
    )


#виводить всi Iвенти
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


#видалення iвенту
@router.message(F.text == "/delete_event")
async def delete_event_cmd(message: Message):
    kb = delete_keyboard()
    if kb:
        await message.answer("Choose the event to delete:", reply_markup=kb)
    else:
        await message.answer("❌ No events to delete.")


@router.callback_query(lambda c: c.data.startswith("delete:"))
async def delete_event(callback: CallbackQuery):
    event_name = callback.data.split(":", 1)[1]
    events = load_events()  # загружаем список
    updated = [e for e in events if e["name"] != event_name]  # удаляем выбранное событие
    save_events(updated)  # сохраняем весь список обратно
    await callback.message.answer("Event was deleted!")


#Змiна Iвента
@router.message(Command("edit_event"))
async def edit_event_cmd(message: Message):
    events = load_events()
    if not events:
        await message.answer("❌ No events to edit.")
        return

    keyboard = events_keyboard(prefix="edit:")  # кнопки с callback_data "edit:NAME"
    await message.answer("Choose the event to edit:", reply_markup=keyboard)


#вибiр Iвента
@router.callback_query(lambda c: c.data.startswith("edit:"))
async def edit_event_callback(callback: CallbackQuery, state: FSMContext):
    event_name = callback.data.split(":", 1)[1]
    await state.update_data(event_name=event_name)
    await state.set_state(EditEvent.select_field)
    await callback.message.answer(
        f"You choosed the event: {event_name}\n"
        f"What do you want to edit? (name, date, time, description)"
    )
    await callback.answer()


# що треба змiнити
@router.message(EditEvent.select_field)
async def select_field(message: Message, state: FSMContext):
    field = message.text.strip().lower()
    if field not in ["name", "date", "time", "description"]:
        await message.answer("❌ Wrong field. Enter: name, date, time or description")
        return
    await state.update_data(field=field)
    await state.set_state(EditEvent.new_value)
    await message.answer(f"Enter the new value for {field}:")


# Нове значченя для поля
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
    await message.answer(f"✅ Event was updated: {field} = {new_value}")
    await state.clear()


#сортировка всiх iвентiв
@router.message(Command("sorted_events"))
async def sorted_events_cmd(message: Message):
    events = load_sorted_events()
    if not events:
        await message.answer("❌ No Events.")
        return

    await message.answer(
        "📅 Date sorted events:",
        reply_markup=sorted_events_keyboard()
    )
