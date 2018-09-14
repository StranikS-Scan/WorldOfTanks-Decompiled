# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/FortTransportConfirmationWindow.py
import BigWorld
from ClientFortifiedRegion import BUILDING_UPDATE_REASON
from adisp import process
from debug_utils import LOG_DEBUG
from gui import SystemMessages
from gui.Scaleform.daapi.view.lobby.fortifications import FortifiedWindowScopes
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortSoundController import g_fortSoundController
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortViewHelper import FortViewHelper
from gui.Scaleform.daapi.view.meta.FortTransportConfirmationWindowMeta import FortTransportConfirmationWindowMeta
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils import fort_formatters
from gui.shared.formatters import icons, text_styles, time_formatters
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.shared import events
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.fortifications.context import TransportationCtx
from helpers import i18n

class FortTransportConfirmationWindow(FortTransportConfirmationWindowMeta, FortViewHelper):

    def __init__(self, ctx = None):
        super(FortTransportConfirmationWindow, self).__init__()
        self.__fromId = ctx.get('fromId')
        self.__toId = ctx.get('toId')
        self.__isInTutorial = self._isTutorial()
        self.__disposeRequestReceived = False

    def _populate(self):
        super(FortTransportConfirmationWindow, self)._populate()
        self.startFortListening()
        self._update()
        g_fortSoundController.playNextStepTransport()

    def _dispose(self):
        self.stopFortListening()
        super(FortTransportConfirmationWindow, self)._dispose()

    def _update(self):
        prefix = i18n.makeString(FORTIFICATIONS.FORTTRANSPORTCONFIRMATIONWINDOW_MAXTRANSPORTINGSIZELABEL)
        stdText = text_styles.standard(prefix)
        defResText = fort_formatters.getDefRes(self.getTransportingSize(), True)
        self.as_setMaxTransportingSizeS(stdText + defResText)
        clockIcon = icons.clock()
        time = time_formatters.getTimeDurationStr(self.fortCtrl.getFort().getTransportationLevel().cooldownTime)
        ctx = {'estimatedTime': time}
        estimatedTextString = i18n.makeString(FORTIFICATIONS.FORTTRANSPORTCONFIRMATIONWINDOW_TRANSPORTINGFOOTERTEXT, **ctx)
        estimatedText = text_styles.standard(estimatedTextString)
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
            self.__changeStateAndDestroy()

    def onWindowClose(self):
        self.__changeStateAndDestroy()

    def onCancel(self):
        self.__changeStateAndDestroy()

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
        else:
            SystemMessages.pushI18nMessage(SYSTEM_MESSAGES.FORTIFICATION_ERRORS_EVENT_COOLDOWN, type=SystemMessages.SM_TYPE.Error)
        self.__changeStateAndDestroy()

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

    def __forcedCloseWindow(self, _):
        self.__disposeRequestReceived = True

    def __changeStateAndDestroy(self):
        ctrl = self.fortCtrl
        if ctrl is not None and ctrl.getFort() is not None:
            self.fireEvent(events.FortEvent(events.FortEvent.TRANSPORTATION_STEP, {'step': events.FortEvent.TRANSPORTATION_STEPS.CONFIRMED,
             'isInTutorial': self.__isInTutorial}), scope=EVENT_BUS_SCOPE.FORT)
        self.destroy()
        return
