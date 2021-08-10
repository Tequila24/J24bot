# -*- coding: utf-8 -*-
"""
@author: Fuego Tequila
"""

import common

class BaseModule:



    def parse_message(self, message: common.vk_message) -> bool:
        raise NotImplementedError

    def scheduled_check(self):
        pass
