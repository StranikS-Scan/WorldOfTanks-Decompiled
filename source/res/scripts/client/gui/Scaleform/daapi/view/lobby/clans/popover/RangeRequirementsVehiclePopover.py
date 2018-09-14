# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/clans/popover/RangeRequirementsVehiclePopover.py
from gui.Scaleform.daapi.view.meta.RangeRequirementsVehiclePopoverMeta import RangeRequirementsVehiclePopoverMeta
from gui.Scaleform.locale.CLANS import CLANS
from helpers import i18n

class RangeRequirementsVehiclePopover(RangeRequirementsVehiclePopoverMeta):

    def __init__(self, _):
        super(RangeRequirementsVehiclePopover, self).__init__()

    def _populate(self):
        super(RangeRequirementsVehiclePopover, self)._populate()
        self.__update()

    def __update(self):
        data = {'titleText': i18n.makeString(CLANS.REQUIREMENTSVEHICLEPOPOVER_TITLE),
         'messageText': i18n.makeString(CLANS.REQUIREMENTSVEHICLEPOPOVER_AVAILABLEFORBATTLE),
         'blocksData': [{'labelText': i18n.makeString(CLANS.LABELTIPS_NATION),
                         'settingRosterVO': self.__makeSLotData(0)}, {'labelText': i18n.makeString(CLANS.LABELTIPS_TYPE),
                         'settingRosterVO': self.__makeSLotData(1)}, {'labelText': i18n.makeString(CLANS.LABELTIPS_LEVEL),
                         'settingRosterVO': self.__makeSLotData(2)}]}
        self.as_setDataS(data)

    def __makeSLotData(self, idx):
        return {'nationIDRange': ['ussr',
                           'germany',
                           'usa',
                           'france',
                           'uk',
                           'czech',
                           'china',
                           'japan'] if idx == 0 else [],
         'vLevelRange': [6, 8] if idx == 1 else [],
         'vTypeRange': ['lightTank',
                        'mediumTank',
                        'heavyTank',
                        'AT-SPG',
                        'SPG'] if idx == 2 else []}
