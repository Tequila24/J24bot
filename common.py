# -*- coding: utf-8 -*-
"""
@author: Fuego Tequila
"""

import json

class vk_message:

    def __init__(self, message_event: dict):
        json_event = json.loads(json.dumps(message_event))

        self.message_id = int(json_event['conversation_message_id'])
        self.author_id = int(json_event['from_id'])
        self.epoch_date = int(json_event['date'])
        self.peer_id = int(json_event['peer_id'])
        self.text = str(json_event['text']).strip()