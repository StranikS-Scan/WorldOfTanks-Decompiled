# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/client/grinch/gui/Scaleform/daapi/view/battle/battle_hints.py
import logging
import time
import typing
from grinch.gui.Scaleform.daapi.view.battle.grinch_hud import GrinchHudComponent
from gui.battle_control.controllers.battle_hints.component import BattleHintComponent
from gui.battle_control.controllers.battle_hints.queues import BattleHintsQueue, BattleHint
_logger = logging.getLogger(__name__)
if typing.TYPE_CHECKING:
    from typing import Optional, Tuple, Union
    from grinch.gui.battle_hints.battle_hints_schema import GrinchEventHintModel
    from gui.battle_control.controllers.battle_hints.queues import BattleHintQueueParams

class GrinchBattleHintComponent(BattleHintComponent, GrinchHudComponent):

    def __init__(self, alias, queueParams):
        super(GrinchBattleHintComponent, self).__init__(queueParams)
        self._alias = alias
        self.uniqueHints = set()

    def getAlias(self):
        return self._alias

    def _showHint(self, model, params):
        showTime = params.get('overrideShowTime', 0)
        isUnique = model.props.unique
        if isUnique:
            hintName = model.props.name
            if hintName in self.uniqueHints:
                return
            self.uniqueHints.add(hintName)
        if not model.text:
            _logger.debug('Grinch hint: %s has no text defined ', model.props.name)
            return
        _logger.debug('Grinch hint: show hint with text: %s, subtext: %s, show_cd: %s and cd: %s, icon: %s', model.text.message, model.text.subtitle, model.props.showCountdown, showTime, model.props.icon)
        self.hud.showHint(model.text.message, model.text.subtitle, model.props.showCountdown, showTime, model.props.icon)

    def _hideHint(self):
        _logger.debug('Grinch hint: hide current hint')
        self.hud.hideHint()


class GrinchBattleHintsQueue(BattleHintsQueue):

    def destroy(self):
        self._enabled = False
        self._queue = []
        self._stopWaitingFadeOut()
        self._stopDelayer()
        self._logger.debug('Destroyed.')


class GrinchBattleHint(BattleHint):

    def getPriority(self, currentTime):
        lastDisplayTime = 0.0
        if self._model.history and self.model.history.modifyPriority:
            lastDisplayTime = self._getLastDisplayTime()
        return (self._model.props.priority, currentTime - lastDisplayTime)

    def show(self):
        overrideShowTime = self._params.get('overrideShowTime')
        showTime = overrideShowTime or self.showTime
        self._params['overrideShowTime'] = int(self._enqueueTime + float(showTime) - time.time())
        super(GrinchBattleHint, self).show()
