# -*- coding: utf-8 -*-
"""
A demo script that shows how to utilize api. It checks if hero is loosing health and
if health is lower than some limit than tries to use help for hero.

Usage:
  python demo_bot.py 'youraddr@mail.domain'

this script can be used in cron if you will specify env variables like:
DISPLAY and DBUS_SESSION_BUS_ADDRESS

"""
import sys
import keyring
import getpass
import time
#from os.path import expanduser

from thetaleapi import TheTaleApi

SERVICE = 'the-tale-api'
LOW_HEALTH = 280
NO_TIME_TO_CHECK_HEALTH = 50
SLEEP_TIME = 18
MIN_ENERGY = 4
GENEROUS_ENERGY = MIN_ENERGY + 4
GENEROUS_HP_FRACTION = 0.6
BONUS_ENERGY_MINIMUM = 10

import logging

logger = logging.getLogger(__name__)


def get_hero(state):
    return state['account']['hero']


def get_hp(state):
    return get_hero(state)['base']['health']


def get_max_hp(state):
    return get_hero(state)['base']['max_health']


def get_energy(state, kind='value'):
    return get_hero(state)['energy'][kind]


def simple_bot(api, action=None):
    state = api.get_game_info()['data']
    if state['mode'] == 'pve':

        current_health = get_hp(state)
        should_help = (
            current_health <= LOW_HEALTH
            # possibly should also check hero['action'] ???
        )
        be_generous = (
            current_health <= GENEROUS_HP_FRACTION * get_max_hp(state) and
            get_energy(state) >= GENEROUS_ENERGY
        )
        logger.info(u"Current hero's health: {0}".format(current_health))
        logger.info(u"Current hero's position: {0}".format(get_hero(state)['position']))

        if should_help or action == 'check':
            if current_health <= NO_TIME_TO_CHECK_HEALTH:
                # no time to check if it's a battle or not
                if get_energy(state) >= MIN_ENERGY:
                    logger.warning(u'Helping hero')
                    api.use_help()
                elif current_health == 1 and get_energy(state, 'bonus') >= BONUS_ENERGY_MINIMUM:
                    logger.warning(u'Hero is dead. Helping...')
                    api.use_help()
                return None
            old_health = current_health

            # it's hard to parse hero['action'] now, so let's wait and check if health is reduced
            logger.debug(u'Waiting one turn')
            time.sleep(SLEEP_TIME)
            state = api.get_game_info()['data']

            current_health = get_hp(state)
            if current_health < old_health:
                realy_heal = (
                    should_help and get_energy(state) >= MIN_ENERGY
                    or be_generous
                )
                if realy_heal:
                    logger.warning(u'Hero is loosing health')
                    logger.warning(u"Current hero's health: {0}".format(current_health))
                    logger.warning(u'Helping hero')
                    api.use_help()


if __name__ == '__main__':
    console = logging.StreamHandler()
    console.setLevel(logging.WARNING)
    #file_handler = logging.FileHandler(expanduser('./.the-tale.log'))
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    #file_handler.setFormatter(formatter)
    console.setFormatter(formatter)

    logger.addHandler(console)
    #logger.addHandler(file_handler)
    logger.setLevel(logging.DEBUG)

    if len(sys.argv) == 3:
        email, action = sys.argv[1:3]
    else:
        email, action = sys.argv[1], None

    password = keyring.get_password(SERVICE, email)
    if password is None:
        password = getpass.getpass()
        keyring.set_password(SERVICE, email, password)
    api = TheTaleApi()
    auth_result = api.auth(email, password).json()
    if auth_result['status'] != 'ok':
        logger.error(auth_result)

    simple_bot(api, action)
    api.logout()
    #file_handler.close()
