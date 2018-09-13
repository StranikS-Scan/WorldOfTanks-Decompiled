# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/FortTransportConfirmationWindow.py
import BigWorld
from adisp import process
from gui import SystemMessages
from gui.Scaleform.daapi.view.lobby.fortifications import TRANSPORTING_CONFIRMED_EVENT
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortViewHelper import FortViewHelper
from gui.Scaleform.daapi.view.meta.FortTransportConfirmationWindowMeta import FortTransportConfirmationWindowMeta
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils import fort_formatters
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils import fort_text
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.Scaleform.framework import AppRef
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.shared.SoundEffectsId import SoundEffectsId
from gui.shared.event_bus import SharedEvent, EVENT_BUS_SCOPE
from gui.shared.fortifications.context import TransportationCtx
from helpers import i18n

class FortTransportConfirmationWindow(View, AbstractWindowView, FortTransportConfirmationWindowMeta, FortViewHelper, AppRef):

    def __init__(self, fromId, toId):
        super(FortTransportConfirmationWindow, self).__init__()
        self.__fromId = fromId
        self.__toId = toId

    def _populate(self):
        super(FortTransportConfirmationWindow, self)._populate()
        self.startFortListening()
        self._update()
        if self.app.soundManager is not None:
            self.app.soundManager.playEffectSound(SoundEffectsId.TRANSPORT_NEXT_STEP)
        return

    def _dispose(self):
        self.stopFortListening()
        self.fireEvent(SharedEvent(TRANSPORTING_CONFIRMED_EVENT), scope=EVENT_BUS_SCOPE.FORT)
        super(FortTransportConfirmationWindow, self)._dispose()

    def _update(self):
        prefix = i18n.makeString(FORTIFICATIONS.FORTTRANSPORTCONFIRMATIONWINDOW_MAXTRANSPORTINGSIZELABEL)
        stdText = fort_text.getText(fort_text.STANDARD_TEXT, prefix)
        defResText = fort_formatters.getDefRes(self.getTransportingSize(), True)
        self.as_setMaxTransportingSizeS(stdText + defResText)
        clockIcon = fort_text.getIcon(fort_text.CLOCK_ICON)
        time = fort_text.getTimeDurationStr(self.fortCtrl.getFort().getTransportationLevel().cooldownTime)
        ctx = {'estimatedTime': time}
        estimatedTextString = i18n.makeString(FORTIFICATIONS.FORTTRANSPORTCONFIRMATIONWINDOW_TRANSPORTINGFOOTERTEXT, **ctx)
        estimatedText = fort_text.getText(fort_text.STANDARD_TEXT, estimatedTextString)
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

    def onUpdated(self):
        self._update()

    def onBuildingRemoved(self, buildingTypeID):
        if buildingTypeID in (self.getServerBuildId(), self.getServerBuildId(False)):
            self.destroy()

    def onTransportingLimit(self):
        if self.app.soundManager is not None:
            self.app.soundManager.playEffectSound(SoundEffectsId.TRANSPORT_CONSTRAIN)
        return

    def onWindowClose(self):
        self.destroy()

    def onCancel(self):
        self.destroy()

    def onTransporting(self, size):
        if self.app.soundManager is not None:
            self.app.soundManager.playEffectSound(SoundEffectsId.TRANSPORT_APPROVE)
        self.transportRequest(size)
        return

    @process
    def transportRequest(self, size):
        result = yield self.fortProvider.sendRequest(TransportationCtx(self.getServerBuildId(), self.getServerBuildId(False), size, waitingID='fort/transport'))
        if result:
            fromBuild = self.fortCtrl.getFort().getBuilding(self.getServerBuildId())
            toBuild = self.fortCtrl.getFort().getBuilding(self.getServerBuildId(False))
            SystemMessages.g_instance.pushI18nMessage(SYSTEM_MESSAGES.FORTIFICATION_TRANSPORT, toBuilding=toBuild.userName, fromBuilding=fromBuild.userName, res=BigWorld.wg_getIntegralFormat(size), type=SystemMessages.SM_TYPE.Warning)
            self.destroy()

    def getTransportingSize(self):
        fromBuild = self.getBuildDescr()
        toBuild = self.getBuildDescr(False)
        storages = min(fromBuild.storage, toBuild.levelRef.storage - toBuild.storage)
        if self._isTutorial():
            return storages
        else:
            restriction = self.fortCtrl.getFort().getTransportationLevel().maxResource
            return min(storages, restriction)

    def getBuildDescr(self, isSource = True):
        return self.fortCtrl.getFort().getBuilding(self.getServerBuildId(isSource))

    def getServerBuildId(self, isSource = True):
        if isSource:
            return self.UI_BUILDINGS_BIND.index(self.__fromId)
        else:
            return self.UI_BUILDINGS_BIND.index(self.__toId)
