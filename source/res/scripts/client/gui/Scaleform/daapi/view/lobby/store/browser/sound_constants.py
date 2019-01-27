# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/store/browser/sound_constants.py
from gui.Scaleform.framework.entities.View import CommonSoundSpaceSettings
from shared_utils import CONST_CONTAINER

class SOUNDS(CONST_CONTAINER):
    COMMON_SOUND_SPACE = 'IngameShop'
    VEHICLE_PREVIEW_SOUND_SPACE = 'IngameShopVehiclePreview'
    STATE_PLACE = 'STATE_hangar_place'
    STATE_PLACE_SHOP = 'STATE_hangar_place_shop'
    STATE_PLACE_VEHICLE_PREVIEW = 'STATE_hangar_place_shop_preview'
    ENTER = 'shop_enter'
    EXIT = 'shop_exit'


INGAMESHOP_SOUND_SPACE = CommonSoundSpaceSettings(name=SOUNDS.COMMON_SOUND_SPACE, entranceStates={SOUNDS.STATE_PLACE: SOUNDS.STATE_PLACE_SHOP}, exitStates={}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent=SOUNDS.ENTER, exitEvent=SOUNDS.EXIT)
INGAMESHOP_PREVIEW_SOUND_SPACE = CommonSoundSpaceSettings(name=SOUNDS.VEHICLE_PREVIEW_SOUND_SPACE, entranceStates={SOUNDS.STATE_PLACE: SOUNDS.STATE_PLACE_VEHICLE_PREVIEW}, exitStates={}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent='', exitEvent='', parentSpace=SOUNDS.COMMON_SOUND_SPACE)
