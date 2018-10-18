# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/halloween/event_battle_results.py
from helpers import dependency
from skeletons.gui.halloween_controller import IHalloweenController
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.meta.EventVictoryScreenViewMeta import EventVictoryScreenViewMeta
from gui.shared import event_bus_handlers, events, EVENT_BUS_SCOPE
from CurrentVehicle import g_currentVehicle
from gui.sounds.ambients import BattleResultsEnv
from skeletons.gui.battle_results import IBattleResultsService
_SNDID_ACHIEVEMENT = 'result_screen_achievements'
_SNDID_BONUS = 'result_screen_bonus'
_VICTORY_SCREEN_AMBIENT = 'bc_result_screen_ambient'

class EventBattleResult(EventVictoryScreenViewMeta):
    battleResults = dependency.descriptor(IBattleResultsService)
    halloweenController = dependency.descriptor(IHalloweenController)
    __sound_env__ = BattleResultsEnv
    __metaclass__ = event_bus_handlers.EventBusListener

    def __init__(self, ctx=None):
        super(EventBattleResult, self).__init__()
        if 'arenaUniqueID' not in ctx:
            raise UserWarning('Key "arenaUniqueID" is not found in context', ctx)
        if not ctx['arenaUniqueID']:
            raise UserWarning('Value of "arenaUniqueID" must be greater than 0')
        self.__arenaUniqueID = ctx['arenaUniqueID']
        self.__populated = False
        self.__isResultsSet = False
        self.__music = None
        self.battleResults.onResultPosted += self.__handleBattleResultsPosted
        return

    def closeView(self):
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_HANGAR), scope=EVENT_BUS_SCOPE.LOBBY)
        self.destroy()

    def onWindowClose(self):
        self.destroy()

    def click(self):
        self.destroy()

    @event_bus_handlers.eventBusHandler(events.HideWindowEvent.HIDE_BATTLE_RESULT_WINDOW, EVENT_BUS_SCOPE.LOBBY)
    def selectVehicle(self, inventoryId):
        g_currentVehicle.selectVehicle(inventoryId)
        return g_currentVehicle.invID == inventoryId

    def onResultScreenFinished(self):
        self.destroy()

    def _populate(self):
        self.soundManager.playSound(_VICTORY_SCREEN_AMBIENT)
        super(EventBattleResult, self)._populate()
        self.__populated = True
        if self.battleResults.areResultsPosted(self.__arenaUniqueID):
            self.__setBattleResults()

    def _dispose(self):
        self.battleResults.onResultPosted -= self.__handleBattleResultsPosted
        self.soundManager.stopSound(_VICTORY_SCREEN_AMBIENT)
        progress = self.halloweenController.getProgress()
        if progress:
            progress.showAward()
        super(EventBattleResult, self)._dispose()

    def __setBattleResults(self):
        if not self.__isResultsSet:
            self.__isResultsSet = True
            vo = self.battleResults.getResultsVO(self.__arenaUniqueID)
            self.as_setVictoryDataS(vo['victoryData'])
            self.as_setProgressDataS(vo['progressData'])
            self.as_setProgressValueS(*vo['progressValue'])

    def __handleBattleResultsPosted(self, reusableInfo, composer):
        if self.__arenaUniqueID == reusableInfo.arenaUniqueID and self.__populated:
            self.__setBattleResults()

    def onVictoryScreenSound(self, eventName):
        self.soundManager.playSound(eventName)
