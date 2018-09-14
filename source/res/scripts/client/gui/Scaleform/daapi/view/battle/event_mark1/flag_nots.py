# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event_mark1/flag_nots.py
from gui.Scaleform.daapi.view.meta.FlagNotificationMeta import FlagNotificationMeta
from gui.battle_control.controllers.event_mark1.bonus_ctrl import IFlagBonusNotificationView, STATES
from gui.Scaleform.locale.INGAME_GUI import INGAME_GUI
from helpers.i18n import makeString
from helpers import time_utils

class _ICONS(object):
    ALLY_AMMO = 'allyAmmo'
    ALLY_BOMB = 'allyBomb'
    ALLY_REPAIR = 'allyRepair'
    BONUS_BIG_GUN = 'bonusBigGun'
    BONUS_MACHINE_GUN = 'bonusMachineGun'


_STATE_DEFENCE_BOMB_COUNT_HIDE = 'defenderDeliveredBombHide'

class EventMark1FlagNotification(FlagNotificationMeta, IFlagBonusNotificationView):

    def __init__(self):
        super(EventMark1FlagNotification, self).__init__()
        self.__isBombCounterDisplayed = False

    def showState(self, state):
        if state == STATES.DEFENCE_BOMB_DELIVERED:
            self.__isBombCounterDisplayed = True
        else:
            self.as_setStateS(state)

    def carriedFlagDropped(self):
        self.as_hideS()

    def showBombCountDown(self, timeLeft):
        if self.__isBombCounterDisplayed:
            self.__updateExplosionInfo(timeLeft)

    def hideBombCountDown(self):
        if self.__isBombCounterDisplayed:
            self.as_setStateS(_STATE_DEFENCE_BOMB_COUNT_HIDE)
            self.__isBombCounterDisplayed = False

    def _populate(self):
        super(EventMark1FlagNotification, self)._populate()
        self.as_setupS(self.__getStates())

    def __updateExplosionInfo(self, timeLeft):
        title = makeString(INGAME_GUI.MARK1_BOMB_DELIVERED)
        body = time_utils.getTimeLeftFormat(timeLeft)
        self.as_updateFieldsS(STATES.DEFENCE_BOMB_DELIVERED, title, body)

    @staticmethod
    def __getStates():
        return [{'state': STATES.ATTACK_REPAIR_TAKEN,
          'title': makeString(INGAME_GUI.MARK1_REPAIR_TITLE),
          'body': makeString(INGAME_GUI.MARK1_REPAIR_BODY),
          'typeID': 1,
          'isAutoHided': False,
          'icon': _ICONS.ALLY_REPAIR},
         {'state': STATES.ATTACK_REPAIR_DELIVERED,
          'title': makeString(INGAME_GUI.MARK1_REPAIR_DELIVERED_TITLE),
          'body': makeString(INGAME_GUI.MARK1_REPAIR_DELIVERED_BODY),
          'typeID': 1,
          'isAutoHided': True,
          'icon': _ICONS.ALLY_REPAIR},
         {'state': STATES.DEFENCE_BOMB_TAKEN,
          'title': makeString(INGAME_GUI.MARK1_BOMB_DEFENCE_TITLE),
          'body': makeString(INGAME_GUI.MARK1_BOMB_DEFENCE_BODY),
          'typeID': 3,
          'isAutoHided': False,
          'icon': _ICONS.ALLY_BOMB},
         {'state': STATES.DEFENCE_BOMB_DELIVERED,
          'title': makeString(INGAME_GUI.MARK1_BOMB_DELIVERED),
          'body': '',
          'typeID': 3,
          'isAutoHided': False,
          'icon': _ICONS.ALLY_BOMB},
         {'state': _STATE_DEFENCE_BOMB_COUNT_HIDE,
          'title': makeString(INGAME_GUI.MARK1_BOMB_DELIVERED),
          'body': '',
          'typeID': 3,
          'isAutoHided': True,
          'icon': _ICONS.ALLY_BOMB},
         {'state': STATES.BIG_GUN_TAKEN,
          'title': makeString(INGAME_GUI.MARK1_BIGGUN_TITLE),
          'body': makeString(INGAME_GUI.MARK1_BIGGUN_BODY),
          'typeID': 4,
          'isAutoHided': True,
          'icon': _ICONS.BONUS_BIG_GUN},
         {'state': STATES.MACHINE_GUN_TAKEN,
          'title': makeString(INGAME_GUI.MARK1_MACHINEGUN_TITLE),
          'body': makeString(INGAME_GUI.MARK1_MACHINEGUN_BODY),
          'typeID': 5,
          'isAutoHided': True,
          'icon': _ICONS.BONUS_MACHINE_GUN}]
