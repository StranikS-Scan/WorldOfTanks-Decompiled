# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/FortPeriodDefenceWindow.py
from FortifiedRegionBase import NOT_ACTIVATED
from adisp import process
from gui.LobbyContext import g_lobbyContext
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortSoundController import g_fortSoundController
from gui.Scaleform.daapi.view.meta.FortPeriodDefenceWindowMeta import FortPeriodDefenceWindowMeta
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortViewHelper import FortViewHelper
from gui.shared.formatters import text_styles
from gui.shared.fortifications.context import SettingsCtx
from gui.shared.fortifications.fort_helpers import adjustDefenceHourToUTC, adjustOffDayToUTC, adjustDefenceHourToLocal, adjustDefenceHoursListToLocal
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from predefined_hosts import g_preDefinedHosts
from ConnectionManager import connectionManager

class FortPeriodDefenceWindow(FortPeriodDefenceWindowMeta, FortViewHelper):

    def __init__(self, _ = None):
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
        return {'windowLbl': FORTIFICATIONS.PERIODDEFENCEWINDOW_HEADERLBL,
         'headerLbl': text_styles.highTitle(FORTIFICATIONS.PERIODDEFENCEWINDOW_READY),
         'peripheryLbl': text_styles.neutral(FORTIFICATIONS.PERIODDEFENCEWINDOW_PERIPHERY),
         'peripheryDescr': text_styles.standard(FORTIFICATIONS.PERIODDEFENCEWINDOW_PERIPHERY_DESCRIPTION),
         'hourDefenceLbl': text_styles.neutral(FORTIFICATIONS.PERIODDEFENCEWINDOW_HOURDEFENCE),
         'hourDefenceDescr': text_styles.standard(FORTIFICATIONS.PERIODDEFENCEWINDOW_HOURDEFENCE_DESCRIPTION),
         'holidayLbl': text_styles.neutral(FORTIFICATIONS.PERIODDEFENCEWINDOW_HOLIDAY),
         'holidayDescr': text_styles.standard(FORTIFICATIONS.PERIODDEFENCEWINDOW_HOLIDAY_DESCRIPTION),
         'acceptBtn': FORTIFICATIONS.PERIODDEFENCEWINDOW_BTN_ACTIVATE,
         'cancelBtn': FORTIFICATIONS.PERIODDEFENCEWINDOW_BTN_NOTNOW}

    def __createData(self):
        fort = self.fortCtrl.getFort()
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
         'skipValues': adjustDefenceHoursListToLocal(g_lobbyContext.getServerSettings().getForbiddenFortDefenseHours()),
         'isTwelveHoursFormat': self.app.utilsManager.isTwelveHoursFormat()}

    @staticmethod
    def __getPeripheryList():
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
