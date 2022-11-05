# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/feature/models/common.py
from gui.impl import backport
from gui.impl.gen import R
from gui.periodic_battles.models import AlertData, PeriodType
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.formatters import text_styles
from gui.shared.utils.decorators import ReprInjector
from season_common import GameSeason

@ReprInjector.simple('state', 'rightBorder', 'primeDelta')
class FunSubModesStatus(object):
    __slots__ = ('state', 'rightBorder', 'primeDelta')

    def __init__(self, state, rightBorder=None, primeDelta=None):
        self.rightBorder = rightBorder if rightBorder is not None else -1
        self.primeDelta = primeDelta if primeDelta is not None else 0
        self.state = state
        return


class FunRandomAlertData(AlertData):
    _RES_ROOT = R.strings.fun_random.alertMessage
    _PERIOD_TYPES_PRIME_ALERT = (PeriodType.AVAILABLE,
     PeriodType.AFTER_CYCLE,
     PeriodType.STANDALONE_NOT_SET,
     PeriodType.NOT_SET,
     PeriodType.ALL_NOT_SET,
     PeriodType.STANDALONE_NOT_AVAILABLE,
     PeriodType.NOT_AVAILABLE,
     PeriodType.NOT_AVAILABLE_END,
     PeriodType.ALL_NOT_AVAILABLE,
     PeriodType.STANDALONE_NOT_AVAILABLE_END)

    @classmethod
    def constructNoVehicles(cls):
        return cls(alertIcon=backport.image(R.images.gui.maps.icons.library.alertBigIcon()), buttonLabel=backport.text(cls._RES_ROOT.button.moreInfo()), buttonVisible=True, statusText=text_styles.vehicleStatusCriticalText(backport.text(cls._RES_ROOT.unsuitableVehicles())), shadowFilterVisible=True, tooltip='', isSimpleTooltip=True)

    @classmethod
    def _getTooltip(cls, _):
        return TOOLTIPS_CONSTANTS.FUN_RANDOM_CALENDAR_DAY


class FunRandomSeason(GameSeason):

    def __init__(self, cycleInfo, seasonData, assetsPointer):
        super(FunRandomSeason, self).__init__(cycleInfo, seasonData)
        self.__assetsPointer = assetsPointer

    def getUserName(self):
        defaultLocRes = R.strings.fun_random.subModes.undefined
        return backport.text(R.strings.fun_random.subModes.dyn(self.__assetsPointer, defaultLocRes).userName())
