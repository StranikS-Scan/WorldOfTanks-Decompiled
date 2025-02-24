# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/Scaleform/daapi/view/lobby/header/helpers/controls_helpers.py
from __future__ import absolute_import
from comp7.gui.Scaleform.daapi.view.lobby.header.helpers.fight_btn_tooltips import getComp7FightBtnTooltipData
from gui.Scaleform.daapi.view.lobby.header.LobbyHeader import TOOLTIP_TYPES
from gui.Scaleform.daapi.view.lobby.header.helpers.controls_helpers import DefaultLobbyHeaderHelper
from gui.impl import backport
from gui.impl.gen import R
from gui.prb_control.settings import PRE_QUEUE_RESTRICTION
from gui.shared.utils.functions import makeTooltip
from helpers import dependency
from skeletons.gui.game_control import IComp7Controller

class Comp7LobbyHeaderHelper(DefaultLobbyHeaderHelper):
    __slots__ = ()
    __comp7Controller = dependency.descriptor(IComp7Controller)

    @classmethod
    def _getDisabledFightTooltipData(cls, prbValidation, isInSquad):
        return (getComp7FightBtnTooltipData(prbValidation, isInSquad), False)

    @classmethod
    def _getOutSquadTooltipData(cls, prbValidation):
        resRoot = R.strings.platoon.headerButton.tooltips.comp7Squad
        if prbValidation.restriction == PRE_QUEUE_RESTRICTION.BAN_IS_SET:
            resRoot = R.strings.menu.headerButtons.fightBtn.tooltip.comp7BanIsSet
        if not cls.__comp7Controller.isQualificationSquadAllowed():
            resRoot = R.strings.platoon.headerButton.tooltips.comp7QualificationSquad
        return (makeTooltip(backport.text(resRoot.header()), backport.text(resRoot.body())), TOOLTIP_TYPES.COMPLEX)
