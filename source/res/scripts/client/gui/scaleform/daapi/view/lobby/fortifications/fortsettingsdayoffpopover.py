# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/FortSettingsDayoffPopover.py
from FortifiedRegionBase import NOT_ACTIVATED
from adisp import process
from gui import SystemMessages
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortViewHelper import FortViewHelper
from gui.Scaleform.daapi.view.meta.FortSettingsDayoffPopoverMeta import FortSettingsDayoffPopoverMeta
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared.formatters import text_styles
from gui.shared.fortifications.context import OffDayCtx
from gui.shared.fortifications.fort_helpers import adjustOffDayToUTC
from helpers import i18n

class FortSettingsDayoffPopover(FortViewHelper, FortSettingsDayoffPopoverMeta):

    def __init__(self, _ = None):
        super(FortSettingsDayoffPopover, self).__init__()

    def onApply(self, offDay):
        self.__setup(offDay)

    def onWindowClose(self):
        self.destroy()

    def __getDataObject(self):
        fort = self.fortCtrl.getFort()
        selectedDay = fort.getLocalOffDay()
        return {'currentDayOff': selectedDay,
         'daysList': self._getDayoffsList()}

    def _populate(self):
        super(FortSettingsDayoffPopover, self)._populate()
        description = text_styles.standard(i18n.makeString(FORTIFICATIONS.SETTINGSDAYOFFPOPOVER_DESCRIPTION))
        dayOffText = text_styles.main(i18n.makeString(FORTIFICATIONS.SETTINGSDAYOFFPOPOVER_DROPDOWNDESCRIPTION))
        self.as_setDescriptionsTextS(description, dayOffText)
        applyButtonText = i18n.makeString(FORTIFICATIONS.SETTINGSDAYOFFPOPOVER_APPLYBUTTONLABEL)
        cancelButtonText = i18n.makeString(FORTIFICATIONS.SETTINGSDAYOFFPOPOVER_CANCELBUTTONLABEL)
        self.as_setButtonsTextS(applyButtonText, cancelButtonText)
        enabledButtonTooltip = TOOLTIPS.FORTIFICATION_FORTSETTINGSDAYOFFPOPOVER_APPLY_ENABLED
        disabledButtonTooltip = TOOLTIPS.FORTIFICATION_FORTSETTINGSDAYOFFPOPOVER_APPLY_DISABLED
        self.as_setButtonsTooltipsS(enabledButtonTooltip, disabledButtonTooltip)
        self.as_setDataS(self.__getDataObject())

    @process
    def __setup(self, offDay):
        offDayUTC = offDay
        if offDay != NOT_ACTIVATED:
            offDayUTC = adjustOffDayToUTC(offDay, self.fortCtrl.getFort().getLocalDefenceHour()[0])
        result = yield self.fortProvider.sendRequest(OffDayCtx(offDayUTC, waitingID='fort/settings'))
        if result:
            if offDay == NOT_ACTIVATED:
                SystemMessages.g_instance.pushI18nMessage(SYSTEM_MESSAGES.FORTIFICATION_DEFENCEHOURSET_NOOFFDAY, type=SystemMessages.SM_TYPE.Warning)
            else:
                dayOffString = i18n.makeString(MENU.datetime_weekdays_full(str(offDay + 1)))
                SystemMessages.g_instance.pushI18nMessage(SYSTEM_MESSAGES.FORTIFICATION_DEFENCEHOURSET_OFFDAY, offDay=dayOffString, type=SystemMessages.SM_TYPE.Warning)
