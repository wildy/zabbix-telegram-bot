#!/usr/bin/python
# -*- encoding: utf-8 -*-

import ConfigParser, telebot, requests, argparse, os
from telebot import types

# Change directory to script's current dir
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# INI file with configuration variables
conffile = "./tgbot.conf"

# Read in configuration
c = ConfigParser.ConfigParser()
c.read(conffile)

api_token = c.get('globals', 'api_token')

zabbix_url = c.get('zabbix', 'zabbix_url')
zabbix_description = c.get('zabbix', 'zabbix_description')


# Init bot
bot = telebot.TeleBot(api_token)

@bot.message_handler(content_types=["text"])
def handle_trigger(event_id, trigger, severity, status, group, zabbix_description, level=None):
	from telebot import types
	group_id = c.get('groups', group)
	message = """
<b>%s</b>
(%s)
Trigger <b>%s</b>:

%s
	""" % (zabbix_description, severity, status, trigger)

	# If passed level from command line (-l), override config
	if not level:
		level = c.get('severities', severity)

	# Do not show notifications if notification level is set low for this event (by config or '-l' parameter)
	if level < -9:
		# Don't even bother sending it
		return
	elif level < 0:
		disable_notification = True
	else:
		disable_notification = False
	print(disable_notification)
	kb = types.InlineKeyboardMarkup()

	if status == 'PROBLEM':
		ack_button = types.InlineKeyboardButton(text="Acknowledge", callback_data="ACKNOWLEDGE %s" % event_id)
		kb.add(ack_button)

	bot.send_message(group_id, message, parse_mode='HTML', disable_notification=disable_notification, reply_markup=kb)

parser = argparse.ArgumentParser(add_help=True)
parser.add_argument('-i', dest='event_id', help='Event ID (for inline acknowledge)', required=True, type=int)
parser.add_argument('-t', dest='trigger', help='Trigger name', required=True)
parser.add_argument('-s', dest='severity', help='Severity', required=True)
parser.add_argument('-S', dest='status', help='Status', required=True)
parser.add_argument('-g', dest='group', help='Group to send trigger to', required=True)
parser.add_argument('-l', dest='level', help='Override this event notification level: -2 = do not send at all; -1 = send without sound, 0 = send standard notification', type=int, default=None)

args = parser.parse_args()

handle_trigger(args.event_id, args.trigger, args.severity, args.status, args.group, zabbix_description, args.level)

