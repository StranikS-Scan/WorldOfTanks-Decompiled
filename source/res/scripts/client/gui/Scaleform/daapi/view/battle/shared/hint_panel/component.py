# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/hint_panel/component.py
from __future__ import absolute_import
from functools import partial
from future.utils import viewitems
import BigWorld
import CommandMapping
import SoundGroups
from constants import ARENA_PERIOD
from gui.Scaleform.daapi.view.battle.shared.hint_panel import plugins
from gui.Scaleform.daapi.view.meta.BattleHintPanelMeta import BattleHintPanelMeta
from gui.battle_control.controllers.period_ctrl import IAbstractPeriodView
from gui.shared import EVENT_BUS_SCOPE
from gui.shared.events import GameEvent
from gui.shared.utils.plugins import PluginsCollection
from helpers import dependency
from shared_utils import first
from skeletons.gameplay import IGameplayLogic, GameplayStateID

class BattleHintPanel(BattleHintPanelMeta, IAbstractPeriodView):
    __gameplayLogic = dependency.descriptor(IGameplayLogic)

    def __init__(self):
        super(BattleHintPanel, self).__init__()
        self._hints = {}
        self._plugins = None
        self.__isBattleLoaded = False
        self.__invalidateCallbackID = None
        return

    def setBtnHint(self, btnID, hintData):
        if hintData:
            if btnID in self._hints:
                if hintData.priority < self._hints[btnID].priority:
                    self._hints[btnID] = hintData
            else:
                self._hints[btnID] = hintData
            self.__invalidateBtnHint()

    def removeBtnHint(self, btnID):
        hint = None
        if btnID in self._hints:
            hint = self._hints.pop(btnID)
        self.__invalidateBtnHint(True)
        return hint

    def setPeriod(self, period):
        if self._plugins is not None:
            self._plugins.setPeriod(period)
        if period == ARENA_PERIOD.PREBATTLE:
            self.__gameplayLogic.addOneshotObserver([GameplayStateID.PREBATTLE], self, enterFn=BattleHintPanel._onPrebattleEnter)
        return

    def getActiveHint(self):
        return self.__getActiveHintData()

    def onPlaySound(self, soundType):
        SoundGroups.g_instance.playSound2D(soundType)

    def onHideComplete(self):
        self.fireEvent(GameEvent(GameEvent.HIDE_BTN_HINT), scope=EVENT_BUS_SCOPE.GLOBAL)

    def _populate(self):
        super(BattleHintPanel, self)._populate()
        self._initPlugins()

    def _dispose(self):
        self._finiPlugins()
        self._hints = None
        if self.__invalidateCallbackID is not None:
            BigWorld.cancelCallback(self.__invalidateCallbackID)
        self.__invalidateCallbackID = None
        super(BattleHintPanel, self)._dispose()
        return

    def _initPlugins(self):
        self._plugins = HintPluginsCollection(self)
        self._plugins.addPlugins(self._createPlugins())
        self._plugins.init()
        self._plugins.start()

    def _finiPlugins(self):
        if self._plugins is not None:
            self._plugins.stop()
            self._plugins.fini()
            self._plugins = None
        return

    def _createPlugins(self):
        return plugins.createPlugins()

    def __getActiveHintData(self):
        return first(sorted(viewitems(self._hints), key=lambda h: h[1].priority, reverse=False))

    def __invalidateBtnHint(self, isRemoved=False):
        if self.__invalidateCallbackID is not None:
            BigWorld.cancelCallback(self.__invalidateCallbackID)
        self.__invalidateCallbackID = BigWorld.callback(0.01, partial(self.__prepareAndShowHint, isRemoved))
        return

    def __prepareAndShowHint(self, isRemoved):
        self.__invalidateCallbackID = None
        if isRemoved:
            self.as_toggleS(False)
            self.__invalidateBtnHint()
            return
        else:
            hintData = self.__getActiveHintData()
            isHintActive = bool(hintData)
            hintCanBeDisplayed = isHintActive and self.__isBattleLoaded
            if hintCanBeDisplayed:
                btnID, hint = hintData
                self.as_setDataS(self.__makeHotKey(hint), hint.messageLeft, hint.messageRight, hint.offsetX, hint.offsetY, hint.reducedPanning, hint.centeredMessage)
                self.fireEvent(GameEvent(GameEvent.SHOW_BTN_HINT, ctx={'btnID': btnID,
                 'hintCtx': hint.hintCtx}), scope=EVENT_BUS_SCOPE.GLOBAL)
            self.as_toggleS(hintCanBeDisplayed)
            return

    def _onPrebattleEnter(self, _=None, __=None):
        self.__isBattleLoaded = True
        self.__invalidateBtnHint()

    def __makeHotKey(self, hint):
        return {'vKey': hint.vKey,
         'keyName': hint.key,
         'isLong': hint.isKeyLong}


class HintPluginsCollection(PluginsCollection):

    def start(self):
        super(HintPluginsCollection, self).start()
        CommandMapping.g_instance.onMappingChanged += self.__onMappingChanged

    def stop(self):
        super(HintPluginsCollection, self).stop()
        CommandMapping.g_instance.onMappingChanged -= self.__onMappingChanged

    def setPeriod(self, period):
        self._invoke('setPeriod', period)

    def __onMappingChanged(self, *args):
        self._invoke('updateMapping')
