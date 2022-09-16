# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/comp7/shared.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl import backport
from gui.impl.gen import R
from gui.periodic_battles.models import AlertData, PeriodType
from gui.shared.formatters import text_styles
from gui.shared.formatters.time_formatters import getTillTimeByResource
from gui.shared.utils.functions import makeTooltip

class Comp7AlertData(AlertData):
    _RES_ROOT = R.strings.comp7.alertMessage
    _RES_REASON_ROOT = R.strings.comp7.noVehicles.text
    _PERIOD_TYPES_WITH_BUTTON = (PeriodType.NOT_AVAILABLE,
     PeriodType.STANDALONE_NOT_AVAILABLE,
     PeriodType.NOT_AVAILABLE_END,
     PeriodType.NOT_SET,
     PeriodType.STANDALONE_NOT_SET)
    _PERIOD_TYPES_PRIME_ALERT = (PeriodType.AVAILABLE,
     PeriodType.NOT_AVAILABLE_END,
     PeriodType.NOT_SET,
     PeriodType.ALL_NOT_SET,
     PeriodType.STANDALONE_NOT_SET,
     PeriodType.NOT_AVAILABLE,
     PeriodType.ALL_NOT_AVAILABLE,
     PeriodType.STANDALONE_NOT_AVAILABLE,
     PeriodType.ALL_NOT_AVAILABLE_END,
     PeriodType.STANDALONE_NOT_AVAILABLE_END,
     PeriodType.AFTER_SEASON)
    _PERIOD_TYPES_WITHOUT_TOOLTIP = (PeriodType.ALL_NOT_SET, PeriodType.ALL_NOT_AVAILABLE_END, PeriodType.AFTER_SEASON)

    @classmethod
    def _getTooltip(cls, periodInfo):
        return None if periodInfo.periodType in cls._PERIOD_TYPES_WITHOUT_TOOLTIP else TOOLTIPS_CONSTANTS.COMP7_CALENDAR_DAY_INFO

    @classmethod
    def constructForBan(cls, duration):
        tillTime = getTillTimeByResource(duration, cls._RES_ROOT.timeLeft, removeLeadingZeros=True)
        resShortCut = R.strings.menu.headerButtons.fightBtn.tooltip.comp7BanIsSet
        header = backport.text(resShortCut.header())
        body = backport.text(resShortCut.body())
        return cls(alertIcon=backport.image(R.images.gui.maps.icons.library.alertBigIcon()), buttonVisible=False, statusText=backport.text(cls._RES_ROOT.temporaryBan(), expiryTime=tillTime), isSimpleTooltip=True, tooltip=makeTooltip(header, body))

    @classmethod
    def constructForOffline(cls):
        return cls(alertIcon=backport.image(R.images.gui.maps.icons.library.alertBigIcon()), buttonVisible=False, statusText=text_styles.vehicleStatusCriticalText(backport.text(cls._RES_ROOT.modeOffline())), shadowFilterVisible=True)
