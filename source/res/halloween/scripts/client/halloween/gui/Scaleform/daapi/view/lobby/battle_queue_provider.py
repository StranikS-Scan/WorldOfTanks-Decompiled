# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/Scaleform/daapi/view/lobby/battle_queue_provider.py
from gui.Scaleform import MENU
from gui.shared.formatters import text_styles
from helpers.i18n import makeString
from gui.Scaleform.locale.ITEM_TYPES import ITEM_TYPES
from gui.Scaleform.daapi.view.lobby.battle_queue import RandomQueueProvider
from CurrentVehicle import g_currentVehicle
from gui.shared.gui_items.Vehicle import VEHICLE_CLASS_NAME
_HTMLTEMP_PLAYERSLABEL = 'html_templates:lobby/queue/playersLabel'

class HalloweenQueueProvider(RandomQueueProvider):

    def needAdditionalInfo(self):
        if self._needAdditionalInfo is None:
            vehicle = g_currentVehicle.item
            self._needAdditionalInfo = vehicle is not None and vehicle.type == VEHICLE_CLASS_NAME.SPG
        return self._needAdditionalInfo

    def additionalInfo(self):
        return text_styles.gold(makeString(MENU.PREBATTLE_WAITINGTIMEWARNING))


class HalloweenWheeledVehiclesQueueProvider(RandomQueueProvider):
    TYPES_ORDERED = (('lightTank', ITEM_TYPES.VEHICLE_TAGS_LIGHT_TANK_NAME),)

    def needAdditionalInfo(self):
        return True

    def additionalInfo(self):
        return text_styles.gold(makeString(MENU.PREBATTLE_EVENTWHEELEDVEHICLESWARNING))

    def getLayoutStr(self):
        pass

    def getTankName(self, vehicle):
        return vehicle.shortUserName + self.tankNameLabelStr

    @property
    def timerLabelStr(self):
        pass

    @property
    def tankNameLabelStr(self):
        pass
