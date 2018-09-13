# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/FortPeriodDefenceWindow.py
import constants
from adisp import process
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortSoundController import g_fortSoundController
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView
from gui.Scaleform.daapi.view.meta.FortPeriodDefenceWindowMeta import FortPeriodDefenceWindowMeta
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortViewHelper import FortViewHelper
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils import fort_text
from gui.shared.fortifications.context import SettingsCtx
from helpers import i18n
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.Scaleform.framework import AppRef
from predefined_hosts import g_preDefinedHosts
from ConnectionManager import connectionManager

class FortPeriodDefenceWindow(View, AbstractWindowView, FortPeriodDefenceWindowMeta, FortViewHelper, AppRef):

    def __init__(self):
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

    def onUpdated(self):
        self.__updateData()

    def _populate(self):
        super(FortPeriodDefenceWindow, self)._populate()
        self.startFortListening()
        self.__updateData()

    def _dispose(self):
        self.stopFortListening()
        super(FortPeriodDefenceWindow, self)._dispose()

    def __updateData(self):
        self.as_setTextsS(self.__createTexts())
        self.as_setDataS(self.__createData())

    def __createTexts(self):
        self.__textsCreated = True
        gt = self.__getHTMLText
        return {'windowLbl': FORTIFICATIONS.PERIODDEFENCEWINDOW_HEADERLBL,
         'headerLbl': gt(fort_text.HIGH_TITLE, FORTIFICATIONS.PERIODDEFENCEWINDOW_READY),
         'peripheryLbl': gt(fort_text.NEUTRAL_TEXT, FORTIFICATIONS.PERIODDEFENCEWINDOW_PERIPHERY),
         'peripheryDescr': gt(fort_text.STANDARD_TEXT, FORTIFICATIONS.PERIODDEFENCEWINDOW_PERIPHERY_DESCRIPTION),
         'hourDefenceLbl': gt(fort_text.NEUTRAL_TEXT, FORTIFICATIONS.PERIODDEFENCEWINDOW_HOURDEFENCE),
         'hourDefenceDescr': gt(fort_text.STANDARD_TEXT, FORTIFICATIONS.PERIODDEFENCEWINDOW_HOURDEFENCE_DESCRIPTION),
         'holidayLbl': gt(fort_text.NEUTRAL_TEXT, FORTIFICATIONS.PERIODDEFENCEWINDOW_HOLIDAY),
         'holidayDescr': gt(fort_text.STANDARD_TEXT, FORTIFICATIONS.PERIODDEFENCEWINDOW_HOLIDAY_DESCRIPTION),
         'acceptBtn': FORTIFICATIONS.PERIODDEFENCEWINDOW_BTN_ACTIVATE,
         'cancelBtn': FORTIFICATIONS.PERIODDEFENCEWINDOW_BTN_NOTNOW}

    def __createData(self):
        fort = self.fortCtrl.getFort()
        skipValues = []
        if constants.IS_KOREA:
            skipValues = [0, 7]
        return {'peripheryData': self.__getPeripheryList(),
         'peripherySelectedID': fort.peripheryID,
         'holidayData': self._getDayoffsList(),
         'holidaySelectedID': fort.offDay,
         'hour': fort.getLocalDefenceHour(),
         'skipValues': skipValues,
         'isTwelveHoursFormat': False}

    def __getHTMLText(self, style, localText):
        text = i18n.makeString(localText)
        return fort_text.getText(style, text)

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
        result = yield self.fortProvider.sendRequest(SettingsCtx(defHour, offDay, peripheryID, waitingID='fort/settings'))
        if result:
            g_fortSoundController.playDefencePeriodActivated()
            self.destroy()
