# -*- coding: utf-8 -*-
"""
@author: Fuego Tequila
"""

from pprint import pprint
import json
from datetime import datetime
import traceback
from pathlib import Path
from typing import List
import os
from common import vk_message
from VkLib import VkLib
from modules.BaseModule import BaseModule
from modules.POTDModule import POTDModule
from modules.ReminderModule import ReminderModule
from modules.VariousModule import VariousModule

class VKBot:
    def __init__(self):
        self.token, self.group_id = self.load_settings_from_file()

        try:
            os.mkdir("db/")
        except OSError as error:
            print("db directory already exists")

        self.vk = VkLib(self.token, self.group_id)
        self.modules: List[BaseModule] = [POTDModule(self.vk, self.group_id),
                                          ReminderModule(self.vk),
                                          VariousModule(self.vk)]
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

    def listen_longpoll(self):
        while True:
            try:
                for event in self.vk.longpoll.listen():
                    if event.type == VkLib.VkBotEventType.MESSAGE_NEW:

                        message = vk_message(dict(event.object))

                        if "помощь" in message.text[:6]:
                            help_str: str = ""
                            for module in self.modules:
                                help_str = help_str + module.get_help()
                            self.vk.reply(message.peer_id, help_str)

                        # Check message for
                        for module in self.modules:
                            if module.check_message(message):
                                break

            except:
                s: str = traceback.format_exc()
                print("FAILURE {0}: \t".format(datetime.today().strftime("%Y-%m-%d %H:%M:%S")) + s)



if __name__ == "__main__":
    print("I am compleeeeete")
    bot = VKBot()







