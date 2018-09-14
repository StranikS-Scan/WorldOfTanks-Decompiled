# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/FortPeriodDefenceWindow.py
import time
from FortifiedRegionBase import NOT_ACTIVATED
import constants
from adisp import process
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortSoundController import g_fortSoundController
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView
from gui.Scaleform.daapi.view.meta.FortPeriodDefenceWindowMeta import FortPeriodDefenceWindowMeta
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortViewHelper import FortViewHelper
from gui.Scaleform.framework.managers.TextManager import TextType
from gui.shared.fortifications.context import SettingsCtx
from gui.shared.fortifications.fort_helpers import adjustDefenceHourToUTC, adjustOffDayToUTC, adjustDefenceHourToLocal
from helpers import i18n, time_utils
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.Scaleform.framework import AppRef
from predefined_hosts import g_preDefinedHosts
from ConnectionManager import connectionManager

class FortPeriodDefenceWindow(View, AbstractWindowView, FortPeriodDefenceWindowMeta, FortViewHelper, AppRef):

    def __init__(self, ctx = None):
        super(FortPeriodDefenceWindow, self).__init__()
        self.__textsCreated = False
        self.__peripheriesList = None
        self.__defenceHour = 0
        return

    def onCancel(self):
        self.destroy()

    def onApply(self, data):
        self.__setup(data.hour, data.holidaySelectedID, data.peripherySelectedID)

    def onWindowClose(self):
        self.onCancel()

    def onShutdownDowngrade(self):
        self.__updateData()

    def onDefenceHourChanged(self, hour):
        if not self.isDisposed():
            self.__updateData()

    def onOffDayChanged(self, offDay):
        self.__updateData()

    def onPeripheryChanged(self, peripheryID):
        self.__updateData()

    def onVacationChanged(self, vacationStart, vacationEnd):
        self.__updateData()

    def _populate(self):
        super(FortPeriodDefenceWindow, self)._populate()
        self.startFortListening()
        self.__updateData()

    def _dispose(self):
        self.stopFortListening()
        super(FortPeriodDefenceWindow, self)._dispose()

    def __updateData(self):
        if self.fortCtrl.getFort().isDefenceHourEnabled():
            return self.destroy()
        self.as_setTextDataS(self.__createTexts())
        self.as_setDataS(self.__createData())

    def __createTexts(self):
        self.__textsCreated = True
        gt = self.__getHTMLText
        return {'windowLbl': FORTIFICATIONS.PERIODDEFENCEWINDOW_HEADERLBL,
         'headerLbl': gt(TextType.HIGH_TITLE, FORTIFICATIONS.PERIODDEFENCEWINDOW_READY),
         'peripheryLbl': gt(TextType.NEUTRAL_TEXT, FORTIFICATIONS.PERIODDEFENCEWINDOW_PERIPHERY),
         'peripheryDescr': gt(TextType.STANDARD_TEXT, FORTIFICATIONS.PERIODDEFENCEWINDOW_PERIPHERY_DESCRIPTION),
         'hourDefenceLbl': gt(TextType.NEUTRAL_TEXT, FORTIFICATIONS.PERIODDEFENCEWINDOW_HOURDEFENCE),
         'hourDefenceDescr': gt(TextType.STANDARD_TEXT, FORTIFICATIONS.PERIODDEFENCEWINDOW_HOURDEFENCE_DESCRIPTION),
         'holidayLbl': gt(TextType.NEUTRAL_TEXT, FORTIFICATIONS.PERIODDEFENCEWINDOW_HOLIDAY),
         'holidayDescr': gt(TextType.STANDARD_TEXT, FORTIFICATIONS.PERIODDEFENCEWINDOW_HOLIDAY_DESCRIPTION),
         'acceptBtn': FORTIFICATIONS.PERIODDEFENCEWINDOW_BTN_ACTIVATE,
         'cancelBtn': FORTIFICATIONS.PERIODDEFENCEWINDOW_BTN_NOTNOW}

    def __createData(self):
        fort = self.fortCtrl.getFort()
        skipValues = []
        if constants.IS_KOREA:
            skipValues = [0, 7]
        peripheryList = self.__getPeripheryList()
        currentPeripheryID = fort.peripheryID
        isServerValid = False
        for i in xrange(len(peripheryList)):
            if peripheryList[i]['id'] == currentPeripheryID:
                isServerValid = True
                break

        if not isServerValid:
            currentPeripheryID = -1
        _, defenceMin = adjustDefenceHourToLocal(0)
        return {'peripheryData': peripheryList,
         'peripherySelectedID': currentPeripheryID,
         'holidayData': self._getDayoffsList(),
         'holidaySelectedID': fort.getLocalOffDay(),
         'hour': -1,
         'minutes': defenceMin,
         'isWrongLocalTime': self._isWrongLocalTime(),
         'skipValues': skipValues,
         'isTwelveHoursFormat': self.app.utilsManager.isTwelveHoursFormat()}

    def __getHTMLText(self, style, localText):
        text = i18n.makeString(localText)
        return self.app.utilsManager.textManager.getText(style, text)

    def __getPeripheryList(self):
        result = []
        optionsList = g_preDefinedHosts.getSimpleHostsList(g_preDefinedHosts.hostsWithRoaming())
        for _, name, _, peripheryID in optionsList:
            result.append({'id': peripheryID,
             'label': name})

        if connectionManager.peripheryID == 0:
            result.append({'id': 0,
             'label': connectionManager.serverUserName})
        return result

    @process
    def __setup(self, defHour, offDay, peripheryID):
        defHourUTC = adjustDefenceHourToUTC(defHour)
        offDayUTC = offDay
        if offDay != NOT_ACTIVATED:
            offDayUTC = adjustOffDayToUTC(offDay, defHour)
        result = yield self.fortProvider.sendRequest(SettingsCtx(defHourUTC, offDayUTC, peripheryID, waitingID='fort/settings'))
        if result:
            g_fortSoundController.playDefencePeriodActivated()
        self.destroy()
