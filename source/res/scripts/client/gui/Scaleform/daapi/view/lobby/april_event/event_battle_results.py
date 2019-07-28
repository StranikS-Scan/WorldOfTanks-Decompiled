# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/april_event/event_battle_results.py
import GUI
import SoundGroups
import constants
from gui.prb_control import prbDispatcherProperty
from gui.prb_control.events_dispatcher import g_eventDispatcher
from helpers import dependency
from gui.Scaleform.daapi.view.meta.EventBattleResultScreenMeta import EventBattleResultScreenMeta
from gui.shared import event_bus_handlers, events, EVENT_BUS_SCOPE, event_dispatcher
from CurrentVehicle import g_currentVehicle
from gui.sounds.ambients import BattleResultsEnv
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.battle_results import IBattleResultsService
from skeletons.gui.shared.utils import IHangarSpace
from skeletons.hb1 import ICustomizableObjectsManager
_SNDID_ACHIEVEMENT = 'result_screen_achievements'
_SNDID_BONUS = 'result_screen_bonus'
_VICTORY_SCREEN_AMBIENT = 'bc_result_screen_ambient'
_HANGAR_EVENT_RESULT = 'ev_2019_secret_event_1_hangar_event_result'

class EventBattleResult(EventBattleResultScreenMeta):
    battleResults = dependency.descriptor(IBattleResultsService)
    appLoader = dependency.descriptor(IAppLoader)
    hangarSpace = dependency.descriptor(IHangarSpace)
    customizableObjectsMgr = dependency.descriptor(ICustomizableObjectsManager)
    __sound_env__ = BattleResultsEnv
    __metaclass__ = event_bus_handlers.EventBusListener

    def __init__(self, ctx=None):
        super(EventBattleResult, self).__init__()
        if 'arenaUniqueID' not in ctx:
            raise UserWarning('Key "arenaUniqueID" is not found in context', ctx)
        if not ctx['arenaUniqueID']:
            raise UserWarning('Value of "arenaUniqueID" must be greater than 0')
        self.__arenaUniqueID = ctx['arenaUniqueID']
        self.__isResultsSet = False
        self.__music = None
        self.__blur = GUI.WGUIBackgroundBlur()
        return

    @prbDispatcherProperty
    def prbDispatcher(self):
        return None

    @property
    def isInEventMode(self):
        if self.prbDispatcher:
            state = self.prbDispatcher.getFunctionalState()
            return state.isInUnit(constants.PREBATTLE_TYPE.EVENT) or state.isInPreQueue(constants.QUEUE_TYPE.EVENT_BATTLES)
        return False

    def closeView(self):
        if self.prbDispatcher and self.prbDispatcher.getEntity().isInQueue():
            if self.isInEventMode:
                g_eventDispatcher.loadEventBattleQueue()
            else:
                g_eventDispatcher.loadBattleQueue()
        else:
            event_dispatcher.showHangar()
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
        super(EventBattleResult, self)._populate()
        self.battleResults.onResultPosted += self.__handleBattleResultsPosted
        self.hangarSpace.onSpaceCreate += self.__onHangarSpaceCreated
        self.addListener(events.LinkedSetEvent.HINTS_VIEW, self.__onLinkedSetHintsView, scope=EVENT_BUS_SCOPE.LOBBY)
        self.soundManager.playSound(_VICTORY_SCREEN_AMBIENT)
        SoundGroups.g_instance.playSound2D(_HANGAR_EVENT_RESULT)
        if self.battleResults.areResultsPosted(self.__arenaUniqueID):
            self.__setBattleResults()
        self._updateComponentVisibility(False)
        self.__blur.enable = True
        self.customizableObjectsMgr.showFade(False)

    def _dispose(self):
        self.battleResults.onResultPosted -= self.__handleBattleResultsPosted
        self.hangarSpace.onSpaceCreate -= self.__onHangarSpaceCreated
        self.removeListener(events.LinkedSetEvent.HINTS_VIEW, self.__onLinkedSetHintsView, scope=EVENT_BUS_SCOPE.LOBBY)
        self.soundManager.stopSound(_VICTORY_SCREEN_AMBIENT)
        self._updateComponentVisibility(True)
        self.__blur.enable = False
        self.customizableObjectsMgr.showFade(True)
        super(EventBattleResult, self)._dispose()

    def __setBattleResults(self):
        if self.__isResultsSet:
            return
        self.__isResultsSet = True
        vo = self.battleResults.getResultsVO(self.__arenaUniqueID)
        self.as_setVictoryDataS(vo['victoryData'])
        if self.hangarSpace.spaceInited:
            self.as_playAnimationS()

    def __handleBattleResultsPosted(self, reusableInfo, composer):
        if self.__arenaUniqueID == reusableInfo.arenaUniqueID:
            self.__setBattleResults()

    def onVictoryScreenSound(self, eventName):
        self.soundManager.playSound(eventName)

    def _updateComponentVisibility(self, visible):
        if not self.isInEventMode:
            tutorialManager = self.appLoader.getApp().tutorialManager
            componentsToHide = ('MainMenuButtonBar', 'HeaderCenterMenuBg', 'MainMenuGradient')
            for component in componentsToHide:
                tutorialManager.setComponentProps(component, {'visible': visible})

    def __onHangarSpaceCreated(self):
        self.as_playAnimationS()

    def __onLinkedSetHintsView(self, event):
        self.__blur.enable = True
