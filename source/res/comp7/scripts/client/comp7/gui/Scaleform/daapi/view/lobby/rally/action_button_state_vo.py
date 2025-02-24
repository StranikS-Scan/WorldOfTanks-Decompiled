# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/Scaleform/daapi/view/lobby/rally/action_button_state_vo.py
from gui.impl import backport
from gui.impl.gen import R
from gui.prb_control.settings import UNIT_RESTRICTION
from helpers import dependency
from skeletons.gui.game_control import IComp7Controller

@dependency.replace_none_kwargs(comp7Ctrl=IComp7Controller)
def unitRestrictionsGetter(comp7Ctrl=None):
    return {UNIT_RESTRICTION.RANK_RESTRICTION: (backport.text(R.strings.comp7_ext.unit.message.rankRangeRestriction()), {}),
     UNIT_RESTRICTION.MODE_OFFLINE: (backport.text(R.strings.comp7_ext.unit.message.modeOffline()), {})}
