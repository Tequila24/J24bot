# -*- coding: utf-8 -*-
"""
@author: Fuego Tequila
"""


import common
from modules.BaseModule import BaseModule
from VkLib import VkLib
from datetime import datetime
import time
import random


preheat_lines = [	"Время пришло ( ͡° ͜ʖ ͡°)",
					"The time has come and so have I",
					"И не надоело вам?",
					"Нормальные люди спят в это время вообще-то",
					"♪ ~Вкалывают роботы, а не человек~ ♪",
					"Вскрываем ящик Пандоры...",
					"Я здесь что б жвачку жевать и пидоров назначать, а жвачка у меня кончилась",
					"Опять работать?" ]

nomination_lines = [	"Герой-пидор сегодняшнего дня @{0}",
						"Правом, данным мне свыше, объявляю пидором дня @{0}!",
						"Ну и пидор же ты, @{0}",
						"Кто это такой красивый у нас? @{0}!",
						"У нас во дворе за такое убивают, @{0}",
						"╰( ͡° ͜ʖ ͡° )つ──☆*:・ﾟ Вжух и ты пидор, @{0}!",
						"@{0}, представитель вида faggot vulgaris",
						"Отринь свою гетеросексуальность, @{0}!"	]

countLines = [	"Минуточку, надо посчитать...",
				"Так... этот один раз, тут два.. так падажжи ёмана",
				"А ВОТ ОНИ",
				"В э фильме снимались",
				"Они сделали свой выбор" ]


class FagModule(BaseModule):

	def __init__(self, vk: VkLib):
		self.vk = vk
		pass

	def register_in_chat(self, peer_id: int):
		pass

	def add_user_to_players(self, peer_id: int, user_id: int):
		pass

	def remove_user_from_players(self, peer_id: int, user_id: int):
		pass

	def parse_message(self, message: common.vk_message):
		print("fag module: " + message.text)
		return False

	def scheduled_check(self):
		print("fag check")