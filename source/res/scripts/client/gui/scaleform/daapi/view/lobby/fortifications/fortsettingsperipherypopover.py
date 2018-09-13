# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/FortSettingsPeripheryPopover.py
from ConnectionManager import connectionManager
from predefined_hosts import g_preDefinedHosts
from adisp import process
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortViewHelper import FortViewHelper
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.daapi.view.meta.FortSettingsPeripheryPopoverMeta import FortSettingsPeripheryPopoverMeta
from gui.Scaleform.daapi.view.lobby.popover.SmartPopOverView import SmartPopOverView
from gui.Scaleform.framework import AppRef
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.shared.fortifications.context import PeripheryCtx
from helpers import i18n

class FortSettingsPeripheryPopover(View, FortSettingsPeripheryPopoverMeta, SmartPopOverView, FortViewHelper, AppRef):

    def __init__(self, ctx = None):
        super(FortSettingsPeripheryPopover, self).__init__()
        self._orderID = str(ctx.get('data'))

    def setTexts(self):
        data = {'descriptionText': i18n.makeString(FORTIFICATIONS.SETTINGSPERIPHERYPOPOVER_DESCRIPTION),
         'serverText': i18n.makeString(FORTIFICATIONS.SETTINGSPERIPHERYPOPOVER_SERVER),
         'applyBtnLabel': i18n.makeString(FORTIFICATIONS.SETTINGSPERIPHERYPOPOVER_APPLYBUTTONLABEL),
         'cancelBtnLabel': i18n.makeString(FORTIFICATIONS.SETTINGSPERIPHERYPOPOVER_CANCELBUTTONLABEL)}
        self.as_setTextsS(data)

    def setData(self):
        data = {'servers': self.__getServersList(),
         'currentServer': self.__getCurrentServer()}
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
