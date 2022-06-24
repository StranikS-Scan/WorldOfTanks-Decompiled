# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/fun_random/fun_random_models.py
from gui.impl import backport
from gui.impl.gen import R
from gui.periodic_battles.models import AlertData
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.formatters import text_styles
from season_common import GameSeason

class FunRandomAlertData(AlertData):
    _RES_ROOT = R.strings.fun_random.alertMessage

    @classmethod
    def constructNoVehicles(cls):
        return cls(alertIcon=backport.image(R.images.gui.maps.icons.library.alertBigIcon()), buttonLabel=backport.text(cls._RES_ROOT.button.moreInfo()), buttonVisible=True, statusText=text_styles.vehicleStatusCriticalText(backport.text(cls._RES_ROOT.unsuitableVehicles())), shadowFilterVisible=True, tooltip='', isSimpleTooltip=True)

    @classmethod
    def _getTooltip(cls, _):
        return TOOLTIPS_CONSTANTS.FUN_RANDOM_CALENDAR_DAY


class FunRandomSeason(GameSeason):

    def __init__(self, cycleInfo, seasonData, eventID):
        super(FunRandomSeason, self).__init__(cycleInfo, seasonData)
        self.__eventID = eventID

    def getUserName(self):
        defaultLocRes = R.strings.fun_random.events.undefined
        return backport.text(R.strings.fun_random.events.num(self.__eventID, defaultLocRes).userName())
