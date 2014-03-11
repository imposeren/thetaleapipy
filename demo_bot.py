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

from thetaleapi import TheTaleApi

SERVICE = 'the-tale-api'
LOW_HEALTH = 120
NO_TIME_TO_CHECK_HEALTH = 50
SLEEP_TIME = 18
MIN_ENERGY = 4


def simple_bot(api, action=None):
    state = api.get_game_info()['data']
    if state['mode'] == 'pve':
        hero = state['account']['hero']
        current_health = hero['base']['health']
        should_help = (
            current_health <= LOW_HEALTH
            # possibly should also check hero['action'] ???
        )
        print(u"Current hero's health: {0}".format(current_health))

        if should_help or action == 'check':
            if current_health <= NO_TIME_TO_CHECK_HEALTH:
                # no time to check if it's a battle or not
                if hero['energy']['value'] >= MIN_ENERGY:
                    print(u'Helping hero')
                    api.use_help()
                return
            old_health = current_health

            # it's hard to parse hero['action'] now, so let's wait and check if health is reduced
            print(u'Waiting one turn')
            time.sleep(SLEEP_TIME)
            state = api.get_game_info()['data']

            hero = state['account']['hero']
            current_health = hero['base']['health']
            print(u"Current hero's health: {0}".format(current_health))
            if current_health < old_health:
                print(u'Hero is loosing health')
                if should_help and hero['energy']['value'] >= MIN_ENERGY:
                    print(u'Helping hero')
                    api.use_help()


if __name__ == '__main__':
    if len(sys.argv) == 3:
        email, action = sys.argv[1:3]
    else:
        email, action = sys.argv[1], None

    password = keyring.get_password(SERVICE, email)
    if password is None:
        password = getpass.getpass()
        keyring.set_password(SERVICE, email, password)
    api = TheTaleApi()
    api.auth(email, password)
    simple_bot(api, action)


