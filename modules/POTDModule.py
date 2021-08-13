# -*- coding: utf-8 -*-
"""
@author: Fuego Tequila
"""


from pprint import pprint
import common
from modules.BaseModule import BaseModule
from VkLib import VkLib
from DBLib import DBLib
import re
import json
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
						"Отринь свою гетеросексуальность, @{0}!",
						"I wanna take you, {0}, to the gay bar!,"
						"{0}, компьютер говорит что ты пидор.",]

countLines = [	"Минуточку, надо посчитать...",
				"Так... этот один раз, тут два.. так падажжи ёмана",
				"А ВОТ ОНИ:",
				"В э фильме снимались:",
				"Они сделали свой выбор:" ]


class POTDModule(BaseModule):

	def __init__(self, vk: VkLib, group_id: int):
		self.group_id = group_id
		self.vk = vk
		self.db = DBLib("db//potd")
		#self.start_in_chat(2000000001, 19155229)
		#self.remove_user_from_players(2000000001, 19155229)
		#self.check_today_fag(2000000001)

	def start_in_chat(self, peer_id: int, author_id: int):
		admins_list = self.vk.get_chat_admins(peer_id)
		if author_id not in admins_list:
			self.vk.reply(peer_id, "Запустить поиск пидора дня может только админ!")
			return

		self.db.create_table("chat{0}".format(peer_id), [("parameter", "TEXT"),
														 ("value", "TEXT")])
		users_list = self.vk.get_chat_members(peer_id, self.group_id)
		for user in users_list.keys():
			self.add_user_to_players(peer_id, user, users_list[user])

	def add_user_to_players(self, peer_id: int, user_id: int, user_nickname: str):
		# get users list from DB
		reply = self.db.exc("""SELECT value FROM '{0}' WHERE parameter = (?);""".format(("chat" + str(peer_id))), ("players", ))
		players: dict
		if len(reply) != 0:
			players = dict(json.loads(reply[0][0]))
		else:
			players = {}

		# check if user exists and his nickname, and add or change if not
		if str(user_id) in players.keys():
			if players[str(user_id)] != user_nickname:
				players[str(user_id)] = user_nickname
				self.vk.reply(peer_id, "@{0}, ты в игре".format(user_nickname))
			else:
				self.vk.reply(peer_id, "Игрок @{0} уже зарегистрирован под ником {1}!".format(user_id, user_nickname))
		else:
			players[str(user_id)] = user_nickname

		# write new players list to DB
		self.db.exc("""INSERT OR REPLACE INTO '{0}' VALUES ((?), (?))""".format(("chat" + str(peer_id))), ("players", json.dumps(players)))
		self.db.com()

	def remove_user_from_players(self, peer_id: int, user_id: int, author_id: int):
		admins_list = self.vk.get_chat_admins(peer_id)
		if author_id not in admins_list:
			if author_id != user_id:
				self.vk.reply(peer_id, "Доступ запрещён")
				return
		# get users list from DB
		reply = self.db.exc("""SELECT value FROM '{0}' WHERE parameter = (?);""".format(("chat" + str(peer_id))), ("players",))
		players: dict
		if len(reply) != 0:
			players = dict(json.loads(reply[0][0]))
		else:
			return

		# if user exists in players list - remove
		if str(user_id) in players.keys():
			removed_player = players.pop(str(user_id))
			self.db.exc("""INSERT OR REPLACE INTO '{0}' VALUES ((?), (?))""".format(("chat" + str(peer_id))), ("players", json.dumps(players)))
			self.db.com()
			self.vk.reply(peer_id, "@{0}, выписан из геев!".format(removed_player))
			#print("@{0}, выписан из геев!".format(removed_player))
		else:
			self.vk.reply(peer_id, "пользователя @{0} нет в списках!".format(user_id))
			#print("Пользователя @{0} нет в списках!".format(user_id))

	def check_today_fag(self, peer_id: int):
		# get current faggot id
		reply = self.db.exc("""SELECT value FROM '{0}' WHERE parameter = (?);""".format(("chat" + str(peer_id))), ("last_fag_id",))
		last_fag_user_id: int
		if len(reply) != 0:
			last_fag_user_id: int = int(reply[0][0])
		else:
			last_fag_user_id = -1

		# get last faggot time
		reply = self.db.exc("""SELECT value FROM '{0}' WHERE parameter = (?);""".format(("chat" + str(peer_id))), ("last_fag_time", ))
		last_fag_time: str
		if len(reply) != 0:
			last_fag_time: str = str(reply[0][0])
		else:
			last_fag_time: str = datetime.utcfromtimestamp(0).strftime("%Y-%m-%d")

		# get players list
		reply = self.db.exc("""SELECT value FROM '{0}' WHERE parameter = (?);""".format(("chat" + str(peer_id))), ("players",))
		players: dict
		if len(reply) != 0:
			players = dict(json.loads(reply[0][0]))
		else:
			players = {}

		# check for cooldown
		if last_fag_time != 0:
			time_ago_in_secs: int = int((datetime.today() - datetime.strptime(last_fag_time, "%Y-%m-%d")).total_seconds())
			hours_ago: int = time_ago_in_secs // 3600
			if (hours_ago < 24) and (last_fag_user_id != -1):
				time_left = 24 - hours_ago
				reply = "Если мне не изменяет память, пидор сегодня - @{0}, и останется им ещё {1} часов".format(players[str(last_fag_user_id)], time_left)
				self.vk.reply(peer_id, reply)
				return

		# send preheat line to chat
		preheat_line = preheat_lines[random.randrange(0, len(preheat_lines) - 1)]
		self.vk.reply(peer_id, preheat_line)
		time.sleep(1)

		# select random id from players list
		players_ids: list =  list(players.keys())
		random.shuffle(players_ids)
		if len(players_ids) > 1:
			today_fag_id = players_ids[random.randrange(0, len(players_ids) - 1)]
		else:
			today_fag_id = players_ids[0]
		self.modify_fag_count_for(peer_id, today_fag_id, 1)

		# save date and id of last winner
		self.db.exc("""INSERT OR REPLACE INTO '{0}' VALUES ((?), (?))""".format(("chat" + str(peer_id))), ("last_fag_time", datetime.today().strftime("%Y-%m-%d")))
		self.db.exc("""INSERT OR REPLACE INTO '{0}' VALUES ((?), (?))""".format(("chat" + str(peer_id))), ("last_fag_id", today_fag_id))
		self.db.com()

		# announce winner to chat
		nomination_line = nomination_lines[random.randrange(0, len(nomination_lines) - 1)]
		self.vk.reply(peer_id, nomination_line.format(players[today_fag_id]))

	def modify_fag_count_for(self, peer_id: int, user_id: int, modify_by: int):
		# get scoreboard from DB
		reply = self.db.exc("""SELECT value FROM '{0}' WHERE parameter = (?);""".format(("chat" + str(peer_id))), ("scoreboard",))
		scoreboard: dict
		if len(reply) != 0:
			scoreboard = dict(json.loads(reply[0][0]))
		else:
			scoreboard = {}

		# modify score for player
		if user_id in scoreboard.keys():
			scoreboard[user_id] = scoreboard[user_id] + modify_by
		else:
			scoreboard[user_id] = 1

		# save modified scoreboard to DB
		self.db.exc("""INSERT OR REPLACE INTO '{0}' VALUES ((?), (?))""".format(("chat" + str(peer_id))), ("scoreboard", json.dumps(scoreboard)))
		self.db.com()

	def show_fag_stats(self, peer_id: int):
		# get scoreboard from DB
		reply = self.db.exc("""SELECT value FROM '{0}' WHERE parameter = (?);""".format(("chat" + str(peer_id))), ("scoreboard",))
		scoreboard: dict
		if len(reply) != 0:
			scoreboard = dict(json.loads(reply[0][0]))
		else:
			scoreboard = {}

		# get users list from DB
		reply = self.db.exc("""SELECT value FROM '{0}' WHERE parameter = (?);""".format(("chat" + str(peer_id))),
							("players",))
		players: dict
		if len(reply) != 0:
			players = dict(json.loads(reply[0][0]))
		else:
			players = {}

		scoreboard_as_string: str = ""
		if len(scoreboard) == 0:
			scoreboard_as_string = "А не было у нас ещё пидоров! Хаха!"
		else:
			players_top_list = dict(sorted(scoreboard.items(), key=lambda x: x[1], reverse=True))  # I like your funny words, magic lambda man
			self.vk.reply(peer_id, countLines[random.randrange(0, len(countLines) - 1)])
			players_list = players
			for fag in players_top_list.keys():
				fag_name: str
				if str(fag) in players_list.keys():
					fag_name = players_list[str(fag)]
				else:
					fag_name = self.vk.get_user_domain_by_id(fag)
				scoreboard_as_string += "{0} - {1} \r\n".format(fag_name, players_top_list[fag])
		self.vk.reply(peer_id, scoreboard_as_string)
		pass

	def show_players_list(self, peer_id: int):
		reply = self.db.exc("""SELECT value FROM '{0}' WHERE parameter = (?);""".format(("chat" + str(peer_id))), ("players",))
		players: dict
		if len(reply) != 0:
			players = dict(json.loads(reply[0][0]))
		else:
			players = {}
		players = dict(sorted(players.items(), key=lambda x: x[1]))
		players_msg: str = ""
		for key in players.keys():
			players_msg  = players_msg + ("@id{0}: {1}\n".format(str(key), str(players[key])))
		self.vk.reply(peer_id, players_msg)

	def check_message(self, message: common.vk_message):
		if not message.is_for_me:
			return False

		if "открыть пидорклуб" in message.text:
			self.start_in_chat(message.peer_id, message.author_id)
			return True

		match = re.match(r'добавь (?:меня )?в пидорклуб', message.text)
		if match:
			user_nickname = self.vk.get_user_domain_by_id(message.author_id)
			self.add_user_to_players(message.peer_id, message.author_id, user_nickname)
			return True

		# do not let Dinar escape from the club
		'''if "выйти из пидорклуба" in message.text:
			self.remove_user_from_players(message.peer_id, message.author_id, message.author_id)
			return True'''

		match = re.match(r'удали(?:ть)? из пидорклуба @?(\w*)', message.text)
		if match:
			to_remove = match.group(1)
			self.remove_user_from_players(message.peer_id, self.vk.get_user_id_by_domain(to_remove), message.author_id)
			return True

		if "кто пидор" in message.text:
			self.check_today_fag(message.peer_id)
			return True

		if "топ пидоров" in message.text:
			self.show_fag_stats(message.peer_id)
			return True

		if "список пидоров" in message.text:
			self.show_players_list(message.peer_id)
			return True

		return False

	def get_help(self) -> str:
		return """Пидор Дня:
				  открыть пидорклуб - запустить игру поиска пидора дня (доступно админам)
				  добавь (меня) в пидорклуб - добавить автора сообщения в список игроков
				  удали(ть) из пидорклуба [id\домен] - удалить пользователя под таким id\доменом из списка игроков (доступно админам)
				  кто пидор - выбрать пидора дня
				  топ пидоров - вывести таблицу лидеров-пидеров \n\n"""
