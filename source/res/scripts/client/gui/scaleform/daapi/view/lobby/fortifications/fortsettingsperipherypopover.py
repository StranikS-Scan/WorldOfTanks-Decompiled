# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/FortSettingsPeripheryPopover.py
from ConnectionManager import connectionManager
from predefined_hosts import g_preDefinedHosts
from adisp import process
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortViewHelper import FortViewHelper
from gui.Scaleform.daapi.view.meta.FortSettingsPeripheryPopoverMeta import FortSettingsPeripheryPopoverMeta
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.shared.fortifications.context import PeripheryCtx
from helpers import i18n

class FortSettingsPeripheryPopover(FortSettingsPeripheryPopoverMeta, FortViewHelper):

    def __init__(self, _ = None):
        super(FortSettingsPeripheryPopover, self).__init__()

    def setTexts(self):
        data = {'descriptionText': i18n.makeString(FORTIFICATIONS.SETTINGSPERIPHERYPOPOVER_DESCRIPTION),
         'serverText': i18n.makeString(FORTIFICATIONS.SETTINGSPERIPHERYPOPOVER_SERVER),
         'applyBtnLabel': i18n.makeString(FORTIFICATIONS.SETTINGSPERIPHERYPOPOVER_APPLYBUTTONLABEL),
         'cancelBtnLabel': i18n.makeString(FORTIFICATIONS.SETTINGSPERIPHERYPOPOVER_CANCELBUTTONLABEL)}
        self.as_setTextsS(data)

    def setData(self):
        servers = self.__getServersList()
        currentPeripheryID = self.__getCurrentServer()
        isServerValid = False
        for i in xrange(len(servers)):
            if servers[i]['id'] == currentPeripheryID:
                isServerValid = True
                break

        if not isServerValid:
            currentPeripheryID = -1
        data = {'servers': servers,
         'currentServer': currentPeripheryID}
        self.as_setDataS(data)

    def onApply(self, peripheryID):
        self.__setup(peripheryID)

    def _populate(self):
        super(FortSettingsPeripheryPopover, self)._populate()
        self.setData()
        self.setTexts()

    def _dispose(self):
        super(FortSettingsPeripheryPopover, self)._dispose()

    def __getServersList(self):
        result = []
        optionsList = g_preDefinedHosts.getSimpleHostsList(g_preDefinedHosts.hostsWithRoaming())
        for _, name, _, peripheryID in optionsList:
            result.append({'id': peripheryID,
             'label': name})

        if connectionManager.peripheryID == 0:
            result.append({'id': 0,
             'label': connectionManager.serverUserName})
        return result

    def __getCurrentServer(self):
        return self.fortCtrl.getFort().peripheryID

    @process
    def __setup(self, peripheryID):
        result = yield self.fortProvider.sendRequest(PeripheryCtx(peripheryID, waitingID='fort/settings'))
