# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/FortSettingsVacationPopover.py
from adisp import process
from debug_utils import LOG_DEBUG
from helpers import i18n, time_utils
from gui import SystemMessages
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.daapi.view.meta.FortSettingsVacationPopoverMeta import FortSettingsVacationPopoverMeta
from gui.Scaleform.daapi.view.lobby.popover.SmartPopOverView import SmartPopOverView
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortViewHelper import FortViewHelper
from gui.Scaleform.framework import AppRef
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.shared.fortifications.context import VacationCtx
from gui.shared.utils import flashObject2Dict

class FortSettingsVacationPopover(View, FortSettingsVacationPopoverMeta, SmartPopOverView, FortViewHelper, AppRef):

    def __init__(self, ctx = None):
        super(FortSettingsVacationPopover, self).__init__()
        self._orderID = str(ctx.get('data'))

    def onApply(self, data):
        self.__setup(data.startVacation, data.endVacation)

    def onWindowClose(self):
        self.destroy()

    def _populate(self):
        super(FortSettingsVacationPopover, self)._populate()
        self.__setData()
        self.__setTexts()

    def _dispose(self):
        super(FortSettingsVacationPopover, self)._dispose()

    @process
    def __setup(self, timeStart, timeEnd):
        result = yield self.fortProvider.sendRequest(VacationCtx(timeStart, timeEnd, waitingID='fort/settings'))
        if result:
            vacationPeriod = '%s - %s' % (time_utils.getDateTimeInLocal(timeStart), time_utils.getDateTimeInLocal(timeEnd))
            SystemMessages.g_instance.pushI18nMessage(SYSTEM_MESSAGES.FORTIFICATION_VACATIONSET, vacationPeriod=vacationPeriod, type=SystemMessages.SM_TYPE.Warning)
            self.destroy()

    def __setTexts(self):
        self.as_setTextsS({'descriptionText': i18n.makeString(FORTIFICATIONS.SETTINGSVACATIONPOPOVER_DESCRIPTION),
         'vacationStart': i18n.makeString(FORTIFICATIONS.SETTINGSVACATIONPOPOVER_VACATIONSTART),
         'vacationDuration': i18n.makeString(FORTIFICATIONS.SETTINGSVACATIONPOPOVER_VACATIONDURATION),
         'ofDays': i18n.makeString(FORTIFICATIONS.SETTINGSVACATIONPOPOVER_OFDAYS),
         'applyBtnLabel': i18n.makeString(FORTIFICATIONS.SETTINGSVACATIONPOPOVER_APPLYBUTTONLABEL),
         'cancelBtnLabel': i18n.makeString(FORTIFICATIONS.SETTINGSVACATIONPOPOVER_CANCELBUTTONLABEL)})

    def __setData(self):
        self.as_setDataS({'isAmericanStyle': False})
