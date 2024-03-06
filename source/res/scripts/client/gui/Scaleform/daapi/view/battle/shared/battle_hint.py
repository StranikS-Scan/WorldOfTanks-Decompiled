# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/battle_hint.py
import logging
import typing
from gui.battle_control.controllers.battle_hints.component import BattleHintComponent
from gui.Scaleform.daapi.view.meta.BattleHintMeta import BattleHintMeta
from gui.battle_control.controllers.battle_hints.queues import BattleHintQueueParams
if typing.TYPE_CHECKING:
    from hints.battle.schemas.base import CHMType
_logger = logging.getLogger(__name__)
defaultHintQueueParams = BattleHintQueueParams(name='default')

class BattleHint(BattleHintComponent, BattleHintMeta):

    def _showHint(self, model, params):
        vo = model.createVO(params)
        if vo:
            self.as_showHintS(vo)
        else:
            _logger.debug('Value object is empty.')

    def _hideHint(self):
        self.as_hideHintS()

    def _cancelFadeOut(self):
        self.as_cancelFadeOutS()


class DefaultBattleHint(BattleHint):

    def __init__(self):
        super(DefaultBattleHint, self).__init__(battleHintsQueueParams=defaultHintQueueParams)
