# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/FortSettingsVacationPopover.py
from adisp import process
import fortified_regions
from gui.shared.fortifications.fort_helpers import adjustVacationToUTC
from helpers import i18n, time_utils
from gui import SystemMessages
from gui.Scaleform.daapi.view.meta.FortSettingsVacationPopoverMeta import FortSettingsVacationPopoverMeta
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortViewHelper import FortViewHelper
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.shared.fortifications.context import VacationCtx
SHOW_MAX_MONTH = 4

class FortSettingsVacationPopover(FortSettingsVacationPopoverMeta, FortViewHelper):

    def __init__(self, _ = None):
        super(FortSettingsVacationPopover, self).__init__()

    def onApply(self, data):
        self.__setup(data.startVacation, data.vacationDuration)

    def onWindowClose(self):
        self.destroy()

    def _populate(self):
        super(FortSettingsVacationPopover, self)._populate()
        self.__setData()
        self.__setTexts()

    @process
    def __setup(self, vacationStart, vacationDuration):
        vacationStartUTC, vacationDurationUTC = adjustVacationToUTC(vacationStart, vacationDuration * time_utils.ONE_DAY)
        result = yield self.fortProvider.sendRequest(VacationCtx(vacationStartUTC, vacationDurationUTC, waitingID='fort/settings'))
        if result:
            vacationPeriod = '%s - %s' % (time_utils.getDateTimeFormat(vacationStartUTC), time_utils.getDateTimeFormat(vacationStartUTC + vacationDurationUTC))
            SystemMessages.g_instance.pushI18nMessage(SYSTEM_MESSAGES.FORTIFICATION_VACATIONSET, vacationPeriod=vacationPeriod, type=SystemMessages.SM_TYPE.Warning)
        self.destroy()

    def __setTexts(self):
        self.as_setTextsS({'descriptionText': i18n.makeString(FORTIFICATIONS.SETTINGSVACATIONPOPOVER_DESCRIPTION),
         'vacationStartText': i18n.makeString(FORTIFICATIONS.SETTINGSVACATIONPOPOVER_VACATIONSTART),
         'vacationDurationText': i18n.makeString(FORTIFICATIONS.SETTINGSVACATIONPOPOVER_VACATIONDURATION),
         'ofDaysText': i18n.makeString(FORTIFICATIONS.SETTINGSVACATIONPOPOVER_OFDAYS),
         'applyBtnLabel': i18n.makeString(FORTIFICATIONS.SETTINGSVACATIONPOPOVER_APPLYBUTTONLABEL),
         'cancelBtnLabel': i18n.makeString(FORTIFICATIONS.SETTINGSVACATIONPOPOVER_CANCELBUTTONLABEL)})

    def __setData(self):
        dayStartUTC, _ = time_utils.getDayTimeBoundsForUTC(time_utils.getCurrentTimestamp())
        vacationStart = dayStartUTC + time_utils.ONE_DAY + fortified_regions.g_cache.minVacationPreorderTime
        self.as_setDataS({'startVacation': vacationStart,
         'vacationDuration': -1,
         'isAmericanStyle': False,
         'showMonth': SHOW_MAX_MONTH})
