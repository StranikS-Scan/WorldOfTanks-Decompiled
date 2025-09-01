# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/Scaleform/daapi/view/battle/battle_hint.py
import logging
import typing
from gui.battle_control.controllers.battle_hints.component import BattleHintComponent
from gui.battle_control.controllers.battle_hints.queues import BattleHintQueueParams
from white_tiger.gui.Scaleform.daapi.view.meta.WhiteTigerBattleHintMeta import WhiteTigerBattleHintMeta
if typing.TYPE_CHECKING:
    from hints.battle.schemas.base import CHMType
_logger = logging.getLogger(__name__)
defaultHintQueueParams = BattleHintQueueParams(name='default')

class WhiteTigerBattleHint(BattleHintComponent, WhiteTigerBattleHintMeta):

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
