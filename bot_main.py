# -*- coding: utf-8 -*-
"""
@author: Fuego Tequila
"""


from datetime import datetime
import time
import traceback
from pathlib import Path
import threading
from typing import List
import re
from common import vk_message
from VkLib import VkLib
from DBLib import DBLib
from modules.BaseModule import BaseModule
from modules.FagModule import FagModule

class VKBot:
    def __init__(self):
        self.token, self.group_id = self.load_settings_from_file()

        self.vk = VkLib(self.token, self.group_id)
        self.modules: List[BaseModule] = [FagModule(self.vk)]

        self.scheduled_check()
        self.listen_longpoll()


    def load_settings_from_file(self):
        token: str = "0"
        group_id: int = 0

        settings_file_path = Path('./settings.txt')
        if settings_file_path.is_file():
            file = open(settings_file_path, 'r')
            lines = file.readlines()
            for line in lines:
                if 'token=' in line:
                    token = line[6:].strip()
                if 'group_id=' in line:
                    group_id = int(line[9:].strip())
        return token, group_id

    def check_is_for_me(self, message_text: str):
        if len(message_text) > 5:
            match = re.match(r'((?:(?:бот)|(?:bot)|(?:джей)|(?:суб24)),? ?)', message_text[:6].lower())
            if match:
                return True, message_text[len(match.group(1)):]
        return False, ''

    def scheduled_check(self):
        threading.Timer(interval=1.0, function=self.scheduled_check, args=[]).start()

        for module in self.modules:
            module.scheduled_check()

    def listen_longpoll(self):
        while True:
            try:
                for event in self.vk.longpoll.listen():
                    if event.type == VkLib.VkBotEventType.MESSAGE_NEW:

                        message = vk_message(dict(event.object))

                        is_for_me, cleaned_message_text = self.check_is_for_me(message.text)
                        if not is_for_me:
                            continue
                        else:
                            message.text = cleaned_message_text

                        for module in self.modules:
                            module.parse_message(message)

            except:
                s: str = traceback.format_exc()
                print("FAILURE {0}: \t".format(datetime.today().strftime("%Y-%m-%d %H:%M:%S")) + s)



if __name__ == "__main__":
    print("I am compleeeeete")

    bot = VKBot()

    print("MAIN THREAD: " + threading.currentThread().name)






