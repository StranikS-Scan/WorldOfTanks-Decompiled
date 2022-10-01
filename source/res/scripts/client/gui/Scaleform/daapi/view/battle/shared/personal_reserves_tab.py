# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/personal_reserves_tab.py
import logging
from gui.Scaleform.daapi.view.meta.PersonalReservesTabMeta import PersonalReservesTabMeta
from gui.impl.battle.battle_page.full_stats.personal_reserves_tab_view import PersonalReservesTabView
_logger = logging.getLogger(__name__)

class PersonalReservesTab(PersonalReservesTabMeta):

    def __init__(self):
        super(PersonalReservesTab, self).__init__()
        _logger.debug('[Personal Reserves Tab] init')

    def _onPopulate(self):
        _logger.debug('[Personal Reserves Tab] onPopulate')
        self._createInjectView()

    def _makeInjectView(self):
        _logger.debug('[Personal Reserves Tab] makeInjectView')
        return PersonalReservesTabView()
