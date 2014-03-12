# -*- coding: utf-8 -*-
"""
A demo script that shows how to utilize api. It checks if hero is loosing health and
if health is lower than some limit than tries to use help for hero.

Usage:
  python demo_bot 'youraddr@mail.domain'

"""
import sys
import keyring
import getpass
import time
from os.path import expanduser

from thetaleapi import TheTaleApi

SERVICE = 'the-tale-api'
LOW_HEALTH = 120
NO_TIME_TO_CHECK_HEALTH = 50
SLEEP_TIME = 18
MIN_ENERGY = 2

import logging

logger = logging.getLogger(__name__)


def get_hero(state):
    return state['account']['hero']


def get_hp(state):
    return get_hero(state)['base']['health']


def get_max_hp(state):
    return get_hero(state)['base']['max_health']


def get_energy(state):
    return get_hero(state)['base']['health']


def simple_bot(api, action=None):
    state = api.get_game_info()['data']
    if state['mode'] == 'pve':

        current_health = get_hp(state)
        should_help = (
            current_health <= LOW_HEALTH
            # possibly should also check hero['action'] ???
        )
        be_generous = (
            current_health <= 0.6 * get_max_hp(state) and
            get_energy(state) >= 8
        )
        logger.info(u"Current hero's health: {0}".format(current_health))

        if should_help or action == 'check':
            if current_health <= NO_TIME_TO_CHECK_HEALTH:
                # no time to check if it's a battle or not
                if get_energy(state) >= MIN_ENERGY:
                    logger.warning(u'Helping hero')
                    api.use_help()
                return
            old_health = current_health

            # it's hard to parse hero['action'] now, so let's wait and check if health is reduced
            logger.debug(u'Waiting one turn')
            time.sleep(SLEEP_TIME)
            state = api.get_game_info()['data']

            current_health = get_hp(state)
            logger.info(u"Current hero's health: {0}".format(current_health))
            if current_health < old_health:
                logging.warning(u'Hero is loosing health')
                realy_heal = (
                    should_help and get_energy(state) >= MIN_ENERGY
                    or be_generous
                )
                if realy_heal:
                    logger.warning(u'Helping hero')
                    api.use_help()


if __name__ == '__main__':
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler(expanduser('./.the-tale.log'))

    logger.addHandler(console)
    logger.addHandler(file_handler)
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
    file_handler.close()
