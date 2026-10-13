# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/scaleform/daapi/view/battle/battle_hints.py
from __future__ import absolute_import
import logging
import time
import typing
from fort_rush.gui.scaleform.daapi.view.battle.hud import FortRushHudComponent
from gui.battle_control.controllers.battle_hints.component import BattleHintComponent
from gui.battle_control.controllers.battle_hints.queues import BattleHintsQueue, BattleHint
_logger = logging.getLogger(__name__)
if typing.TYPE_CHECKING:
    from typing import Optional, Tuple, Union
    from fort_rush.gui.battle_hints.battle_hints_schema import FortRushHintModel
    from gui.battle_control.controllers.battle_hints.queues import BattleHintQueueParams

class FortRushBattleHintComponent(BattleHintComponent, FortRushHudComponent):

    def __init__(self, alias, queueParams):
        super(FortRushBattleHintComponent, self).__init__(queueParams)
        self._alias = alias
        self.uniqueHints = set()

    def getAlias(self):
        return self._alias

    def _showHint(self, model, params):
        params = params or {}
        showTime = params.get('overrideShowTime', 0)
        isUnique = model.props.unique
        if isUnique:
            hintName = model.props.name
            if hintName in self.uniqueHints:
                return
            self.uniqueHints.add(hintName)
        if not model.text:
            _logger.debug('FortRush hint: %s has no text defined ', model.props.name)
            return
        message = model.text.message
        if params:
            try:
                message = message.format(**params)
            except KeyError:
                _logger.error('FortRush hint: failed to format message "%s" with params %s', message, params)

        _logger.debug('FortRush hint: show hint with text: %s, description: %s, show_cd: %s and cd: %s', message, model.text.description, model.props.showCountdown, showTime)
        self.hud.showHint(message, model.text.description, model.props.showCountdown, showTime)

    def _hideHint(self):
        _logger.debug('FortRush hint: hide current hint')
        self.hud.hideHint()


class FortRushBattleHintsQueue(BattleHintsQueue):

    def destroy(self):
        self._enabled = False
        self._queue = []
        self._stopWaitingFadeOut()
        self._stopDelayer()
        self._logger.debug('Destroyed.')


class FortRushBattleHint(BattleHint):

    def getPriority(self, currentTime):
        lastDisplayTime = 0.0
        if self._model.history and self.model.history.modifyPriority:
            lastDisplayTime = self._getLastDisplayTime()
        return (self._model.props.priority, currentTime - lastDisplayTime)

    def show(self):
        overrideShowTime = self._params.get('overrideShowTime')
        showTime = overrideShowTime or self.showTime
        self._params['overrideShowTime'] = int(self._enqueueTime + float(showTime) - time.time())
        super(FortRushBattleHint, self).show()
