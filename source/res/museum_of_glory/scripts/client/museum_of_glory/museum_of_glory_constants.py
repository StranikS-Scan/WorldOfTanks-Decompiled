# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: museum_of_glory/scripts/client/museum_of_glory/museum_of_glory_constants.py
MUSEUM_OF_GLORY_CONFIG = 'museum_of_glory_config'
MUSEUM_OF_GLORY = 'MuseumOfGlorySettings'
AUDIO_GUIDE_ENABLED = 'AudioGuideEnabled'
IS_INTRO_SEEN = 'IsIntroSeen'
LAST_SEEN_INDEX = 'lastSeenIndex'
ACCOUNT_DEFAULT_SETTINGS = {MUSEUM_OF_GLORY: {AUDIO_GUIDE_ENABLED: True,
                   IS_INTRO_SEEN: False,
                   LAST_SEEN_INDEX: 0}}
CHARACTERISTIC_FIELDS = ['mass',
 'armor',
 'caliber',
 'weapon',
 'power',
 'speed',
 'crew',
 'combatCrew']

class MuseumOfGlorySoundEvents(object):
    SOUND_EVENT_PREFIX = 'h16_mt_museum_vo_guide_'
    WELCOME_SOUND_EVENT = 'h16_mt_museum_vo_guide_welcome'
    STOP_SOUND_EVENT = 'h16_mt_museum_vo_guide_stop'
    PAUSE_SOUND_EVENT = 'h16_mt_museum_vo_guide_pause'
    RESUME_SOUND_EVENT = 'h16_mt_museum_vo_guide_resume'
    EXCURSION_MUTE = 'h16_mt_museum_vo_guide_mute'
    EXCURSION_UNMUTE = 'h16_mt_museum_vo_guide_unmute'
    STATE_PLACE = 'STATE_hangar_place'
    STATE_PLACE_GARAGE = 'STATE_hangar_place_garage'
    EXCURSION_STATE = 'STATE_ext_mt_museum_excursion'
    DATES_STATE = 'STATE_ext_mt_museum_dates'
    STATES = {EXCURSION_STATE: ['STATE_ext_mt_museum_excursion_off', 'STATE_ext_mt_museum_excursion_on']}
