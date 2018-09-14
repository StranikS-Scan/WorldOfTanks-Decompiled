# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/FortTransportConfirmationWindow.py
import BigWorld
from ClientFortifiedRegion import BUILDING_UPDATE_REASON
from adisp import process
from gui import SystemMessages
from gui.Scaleform.daapi.view.lobby.fortifications import FortifiedWindowScopes
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortSoundController import g_fortSoundController
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortViewHelper import FortViewHelper
from gui.Scaleform.daapi.view.meta.FortTransportConfirmationWindowMeta import FortTransportConfirmationWindowMeta
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils import fort_formatters
from gui.Scaleform.framework.managers.TextManager import TextType, TextIcons
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.Scaleform.framework import AppRef
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.shared import events
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.fortifications.context import TransportationCtx
from helpers import i18n

class FortTransportConfirmationWindow(View, AbstractWindowView, FortTransportConfirmationWindowMeta, FortViewHelper, AppRef):

    def __init__(self, ctx = None):
        super(FortTransportConfirmationWindow, self).__init__()
        self.addListener(events.FortEvent.CLOSE_TRANSPORT_CONFIRM_WINDOW, self.__forcedCloseWindow, scope=FortifiedWindowScopes.FORT_MAIN_SCOPE)
        self.__fromId = ctx.get('fromId')
        self.__toId = ctx.get('toId')
        self.__isInTutorial = self._isTutorial()

    def _populate(self):
        super(FortTransportConfirmationWindow, self)._populate()
        self.startFortListening()
        self._update()
        g_fortSoundController.playNextStepTransport()

    def __forcedCloseWindow(self, _):
        BigWorld.callback(0.2, self.__destoryCallback)

    def __destoryCallback(self):
        self.destroy()

    def _dispose(self):
        self.removeListener(events.FortEvent.CLOSE_TRANSPORT_CONFIRM_WINDOW, self.__forcedCloseWindow, scope=FortifiedWindowScopes.FORT_MAIN_SCOPE)
        self.stopFortListening()
        ctrl = self.fortCtrl
        if ctrl is not None and ctrl.getFort() is not None:
            self.fireEvent(events.FortEvent(events.FortEvent.TRANSPORTATION_STEP, {'step': events.FortEvent.TRANSPORTATION_STEPS.CONFIRMED,
             'isInTutorial': self.__isInTutorial}), scope=EVENT_BUS_SCOPE.FORT)
        super(FortTransportConfirmationWindow, self)._dispose()
        return

    def _update(self):
        prefix = i18n.makeString(FORTIFICATIONS.FORTTRANSPORTCONFIRMATIONWINDOW_MAXTRANSPORTINGSIZELABEL)
        stdText = self.app.utilsManager.textManager.getText(TextType.STANDARD_TEXT, prefix)
        defResText = fort_formatters.getDefRes(self.getTransportingSize(), True)
        self.as_setMaxTransportingSizeS(stdText + defResText)
        clockIcon = self.app.utilsManager.textManager.getIcon(TextIcons.CLOCK_ICON)
        time = self.app.utilsManager.textManager.getTimeDurationStr(self.fortCtrl.getFort().getTransportationLevel().cooldownTime)
        ctx = {'estimatedTime': time}
        estimatedTextString = i18n.makeString(FORTIFICATIONS.FORTTRANSPORTCONFIRMATIONWINDOW_TRANSPORTINGFOOTERTEXT, **ctx)
        estimatedText = self.app.utilsManager.textManager.getText(TextType.STANDARD_TEXT, estimatedTextString)
        self.as_setFooterTextS(clockIcon + estimatedText)
        data = self.__buildData()
        self.as_setDataS(data)
        isFirstTransporting = self._isTutorial()
        self.as_enableForFirstTransportingS(isFirstTransporting)

    def __buildData(self):
        maxSize = self.getTransportingSize()
        fromBuild = self.getBuildDescr()
        toBuild = self.getBuildDescr(False)
        return {'maxTransportingSize': maxSize,
         'defResTep': self.fortCtrl.getFort().getDefResStep(),
         'sourceBaseVO': self._makeBuildingData(fromBuild, fromBuild.direction, fromBuild.position),
         'targetBaseVO': self._makeBuildingData(toBuild, toBuild.direction, toBuild.position)}

    def onUpdated(self, isFullUpdate):
        self._update()

    def onBuildingChanged(self, buildingTypeID, reason, ctx = None):
        if buildingTypeID in (self.getServerBuildId(), self.getServerBuildId(False)) and reason == BUILDING_UPDATE_REASON.DELETED:
            self.destroy()

    def onTransportingLimit(self):
        g_fortSoundController.playLimitTransport()

    def onWindowClose(self):
        self.destroy()

    def onCancel(self):
        self.destroy()

    def onTransporting(self, size):
        g_fortSoundController.playStartTransport()
        self.transportRequest(size)

    @process
    def transportRequest(self, size):
        if not self.getBuildDescr(False).isInCooldown():
            result = yield self.fortProvider.sendRequest(TransportationCtx(self.getServerBuildId(), self.getServerBuildId(False), size, waitingID='fort/transport'))
            if result:
                fromBuild = self.fortCtrl.getFort().getBuilding(self.getServerBuildId())
                toBuild = self.fortCtrl.getFort().getBuilding(self.getServerBuildId(False))
                SystemMessages.g_instance.pushI18nMessage(SYSTEM_MESSAGES.FORTIFICATION_TRANSPORT, toBuilding=toBuild.userName, fromBuilding=fromBuild.userName, res=BigWorld.wg_getIntegralFormat(size), type=SystemMessages.SM_TYPE.Warning)
            self.destroy()
        else:
            SystemMessages.pushI18nMessage(SYSTEM_MESSAGES.FORTIFICATION_ERRORS_EVENT_COOLDOWN, type=SystemMessages.SM_TYPE.Error)
            self.destroy()

    def getTransportingSize(self):
        fromBuild = self.getBuildDescr()
        toBuild = self.getBuildDescr(False)
        storages = min(fromBuild.storage, toBuild.levelRef.storage - toBuild.storage)
        if self.__isInTutorial:
            return storages
        else:
            restriction = self.fortCtrl.getFort().getTransportationLevel().maxResource
            return min(storages, restriction)

    def getBuildDescr(self, isSource = True):
        return self.fortCtrl.getFort().getBuilding(self.getServerBuildId(isSource))

    def getServerBuildId(self, isSource = True):
        return self.getBuildingIDbyUID(self.__fromId if isSource else self.__toId)
