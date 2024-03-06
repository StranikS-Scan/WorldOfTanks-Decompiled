# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/battle_hints/component.py
import typing
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.battle_control.controllers.battle_hints.common import getLogger
from gui.battle_control.controllers.battle_hints.queues import BattleHintQueueParams
if typing.TYPE_CHECKING:
    from hints.battle.schemas.base import CHMType
    from gui.battle_control.controllers.battle_hints.controller import BattleHintsController
_logger = getLogger('Component')

class BattleHintComponent(object):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, battleHintsQueueParams=None, *args, **kwargs):
        self.__battleHintsQueueParams = battleHintsQueueParams
        if self.__battleHintsQueueParams is None:
            self.__battleHintsQueueParams = BattleHintQueueParams(name='{}_{}'.format(self.__class__.__name__, id(self)))
        super(BattleHintComponent, self).__init__(*args, **kwargs)
        _logger.debug('Initialized with queue params %s.', self.__battleHintsQueueParams)
        return

    def getBattleHintsQueueParams(self):
        return self.__battleHintsQueueParams

    def showHint(self, model, params=None):
        self._showHint(model, params)

    def hideHint(self):
        self._hideHint()

    def cancelFadeOut(self):
        self._cancelFadeOut()

    def onFadeOutFinished(self):
        battleHints = self.__sessionProvider.dynamic.battleHints
        if not battleHints:
            _logger.warning('No battle hint controller on fade out finished event.')
            return
        battleHints.onFadeOutFinished(self)

    def _showHint(self, model, params):
        raise NotImplementedError

    def _hideHint(self):
        raise NotImplementedError

    def _cancelFadeOut(self):
        pass
