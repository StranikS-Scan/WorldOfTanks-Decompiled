# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/scaleform/daapi/view/lobby/header/helpers/controls_helpers.py
from __future__ import absolute_import
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform.daapi.view.lobby.header.LobbyHeader import TOOLTIP_TYPES
from gui.Scaleform.daapi.view.lobby.header.helpers.controls_helpers import DefaultLobbyHeaderHelper
from gui.shared.utils.functions import makeTooltip
from last_stand.gui.scaleform.daapi.view.lobby.header.helpers.fight_btn_tooltips import getLSFightButtonTooltipData

class LSLobbyHeaderHelper(DefaultLobbyHeaderHelper):
    __slots__ = ()

    @classmethod
    def _getDisabledFightTooltipData(cls, prbValidation, isInSquad):
        return (getLSFightButtonTooltipData(prbValidation, isInSquad), False)

    @classmethod
    def _getOutSquadTooltipData(cls, _):
        header = backport.text(R.strings.last_stand_platoon.headerButton.tooltips.squad.header())
        body = backport.text(R.strings.last_stand_platoon.headerButton.tooltips.squad.body())
        return (makeTooltip(header, body), TOOLTIP_TYPES.COMPLEX)
