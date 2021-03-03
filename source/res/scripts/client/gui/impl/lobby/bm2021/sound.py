# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/bm2021/sound.py
from enum import Enum
from sound_gui_manager import CommonSoundSpaceSettings
from gui.impl.gen.resources import R
from gui.impl import backport

class States(Enum):
    BLACK_MARKET = 'STATE_black_market'
    HANGAR_PLACE = 'STATE_hangar_place'
    HANGAR_OVERLAY = 'STATE_overlay_hangar_general'


class StateValues(Enum):
    HANGAR_PLACE_GARAGE = 'STATE_hangar_place_garage'
    HANGAR_PLACE_SHOP = 'STATE_hangar_place_shop'
    OVERLAY_HANGAR_GENERAL_ON = 'STATE_overlay_hangar_general_on'
    OVERLAY_HANGAR_GENERAL_OFF = 'STATE_overlay_hangar_general_off'
    BLACK_MARKET_STATE_ITEM = 'STATE_black_market_item'
    BLACK_MARKET_STATE_DEFAULT = 'STATE_black_market_default'


def _makeOverlaySoundSpace(enterEvent):
    return CommonSoundSpaceSettings(name='black_market_overlay', entranceStates={States.HANGAR_OVERLAY.value: StateValues.OVERLAY_HANGAR_GENERAL_ON.value}, exitStates={States.HANGAR_OVERLAY.value: StateValues.OVERLAY_HANGAR_GENERAL_OFF.value}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent=enterEvent, exitEvent='')


BLACK_MARKET_OVERLAY_SOUND_SPACE = _makeOverlaySoundSpace('')
BLACK_MARKET_AWARD_SOUND_SPACE = _makeOverlaySoundSpace(backport.sound(R.sounds.shop_buy_tank()))
BLACK_MARKET_CONFIRM_SOUND_SPACE = _makeOverlaySoundSpace(backport.sound(R.sounds.black_market_mini_award()))
BLACK_MARKET_ITEM_SOUND_SPACE = CommonSoundSpaceSettings(name='black_market_item', entranceStates={States.BLACK_MARKET.value: StateValues.BLACK_MARKET_STATE_ITEM.value,
 States.HANGAR_PLACE.value: StateValues.HANGAR_PLACE_SHOP.value}, exitStates={States.BLACK_MARKET.value: StateValues.BLACK_MARKET_STATE_DEFAULT.value,
 States.HANGAR_PLACE.value: StateValues.HANGAR_PLACE_GARAGE.value}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent=backport.sound(R.sounds.black_market_enter()), exitEvent=backport.sound(R.sounds.black_market_exit()))
