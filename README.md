zabbix-telegram-bot: Simple Zabbix Telegram bot
===============================================

# Requirements:
* requests
* py-zabbix (pip install py-zabbix)
* configparser
* PyTelegramAPI

# Usage:
## tg_sender.py
`tg_sender.py` is used to send a notification from Zabbix to a Telegram group defined in tgbot.conf.

* Obtain your API token from @BotFather and set `api_token` in tgbot.conf `globals`.
* Obtain your Groups ID (looks like a negative number, you can use `@get_id_bot` for this) for the groups you want to post events to.
* Set `zabbix_url`, `zabbix_api_user` and `zabbix_api_pass` in tgbot.conf `globals`.
* Set zabbix_description for this Zabbix instance (e.g. 'Lab Zabbix server`).
* Set your Telegram group aliases in the `[groups]` section (see examples).
* To send triggers to a Telegram group configure a Zabbix action as such: `tg_sender.py -i {EVENT.ID} -t {EVENT.VALUE} -s {EVENT.SEVERITY} -S {EVENT.STATUS} -g <group alias defined in tgbot.conf> [-l level]`, where:
  - `-i` is the Zabbix event ID
  - `-t` is the Zabbix event value (as in, text)
  - `-s` is the Zabbix event severity (e.g. 'Average')
  - `-S` is the Zabbix event status (e.g. 'PROBLEM', or 'OK')
  - `-l` is the notification level.

 Currently the notification levels are defined as such:
   - Anything lower than `0` wouldn't sound notifications.
   - Anything lower than `-9` will not send a notification altogether. (mainly for testing).

## tg_receiver.py
`tg_receiver.py` is a simple script that acknowledges an event in Zabbix with predefined message each time a user hits the 'Acknowledge' button under that event in Telegram.

## Config syntax:
### `globals` section:
  - `globals.api_token`: Telegram Bot API token for your bot.
  - `globals.ignore_older_than_mins` - Bot wouldn't relay acknowledges for messages that were posted by `tg_sender.py` earlier than `ignore_older_than_mins` minutes ago.

### `zabbix` section
  - `zabbix.zabbix_url` - Your Zabbix server URL.
  - `zabbix.zabbix_api_user` - Your Zabbix API username. Needs to be in the *API Access* group.
  - `zabbix.zabbix_api_password` - Password for your Zabbix API username.

### `severities` section:
The `severities` section is used to define the *default* notification levels for events with this severity. To use this, currently, this severity needs to exist in Zabbix! (so if you use non-default severities, you need to change these values). These values can also be overriden per-invokation with the `-l` command line option for `tg_sender.py`.
At present, the behaviour is:
  - Anything lower than `0` wouldn't sound notifications.
  - Anything lower than `-9` won't get sent out at all, mainly useful for testing or overriding the action for specific event.

### `groups` section:
This section holds defined group aliases for the `-g` option. You need to obtain your Groups ID somehow (e.g. via the `@get_id_bot` Telegram bot).

### `limits` section:
*TODO*