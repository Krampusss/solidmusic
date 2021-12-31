import time
from importlib import import_module
from os import listdir
from os.path import join, dirname, realpath
from typing import Dict, List, Optional

from pyrogram.types import InlineKeyboardButton

from database.lang_utils import gm

plugins_dir = join(dirname(realpath(__file__)), ".")

cmds = {}
helps: Dict[str, Dict[str, str]] = {}
modules: List[InlineKeyboardButton] = []


def _all_modules():
    for file in listdir(plugins_dir):
        if file.endswith(".py") and not file.startswith("__"):
            yield file[:-3]


async def paginate_module(chat_id: int, user_id: int):
    global modules
    temp, keyboard = [], []
    for count, button in enumerate(modules, start=1):
        temp.append(button)
        if count % 3 == 0:
            keyboard.append(temp)
            temp = []
        if len(modules) == count:
            keyboard.append(temp)
    keyboard.append(
        [
            InlineKeyboardButton(
                f"⬅️ {await gm(chat_id, 'backtomenu')}", "goback"
            ),
            InlineKeyboardButton(
                f"🗑️ {await gm(chat_id, 'close_btn_name')}", f"close|{user_id}"
            ),
        ]
    )
    temp.clear()
    return keyboard


async def load_modules(user_id: Optional[int] = 0):
    for mods in _all_modules():
        try:
            imported_mods = import_module(f"plugins.{mods}")
            time.sleep(0.25) if not user_id else None
            print(f"Loaded plugins {imported_mods.__name__}") if not user_id else None
            if hasattr(imported_mods, "__cmds__"):
                x = (
                    imported_mods.__name__
                    if "_" not in imported_mods.__name__
                    else imported_mods.__name__.split('_')[0]
                )
                print(f"Loaded command {imported_mods.__cmds__}") if not user_id else None
                cmds[x] = imported_mods.__cmds__
                if user_id:
                    modules.append(
                        InlineKeyboardButton(
                            x.split("plugins.")[1].title(),
                            callback_data=f"plugins.{mods.split('_')[0] if '_' in mods else mods}|{user_id}"
                        )
                    )
            if hasattr(imported_mods, "__help__"):
                x = (
                    imported_mods.__name__
                    if "_" not in imported_mods.__name__
                    else imported_mods.__name__.split('_')[0]
                )
                helps[x] = imported_mods.__help__
        except SyntaxError as e:
            print(f"Not loaded {e.filename}\nBecause of {e.with_traceback(e.__traceback__)}")
