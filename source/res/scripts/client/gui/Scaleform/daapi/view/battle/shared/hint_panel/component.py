# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/hint_panel/component.py
import CommandMapping
import SoundGroups
from gui.Scaleform.daapi.view.battle.shared.hint_panel import plugins
from gui.Scaleform.daapi.view.meta.BattleHintPanelMeta import BattleHintPanelMeta
from gui.battle_control.controllers.period_ctrl import IAbstractPeriodView
from gui.shared import EVENT_BUS_SCOPE, events
from gui.shared.events import GameEvent
from gui.shared.utils.plugins import PluginsCollection
from shared_utils import first

class BattleHintPanel(BattleHintPanelMeta, IAbstractPeriodView):

    def __init__(self):
        super(BattleHintPanel, self).__init__()
        self.__hints = {}
        self.__plugins = None
        self.__isBattleLoaded = False
        self.__isHintActive = False
        return

    def setBtnHint(self, btnID, hintData):
        if hintData:
            self.__hints[btnID] = hintData
            self.__invalidateBtnHint()

    def removeBtnHint(self, btnID):
        if btnID in self.__hints:
            self.__hints.pop(btnID)
        self.__invalidateBtnHint()

    def setPeriod(self, period):
        self.__plugins.setPeriod(period)

    def getActiveHint(self):
        hintData = self.__getActiveHintData()
        if hintData:
            _, hint = hintData
            return hint
        else:
            return None

    def onPlaySound(self, soundType):
        SoundGroups.g_instance.playSound2D(soundType)

    def onHideComplete(self):
        self.fireEvent(GameEvent(GameEvent.HIDE_BTN_HINT), scope=EVENT_BUS_SCOPE.GLOBAL)

    def _populate(self):
        super(BattleHintPanel, self)._populate()
        self.addListener(events.GameEvent.BATTLE_LOADING, self.__handleBattleLoading, EVENT_BUS_SCOPE.BATTLE)
        self.__plugins = HintPluginsCollection(self)
        self.__plugins.addPlugins(plugins.createPlugins())
        self.__plugins.init()
        self.__plugins.start()

    def _dispose(self):
        if self.__plugins is not None:
            self.__plugins.stop()
            self.__plugins.fini()
            self.__plugins = None
        self.__hints = None
        self.removeListener(events.GameEvent.BATTLE_LOADING, self.__handleBattleLoading, scope=EVENT_BUS_SCOPE.BATTLE)
        super(BattleHintPanel, self)._dispose()
        return

    def __getActiveHintData(self):
        return first(sorted(self.__hints.iteritems(), key=lambda h: h[1].priority, reverse=False))

    def __invalidateBtnHint(self):
        hintData = self.__getActiveHintData()
        if hintData:
            btnID, hint = hintData
            self.as_setDataS(hint.key, hint.messageLeft, hint.messageRight, hint.offsetX, hint.offsetY)
            self.fireEvent(GameEvent(GameEvent.SHOW_BTN_HINT, ctx={'btnID': btnID}), scope=EVENT_BUS_SCOPE.GLOBAL)
        self.__isHintActive = bool(hintData)
        if self.__isBattleLoaded:
            self.as_toggleS(self.__isHintActive)

    def __handleBattleLoading(self, event):
        self.__isBattleLoaded = not event.ctx['isShown']
        if self.__isBattleLoaded and self.__isHintActive:
            self.as_toggleS(True)


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
