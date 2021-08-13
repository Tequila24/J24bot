# -*- coding: utf-8 -*-
"""
@author: Fuego
"""


import common
from modules.BaseModule import BaseModule
from VkLib import VkLib
import random
import re
from DBLib import DBLib
from datetime import datetime, timedelta
import typing
import threading


class VariousModule(BaseModule):

    def __init__(self, vk: VkLib):
        self.vk = vk
        self.db = DBLib("db//etc_module")
        self.db.create_table("active_chats", [('id', 'INTEGER')])

    def introduce(self, peer_id: int):
        self.vk.reply(peer_id, """beep-boop I'm a bot\n
                                  Меня зовут Джей. Для полноценной работы всех модулей желательно выдать мне права администратора. 
                                  Обратиться ко мне можно начав писать команду с имени, например "джей помощь" иди "@jay_bot помощь".
                                  Книга жалоб и предложений - в личке моего профиля.""")

    def echo(self, peer_id: int, message: str):
        self.vk.reply(peer_id, '>' + message.strip())

    def reply_dice(self, peer_id: int, author_id: int, dices_amount, dice_value):
        if (dices_amount < 1) or (dice_value < 2):
            self.vk.reply(peer_id, "Количество костей должно быть больше 0, а значение - больше 1")
            return

        if (dices_amount > 999) or (dice_value > 999):
            self.vk.reply(peer_id, "превышен лимит")
            return

        reply_text = "@{0} ".format(self.vk.get_user_domain_by_id(author_id))
        for i in range(dices_amount):
            reply_text += " " + str(random.randrange(1, dice_value + 1))
        self.vk.reply(peer_id, reply_text)

    def broadcast(self, message_text: str):
        active_chats = self.db.exc("""SELECT * FROM 'active_chats'""")
        for chat in active_chats:
            try:
                self.vk.reply(chat[0], message_text)
            except:
                self.db.exc("""DELETE FROM 'active_chats' WHERE id=(?);""", (chat[0], ))
                self.db.com()

    def check_message(self, message: common.vk_message) -> bool:
        if message.is_new_chat:
            self.db.exc("""INSERT OR REPLACE INTO 'active_chats' VALUES(?);""", (str(message.peer_id),))
            self.db.com()
            self.introduce(message.peer_id)
            return True

        if 'эхо' in message.text[:3]:
            self.echo(message.peer_id, message.text[3:])
            return True

        match = re.match(r'(-?\d+)[DdДд](-?\d+)', message.text)
        if match:
            self.reply_dice(message.peer_id, message.author_id, int(match.group(1)), int(match.group(2)))
            return True

        if 'бродкаст' in message.text[:8]:
            if int(message.peer_id) == 2000000001: #test conf
                if int(message.author_id) == 19155229:
                    self.broadcast(message.text[8:])

        return False

    def get_help(self) -> str:
        return """Общие:
                  эхо [сообщение]- повторить сообщение
                  [N]d[M] - бросить кости а-ля 1d20, где N - количество костей, M - количество граней. Максимальные значения - 999 \n\n"""