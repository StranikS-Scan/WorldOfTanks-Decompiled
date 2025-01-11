# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/client/grinch/gui/Scaleform/daapi/view/lobby/prb_windows/grinch_squad_action_button_statew_vo.py
from grinch.gui.prb_control.settings import GRINCH_UNIT_RESTRICTION
from gui.Scaleform.daapi.view.lobby.prb_windows.squad_action_button_state_vo import SquadActionButtonStateVO
from gui.impl import backport
from helpers import i18n
from gui.impl.gen import R

class GrinchSquadActionButtonStateVO(SquadActionButtonStateVO):

    def _prepareRestrictions(self):
        super(GrinchSquadActionButtonStateVO, self)._prepareRestrictions()
        message = i18n.makeString(backport.text(R.strings.platoon.grinch.restrictions.roleFull()))
        self.addRestriction(GRINCH_UNIT_RESTRICTION.ROLE_FULL, message)
