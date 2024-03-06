# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prebattle_hints/controller.py
import importlib
import random
from logging import getLogger
import typing
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showPrebattleHintsWindow
from helpers import dependency
from hints_common.prebattle.manager import getInstance
from hints_common.prebattle.schemas import BaseHintModel, configSchema
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.prebattle_hints.controller import IPrebattleHintsController, IPrebattleHintsControlStrategy
from soft_exception import SoftException
_logger = getLogger(__name__)

class PrebattleHintsController(IPrebattleHintsController):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        self.__strategies = {}
        self.__defaultStrategy = DefaultControlStrategy()
        self.__hasHintToShow = False
        self.__sessionProvider.onBattleSessionStart += self.__onBattleSessionStart
        self.__sessionProvider.onBattleSessionStop += self.__onBattleSessionStop
        g_eventBus.addListener(events.GameEvent.BATTLE_LOADING, self.__handleBattleLoading, EVENT_BUS_SCOPE.BATTLE)

    def fini(self):
        self.__strategies.clear()
        self.__defaultStrategy = None
        self.__hasHintToShow = False
        self.__sessionProvider.onBattleSessionStart -= self.__onBattleSessionStart
        self.__sessionProvider.onBattleSessionStop -= self.__onBattleSessionStop
        g_eventBus.removeListener(events.GameEvent.BATTLE_LOADING, self.__handleBattleLoading, EVENT_BUS_SCOPE.BATTLE)
        return

    def isEnabled(self):
        config = configSchema.getModel()
        return bool(config and config.enabled)

    def isEnabledForCurrentBattleSession(self):
        return self.__hasHintToShow and not self.__sessionProvider.shared.prebattleSetups.isSelectionStarted()

    def addControlStrategy(self, arenaBonusType, strategy):
        if arenaBonusType in self.__strategies:
            raise SoftException('Strategy for arenaBonusType = {} already registered'.format(arenaBonusType))
        self.__strategies[arenaBonusType] = strategy

    def removeControlStrategy(self, arenaBonusTypes):
        self.__strategies.pop(arenaBonusTypes, None)
        return

    def onShowHintsWindowSuccess(self, hint):
        self.__getControlStrategy(self.__sessionProvider.arenaVisitor.getArenaBonusType()).onShowHintsWindowSuccess(hint)

    def __getControlStrategy(self, arenaBonusType):
        return self.__strategies.get(arenaBonusType, self.__defaultStrategy)

    def __handleBattleLoading(self, event):
        if event.ctx['isShown'] and self.isEnabledForCurrentBattleSession():
            self.__showHintsWindow()

    def __showHintsWindow(self):
        arenaBonusType = self.__sessionProvider.arenaVisitor.getArenaBonusType()
        hintModel = self.__getControlStrategy(arenaBonusType).getHintToShow(arenaBonusType)
        if hintModel is None:
            _logger.error('Cannot find next hint for arenaBonusType = %s', arenaBonusType)
            return
        else:
            if hintModel.viewClass:
                split = hintModel.splitViewClass()
                if len(split) != 2:
                    _logger.error('Wrong hint view path format: %s', hintModel.viewClass)
                    return
                moduleName, className = split
                try:
                    module = importlib.import_module(moduleName)
                except (ImportError, ValueError):
                    _logger.error('Cannot import hint view module: %s', moduleName)
                    return

                if not hasattr(module, className):
                    _logger.error('Hint view class(%s) not found', className)
                    return
                showPrebattleHintsWindow(hintModel, getattr(module, className))
            else:
                showPrebattleHintsWindow(hintModel)
            return

    def __onBattleSessionStart(self):
        if self.isEnabled():
            arenaBonusType = self.__sessionProvider.arenaVisitor.getArenaBonusType()
            self.__hasHintToShow = self.__getControlStrategy(arenaBonusType).hasHintToShow(arenaBonusType)

    def __onBattleSessionStop(self):
        self.__hasHintToShow = False


class DefaultControlStrategy(IPrebattleHintsControlStrategy):

    def hasHintToShow(self, arenaBonusType):
        return any((h for h in getInstance().iterHints() if h.isEnabledFor(arenaBonusType)))

    def getHintToShow(self, arenaBonusType):
        hints = [ h for h in getInstance().iterHints() if h.isEnabledFor(arenaBonusType) ]
        return None if not hints else random.choice(hints)

    def onShowHintsWindowSuccess(self, hint):
        pass
