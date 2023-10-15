# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/Scaleform/daapi/view/battle/battle_base_hint.py
from functools import partial
from gui.Scaleform.daapi.view.battle.classic.battle_end_warning_panel import BattleEndWarningPanel
from halloween.gui.Scaleform.daapi.view.battle.battle_hint import BattleHint
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from PlayerEvents import g_playerEvents
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.battle_session import IBattleSessionProvider
_END_WARNING_WAIT_TIME = 3.5

class BattleBaseHint(BattleHint):
    _settingsCore = dependency.descriptor(ISettingsCore)
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(BattleBaseHint, self).__init__()
        self.__finished = False
        self.__endWarningShowed = False
        self.__delayer = CallbackDelayer()

    @property
    def battleHintsController(self):
        return self._sessionProvider.dynamic.battleHints

    def showHint(self, hint, data):
        if self.__endWarningShowed:
            self.__delayer.delayCallback(_END_WARNING_WAIT_TIME, partial(self.battleHintsController.showHint, hint.name, data))
            return
        super(BattleBaseHint, self).showHint(hint, data)

    def _populate(self):
        super(BattleBaseHint, self)._populate()
        g_playerEvents.onRoundFinished += self.__onRoundFinished
        BattleEndWarningPanel.onBattleEndWarningShow += self.__onBattleEndWarningShow
        BattleEndWarningPanel.onBattleEndWarningHide += self.__onBattleEndWarningHide

    def _dispose(self):
        self.__delayer.destroy()
        g_playerEvents.onRoundFinished -= self.__onRoundFinished
        BattleEndWarningPanel.onBattleEndWarningShow -= self.__onBattleEndWarningShow
        BattleEndWarningPanel.onBattleEndWarningHide -= self.__onBattleEndWarningHide
        super(BattleBaseHint, self)._dispose()

    def _makeVO(self, hint, data):
        vo = hint.makeVO(data)
        vo['bgLabel'] = self.__getBGColor(hint.customData)
        return vo

    def _showHint(self, data):
        if not self.__finished:
            super(BattleBaseHint, self)._showHint(data=data)

    def __getBGColor(self, colorData):
        colors = colorData.split()
        isColorBlind = self._settingsCore.getSetting('isColorBlind')
        return colors[1] if isColorBlind and len(colors) > 1 else colors[0]

    def __onRoundFinished(self, *args):
        self.__finished = True
        self._hideHint()

    def __onBattleEndWarningShow(self):
        self._hideHint()
        self.__endWarningShowed = True

    def __onBattleEndWarningHide(self):
        self.__endWarningShowed = False