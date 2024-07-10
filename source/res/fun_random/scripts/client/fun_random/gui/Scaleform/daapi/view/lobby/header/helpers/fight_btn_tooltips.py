# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/Scaleform/daapi/view/lobby/header/helpers/fight_btn_tooltips.py
from __future__ import absolute_import
from gui.impl import backport
from gui.impl.gen import R
from gui.prb_control.settings import PRE_QUEUE_RESTRICTION, UNIT_RESTRICTION
from gui.Scaleform.daapi.view.lobby.header.helpers.fight_btn_tooltips import getRandomTooltipData
from gui.shared.utils.functions import makeTooltip
from helpers import dependency
from skeletons.gui.game_control import IFunRandomController

@dependency.replace_none_kwargs(funRandomCtrl=IFunRandomController)
def getFunRandomFightBtnTooltipData(result, isInSquad, funRandomCtrl=None):
    state = result.restriction
    resShortCut = R.strings.fun_random.headerButtons.fightBtn.tooltip
    if state in (PRE_QUEUE_RESTRICTION.MODE_NOT_SET, UNIT_RESTRICTION.MODE_NOT_SET):
        header = backport.text(resShortCut.funRandomNotSet.header())
        body = backport.text(resShortCut.funRandomNotSet.body())
    elif state in (PRE_QUEUE_RESTRICTION.MODE_NOT_AVAILABLE, UNIT_RESTRICTION.MODE_NOT_AVAILABLE):
        desiredSubMode = funRandomCtrl.subModesHolder.getDesiredSubMode()
        if desiredSubMode is not None and desiredSubMode.isLastActiveCycleEnded():
            header = backport.text(resShortCut.funRandomSubModeEnded.header())
            body = backport.text(resShortCut.funRandomSubModeEnded.body(), subModeName=backport.text(desiredSubMode.getLocalsResRoot().userName()))
        else:
            header = backport.text(resShortCut.funRandomDisabled.header())
            body = backport.text(resShortCut.funRandomDisabled.body())
    elif state in PRE_QUEUE_RESTRICTION.VEHICLE_LIMITS + UNIT_RESTRICTION.VEHICLE_LIMITS:
        header = backport.text(resShortCut.funRandomVehLimits.header())
        body = backport.text(resShortCut.funRandomVehLimits.body())
    else:
        return getRandomTooltipData(result, isInSquad)
    return makeTooltip(header, body)
