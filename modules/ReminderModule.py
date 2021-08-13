# -*- coding: utf-8 -*-
"""
@author: Fuego
"""


import common
from modules.BaseModule import BaseModule
from VkLib import VkLib
from DBLib import DBLib
import re
from datetime import datetime, timedelta
import typing
import threading


class ReminderModule(BaseModule):

	def __init__(self, vk: VkLib):
		self.vk = vk
		self.db = DBLib("db//reminders", check_same_thread = False)

		self.schedule_check()

	def parse_reminder_command(self, reminder_raw: str) -> typing.Tuple[str, str]:
		expiration_date: str = ""
		reminder_text: str = ""

		match = re.match(r'(напомни (?:мне )?)', reminder_raw)
		if match:
			reminder_raw = reminder_raw[len(match.group(1)):].strip()

		match = re.match(r'(.+) через', reminder_raw)
		if match:
			reminder_text = match.group(1)

			match2 = re.search(r'через (?:(\d+) час(?:ов?|а?) ?)?(?:(\d+) минуты*у* ?)?(?:(\d+) секунды*у* ?)?', reminder_raw)
			if match2:
				expiration_date = (datetime.now() + timedelta(0,
															  int(match2.group(3)) if match2.group(3) is not None else 0,
															  0,
															  0,
															  int(match2.group(2)) if match2.group(2) is not None else 0,
															  int(match2.group(1)) if match2.group(1) is not None else 0,
															  0) ).strftime("%Y-%m-%d %H:%M:%S")
		else:

			year: str = str(datetime.now().year)
			month: str = ""
			day: str = ""
			hour: str = "10"
			minute: str = "0"
			second: str = "0"

			# REMINDER TEXT
			match = re.search(r'(.+) \d+[-.]\d+', reminder_raw)
			if match:
				reminder_text = match.group(1)

			# DATE DD-MM | DD.MM
			match = re.search(r'(\d{1,2})[-.](\d{1,2})[^.]', reminder_raw)
			if match:
				year = str(datetime.now().year)
				month = match.group(2)
				day = match.group(1)

			# DATE YYYY-MM-DD | YYYY.MM.DD
			match = re.search(r'(\d{4})[-.](\d{1,2})[-.](\d{1,2})', reminder_raw)
			if match:
				year = match.group(1)
				month = match.group(2)
				day = match.group(3)

			# DATE DD-MM-YYYY | DD.MM.YYYY
			match = re.search(r'(\d{1,2})[-.](\d{1,2})[-.](\d{4})', reminder_raw)
			if match:
				year = match.group(3)
				month = match.group(2)
				day = match.group(1)

			# TIME HH:MM:SS
			match = re.search(r'в (\d{1,2}):?(\d{1,2})?:?(\d{1,2})?', reminder_raw)
			if match:
				hour = match.group(1)
				minute = match.group(2) if match.group(2) is not None else 0
				second = match.group(3) if match.group(3) is not None else 0

			expiration_date = "{0}-{1}-{2} {3}:{4}:{5}".format(	year, month, day, hour, minute, second)

		return expiration_date, reminder_text

	def create_reminder(self, peer_id: int, author_id: int, reminder_raw: str):
		self.db.create_table("chat{0}".format(peer_id), [("id", "INTEGER"),
														 ("expiration_date", "TEXT"),
														 ("author_id", "INTEGER"),
														 ("text", "TEXT"),
														 ("chat_id", "INTEGER")])

		expiration_date, reminder_text = self.parse_reminder_command(reminder_raw)

		try:
			datetime.strptime(expiration_date, "%Y-%m-%d %H:%M:%S")
		except:
			self.vk.reply(peer_id, "Неправильный формат!")
			return

		response = (self.db.exc("SELECT MAX(id) FROM chat{0}".format(str(peer_id))))[0]
		if response[0] is not None:
			reminder_id = response[0]+1
		else:
			reminder_id = 1
		self.db.exc("""INSERT INTO 'chat{0}' VALUES((?), (?), (?), (?), (?));""".format(peer_id), (reminder_id, expiration_date, author_id, reminder_text, peer_id))
		self.db.com()
		self.vk.reply(peer_id, "Окей, записал")

	def remove_reminder(self, peer_id: int, author_id: int, reminder_id: int):
		response = self.db.exc("""SELECT * FROM 'chat{0}' WHERE id=(?);""".format(peer_id), (reminder_id, ))
		if len(response):
			if int(response[0][2]) == author_id:
				self.db.exc("""DELETE FROM 'chat{0}' WHERE id=(?);""".format(peer_id), (reminder_id, ))
				self.db.com()
				self.vk.reply(peer_id, "Твоя напоминалка номер {0} удалена!".format(reminder_id))
			else:
				self.vk.reply(peer_id, "Нельзя удалить чужую напоминалку!")
		else:
			self.vk.reply(peer_id, "Напоминалка с таким номером не найдена!")

	def get_reminders_for_user(self, peer_id: int, author_id: int):
		response = self.db.exc("""SELECT * FROM 'chat{0}' WHERE author_id = (?) ORDER BY expiration_date ASC;""".format(peer_id), (author_id, ))
		author_domain = self.vk.get_user_domain_by_id(author_id)
		if len(response):
			reply: str = "@{0}, вот твои напоминалки: \r\n".format(author_domain)
			for line in response:
				reply += "# {0}, {1}, {2}\r\n".format(line[0], line[1], line[3])
			self.vk.reply(peer_id, reply, disable_mention=False)
		else:
			self.vk.reply(peer_id, "{0}, у тебя нет напоминалок!".format(author_domain), disable_mention=False)

	def check_message(self, message: common.vk_message):
		if not message.is_for_me:
			return False

		match = re.search(r'напомни(?: мне)? (.+)', message.text)
		if match:
			self.create_reminder(message.peer_id, message.author_id, message.text)
			return True

		match = re.match(r'удали напоминалку (\d+)', message.text)
		if match:
			self.remove_reminder(message.peer_id, message.author_id, int(match.group(1)))
			return True

		if 'мои напоминалки' in message.text:
			self.get_reminders_for_user(message.peer_id, message.author_id)
			return True

		return False

	def schedule_check(self):
		threading.Timer(interval=1.0, function=self.schedule_check, args=[]).start()
		tables = self.db.exc("SELECT name FROM sqlite_master WHERE type='table';")
		if len(tables) > 0:
			for table in tables:
				table = table[0]
				reminders = self.db.exc("""SELECT * FROM {0};""".format(table))
				if len(reminders):
					for line in reminders:
						try:
							t_delta: float = (datetime.strptime(line[1], "%Y-%m-%d %H:%M:%S") - datetime.now()).total_seconds()
							if t_delta < 0.0:
								message: str = "@{0}, напоминаю: {1}".format(self.vk.get_user_domain_by_id(line[2]), line[3])
								self.vk.reply(line[4], message, disable_mention=False)
								self.db.exc("""DELETE FROM '{0}' WHERE id=(?);""".format(table), (line[0], ))
								self.db.com()
						except:
							print("FAILURE {0}: \t".format(datetime.today().strftime("%Y-%m-%d %H:%M:%S")) + "удалена напоминалка: " + str(line))
							self.db.exc("""DELETE FROM '{0}' WHERE id=(?);""".format(table), (line[0],))
							self.db.com()

	def get_help(self) -> str:
		return """Напоминалки:
				  напомни (мне) [текст] через [часов] [минут] [секунд] - Напоминалка с пингом! Например: "напомни попить чаю через 30 минут
				  напомни (мне) %текст %год-%месяц-%день %час-%минута-%секунда. Если время не будет указано, напомнит в 10:00:00
				  мои напоминалки - вывести список напоминалок
				  удали напоминалку [N] - удалить напоминалки под номером N \n\n"""