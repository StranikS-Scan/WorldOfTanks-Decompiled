# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/FortSettingsDefenceHourPopover.py
import BigWorld
import constants
from adisp import process
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortViewHelper import FortViewHelper
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.daapi.view.meta.FortSettingsDefenceHourPopoverMeta import FortSettingsDefenceHourPopoverMeta
from gui.Scaleform.daapi.view.lobby.popover.SmartPopOverView import SmartPopOverView
from gui.Scaleform.framework import AppRef
from gui.shared.fortifications.context import DefenceHourCtx
from gui.shared.fortifications.fort_helpers import adjustDefenceHourToUTC
from helpers import i18n, time_utils
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui import SystemMessages
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES

class FortSettingsDefenceHourPopover(View, FortSettingsDefenceHourPopoverMeta, SmartPopOverView, FortViewHelper, AppRef):

    def __init__(self, ctx = None):
        super(FortSettingsDefenceHourPopover, self).__init__()

    def setTexts(self):
        data = {'descriptionText': i18n.makeString(FORTIFICATIONS.SETTINGSDEFENCEHOURPOPOVER_DESCRIPTION),
         'defenceHourText': i18n.makeString(FORTIFICATIONS.SETTINGSDEFENCEHOURPOPOVER_DEFENCEHOUR),
         'applyBtnLabel': i18n.makeString(FORTIFICATIONS.SETTINGSDEFENCEHOURPOPOVER_APPLYBUTTONLABEL),
         'cancelBtnLabel': i18n.makeString(FORTIFICATIONS.SETTINGSDEFENCEHOURPOPOVER_CANCELBUTTONLABEL)}
        self.as_setTextsS(data)

    def setData(self):
        skipValues = []
        if constants.IS_KOREA:
            skipValues = [0, 7]
        data = {'hour': self.fortCtrl.getFort().getLocalDefenceHour(),
         'skipValues': skipValues,
         'isWrongLocalTime': self._isWrongLocalTime()}
        self.as_setDataS(data)

    def onApply(self, defHour):
        self.__setup(defHour)

    def onWindowClose(self):
        self.destroy()

    def _populate(self):
        super(FortSettingsDefenceHourPopover, self)._populate()
        self.setData()
        self.setTexts()

    def _dispose(self):
        super(FortSettingsDefenceHourPopover, self)._dispose()

    @process
    def __setup(self, defHour):
        defHourUTC = adjustDefenceHourToUTC(defHour)
        result = yield self.fortProvider.sendRequest(DefenceHourCtx(defHourUTC, waitingID='fort/settings'))
        if result:
            start = time_utils.getTimeTodayForUTC(defHourUTC)
            finish = time_utils.getTimeTodayForUTC(defHourUTC + 1)
            defenceHourStr = '%s - %s' % (BigWorld.wg_getShortTimeFormat(start), BigWorld.wg_getShortTimeFormat(finish))
            SystemMessages.g_instance.pushI18nMessage(SYSTEM_MESSAGES.FORTIFICATION_DEFENCEHOURSET, defenceHour=defenceHourStr, type=SystemMessages.SM_TYPE.Warning)
