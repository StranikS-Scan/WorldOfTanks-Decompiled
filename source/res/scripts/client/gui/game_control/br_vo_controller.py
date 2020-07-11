# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/br_vo_controller.py
import BigWorld
import WWISE
import nations
from constants import CURRENT_REALM
from gui.battle_control import avatar_getter
from items import vehicles
from helpers import dependency
from skeletons.gui.game_control import IBootcampController
_RU_REALMS = ('DEV', 'QA', 'RU')
_SWITCH_RU = 'SWITCH_ext_BR_vo_language'
_SWITCH_RU_ON = 'SWITCH_ext_BR_vo_language_RU'
_SWITCH_RU_OFF = 'SWITCH_ext_BR_vo_language_nonRU'
_SWITCH_CHAR = 'SWITCH_ext_BR_vo_char'
_SWITCH_CHAR_FOR_NATIONS = {'ussr': 'SWITCH_ext_BR_vo_char_RU',
 'usa': 'SWITCH_ext_BR_vo_char_US',
 'germany': 'SWITCH_ext_BR_vo_char_GE',
 'france': 'SWITCH_ext_BR_vo_char_FR',
 'uk': 'SWITCH_ext_BR_vo_char_UK'}

class BRVoiceOverController(object):
    __bcc = dependency.descriptor(IBootcampController)

    def __init__(self):
        super(BRVoiceOverController, self).__init__()
        self.__isActive = False

    def init(self):
        WWISE.WW_setRealm(CURRENT_REALM)

    def fini(self):
        pass

    def activate(self):
        self.__isActive = True

    def deactivate(self):
        self.__isActive = False

    def onAvatarBecomePlayer(self):
        if self.__bcc.isInBootcampAccount() or self.__bcc.isInBootcamp():
            return
        else:
            avatar = BigWorld.player()
            playerVehicle = avatar.vehicle
            if playerVehicle is not None:
                self.__updateBattleSwitches(playerVehicle)
            else:
                avatar.onVehicleEnterWorld += self.__onVehicleEnterWorld
            return

    def __onVehicleEnterWorld(self, vehicle):
        if vehicle.id == avatar_getter.getPlayerVehicleID():
            BigWorld.player().onVehicleEnterWorld -= self.__onVehicleEnterWorld
            self.__updateBattleSwitches(vehicle)

    def __updateBattleSwitches(self, vehicle):
        if self.__isActive:
            compactDescr = vehicle.typeDescriptor.type.compactDescr
            WWISE.WW_setSwitch(_SWITCH_CHAR, self.__compactDescrToSwitchValue(compactDescr))
            WWISE.WW_setSwitch(_SWITCH_RU, self.__switchRuValue)

    def __compactDescrToSwitchValue(self, descr):
        _, nationIdx, _ = vehicles.parseIntCompactDescr(descr)
        nationName = nations.NAMES[nationIdx]
        return _SWITCH_CHAR_FOR_NATIONS[nationName]

    @property
    def __isRuRealm(self):
        return CURRENT_REALM in _RU_REALMS

    @property
    def __switchRuValue(self):
        return _SWITCH_RU_ON if self.__isRuRealm else _SWITCH_RU_OFF
