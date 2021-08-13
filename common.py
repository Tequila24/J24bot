# -*- coding: utf-8 -*-
"""
@author: Fuego Tequila
"""

import json
import re

class vk_message:

    def __init__(self, message_event: dict):
        json_event = message_event

        self.message_id = int(json_event['conversation_message_id'])
        self.author_id = int(json_event['from_id'])
        self.epoch_date = int(json_event['date'])
        self.peer_id = int(json_event['peer_id'])
        self.text = str(json_event['text']).strip()

        self.is_for_me = False
        if len(self.text) > 5:
            match = re.match(r'((?:(?:джей)|(?:jay)|(?:\[club206383181\|@jay_bot\])))', self.text[:24].lower())
            if match:
                self.is_for_me = True
                self.text = self.text[len(match.group(1)):].strip()

        self.is_new_chat = False
        if 'action' in json_event:
            if json_event['action']['type'] == 'chat_invite_user':
                if int(json_event['action']['member_id']) == -206383181:
                    self.is_new_chat = True