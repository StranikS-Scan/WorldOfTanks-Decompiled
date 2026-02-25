# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/crew_controller.py
from gui.shared.gui_items.Tankman import NO_SLOT, NO_TANKMAN
from gui.prb_control.entities.listener import IGlobalListener
from helpers import dependency
import Event
from skeletons.gui.game_control import ICrewController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.impl import IGuiLoader

class CrewController(ICrewController, IGlobalListener):
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __uiLoader = dependency.descriptor(IGuiLoader)

    def __init__(self):
        super(CrewController, self).__init__()
        self.__widgetSlotIdx = NO_SLOT
        self.__widgetTankmanID = NO_TANKMAN
        self.__isActiveJunkTankmen = False
        self.onJunkStatusChanged = Event.Event()

    def onAccountBecomePlayer(self):
        self.__isActiveJunkTankmen = self.__lobbyContext.getServerSettings().isJunkCrewConversionEnabled()
        self.__subscribe()

    def setWidgetData(self, viewKey):
        view = self.__uiLoader.windowsManager.getViewByLayoutID(viewKey)
        if view and view.crewWidget:
            currentSlotIdx, _, currentTankman = view.crewWidget.getWidgetData()
            self.__widgetSlotIdx = currentSlotIdx
            self.__widgetTankmanID = currentTankman.invID if currentTankman else NO_TANKMAN

    def getWidgetData(self):
        return (self.__widgetSlotIdx, self.__widgetTankmanID)

    def onDisconnected(self):
        self.__dispose()

    @property
    def isActiveJunkTankmen(self):
        return self.__isActiveJunkTankmen

    def __onServerSettingsChange(self, diff):
        isJunkCrewConversionEnabled = diff.get('isJunkCrewConversionEnabled')
        if isJunkCrewConversionEnabled is not None:
            self.__isActiveJunkTankmen = isJunkCrewConversionEnabled
            self.onJunkStatusChanged()
        return

    def __subscribe(self):
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChange

    def __unSubscribe(self):
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChange

    def __dispose(self):
        self.__unSubscribe()
