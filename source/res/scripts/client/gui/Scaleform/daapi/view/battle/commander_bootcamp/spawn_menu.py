# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/commander_bootcamp/spawn_menu.py
from gui.Scaleform.daapi.view.meta.BCCommanderSpawnMenuMeta import BCCommanderSpawnMenuMeta
from gui.battle_control.controllers.commander.spawn_ctrl.interfaces import IRTSSpawnListener
from gui.impl import backport
from gui.impl.gen import R
from gui.shared import EVENT_BUS_SCOPE, events
from gui.shared.utils import toUpper
from helpers.CallbackDelayer import CallbackDelayer

class BCSpawnMenu(BCCommanderSpawnMenuMeta, CallbackDelayer, IRTSSpawnListener):
    _ALERT_HINT_STATE = 0
    _GREEN_HINT_STATE = 1
    _INITIAL_HINT_DELAY = 1
    _AUTO_BTN_HINT_DELAY = 3

    def __init__(self):
        super(BCSpawnMenu, self).__init__()
        self.__hasUserPlacedEntities = False

    def _populate(self):
        super(BCSpawnMenu, self)._populate()
        self.as_setEnemyNameVisibilityS(False)
        self.as_showFooterHintTextS(True, backport.text(R.strings.rts_battles.tutorial.spawnMenu.mainHintText()))
        self.as_showMapHintS(False, self._ALERT_HINT_STATE, '')
        self.as_showButtonArrowHintS(False, '')
        self.as_setIsBootcampS(True)
        self.addListener(events.GameEvent.BATTLE_LOADING, self.__handleBattleLoading, EVENT_BUS_SCOPE.BATTLE)

    def _dispose(self):
        self.removeListener(events.GameEvent.BATTLE_LOADING, self.__handleBattleLoading, EVENT_BUS_SCOPE.BATTLE)
        super(BCSpawnMenu, self)._dispose()

    def _updateResetButtonState(self):
        pass

    def updatePointsList(self):
        super(BCSpawnMenu, self).updatePointsList()
        if self._getSpawnCtrl().placedEntities:
            self._onEntitiesPlaced()
            if not self.__hasUserPlacedEntities:
                self.as_showMapHintS(False, self._GREEN_HINT_STATE, '')

    def _isStrategistEnemyVehicle(self, vInfo):
        return False

    def onAutoSetBtnClick(self):
        super(BCSpawnMenu, self).onAutoSetBtnClick()
        self.__hasUserPlacedEntities = True
        self._onEntitiesPlaced()
        self.as_showMapHintS(True, self._GREEN_HINT_STATE, backport.text(R.strings.rts_battles.tutorial.spawnMenu.map.successfulPlacement()))

    def _onEntitiesPlaced(self):
        self.stopCallback(self.__activateButtonCB)
        self.as_showButtonArrowHintS(False, '')
        self.as_showFooterHintTextS(False, '')

    def __handleBattleLoading(self, event):
        if event.ctx['isShown']:
            return
        self.delayCallback(self._INITIAL_HINT_DELAY, self.__updateMapHintCB, self._ALERT_HINT_STATE, R.strings.rts_battles.tutorial.spawnMenu.map.alert())

    def __updateMapHintCB(self, hintState, hintText):
        self.as_showMapHintS(True, hintState, backport.text(hintText))
        self.delayCallback(self._AUTO_BTN_HINT_DELAY, self.__activateButtonCB)

    def __activateButtonCB(self):
        self.as_showButtonArrowHintS(True, toUpper(backport.text(R.strings.rts_battles.tutorial.spawnMenu.autoButtonHintText())))
