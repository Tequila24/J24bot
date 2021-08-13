# -*- coding: utf-8 -*-
"""
@author: Fuego Tequila
"""

import common

class BaseModule:

    def check_message(self, message: common.vk_message) -> bool:
        raise NotImplementedError

    def get_help(self) -> str:
        raise NotImplementedError