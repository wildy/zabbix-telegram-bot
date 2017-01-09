#!/usr/bin/python
# -*- encoding: utf-8 -*-
#
# Telegram events receiver, acknowledges events.
import ConfigParser, telebot, requests, re
from pyzabbix import ZabbixAPI
from datetime import datetime


# INI file with configuration variables
conffile = "./tgbot.conf"

# Read in configuration
c = ConfigParser.ConfigParser()
c.read(conffile)

api_token = c.get('globals', 'api_token')
ignore_older_than_mins = c.get('globals', 'ignore_older_than_mins')

zabbix_url = c.get('zabbix', 'zabbix_url')
zabbix_description = c.get('zabbix', 'zabbix_description')
zabbix_api_user = c.get('zabbix', 'zabbix_api_user')
zabbix_api_password = c.get('zabbix', 'zabbix_api_password')

bot = telebot.TeleBot(api_token)

# Get callback query and process it
@bot.callback_query_handler(func=lambda call: True)
def ack_callback(call):
	ack = {}
	ack['eventid']	= int(re.search(r'^ACKNOWLEDGE (\d+)$', call.data).group(1))
	ack['timestamp'] = datetime.fromtimestamp(int(call.message.date))
	message = "SmartLabs_Monitoring_Bot: Acknowledged by @%s from Telegram" % call.from_user.username

	# If the message is older than ignore_older_than_mins, complain to chat loudly
	reply_age_mins = ((datetime.now() - ack['timestamp']).seconds // 60)%60
	too_old_msg = "*ERROR:* Received ACK to message older than %s mins, you can only ACK this manually!" % ignore_older_than_mins
	success_msg = "@%s *successfully acknowledged* Zabbix trigger %s." % (call.from_user.username, ack['eventid'])
	unsuccessful_msg = "*ERROR:* Could not acknowledge Zabbix event %s, check bot!" % ack['eventid']

	if (reply_age_mins > ignore_older_than_mins):
		# User clicked the button on an ancient message
		print(too_old_msg + ', call: ' + str(call))
		bot.send_message(call.message.chat.id, too_old_msg, parse_mode='Markdown', reply_to_message_id=call.message.message_id)
		bot.answer_callback_query(call.id, text=too_old_msg, show_alert=True)
	else:
		try:
			# Try to ACK it in Zabbix
			zabbix_acknowledge(ack['eventid'], message)
			bot.send_message(call.message.chat.id, success_msg, parse_mode='Markdown', reply_to_message_id=call.message.message_id, disable_notification=True)
			bot.answer_callback_query(call.id, text=success_msg, show_alert=False)
		except:
			# For some reason we couldn't :(
			bot.send_message(call.message.chat.id, unsuccessful_msg, parse_mode='Markdown')
			bot.answer_callback_query(call.id, text=unsuccessful_msg, show_alert=True)
			raise


def zabbix_acknowledge(event_id, message):
	# Try to acknowledge an event in Zabbix
	zapi = ZabbixAPI(url=zabbix_url, user=zabbix_api_user, password=zabbix_api_password)
	zapi.do_request('event.acknowledge', {'eventids': event_id, 'message': message })

if __name__ == "__main__":
	# Start the bot
	bot.polling()