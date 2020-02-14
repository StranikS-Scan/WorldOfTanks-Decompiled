# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/BCBattleSelector.py
import logging
from gui.Scaleform.daapi.view.lobby.header.BattleTypeSelectPopover import BattleTypeSelectPopover
_logger = logging.getLogger(__name__)

class BCBattleSelector(BattleTypeSelectPopover):

    def as_updateS(self, items, extraItems, isShowDemonstrator, demonstratorEnabled):
        _logger.debug('BCBattleSelector, %s', items)
        for battleTypeItem in items:
            if battleTypeItem['data'] != 'random':
                battleTypeItem['disabled'] = True

        super(BCBattleSelector, self).as_updateS(items, extraItems, isShowDemonstrator, demonstratorEnabled)
