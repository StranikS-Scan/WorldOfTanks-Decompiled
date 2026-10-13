# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/scaleform/daapi/view/lobby/header/helpers/controls_helpers.py
from __future__ import absolute_import
from gui.impl.gen import R
from gui.Scaleform.daapi.view.lobby.header.helpers.controls_helpers import DefaultLobbyHeaderHelper
from halloween.gui.impl.lobby.page.hw_lobby_header import HWLobbyHeader
from halloween.gui.scaleform.daapi.view.lobby.header.helpers.fight_btn_tooltips import getHalloweenFightButtonTooltipData

class HalloweenLobbyHeaderHelper(DefaultLobbyHeaderHelper):
    __slots__ = ()

    @classmethod
    def getHeaderType(cls):
        return HWLobbyHeader

    @classmethod
    def _getDisabledFightTooltipData(cls, prbValidation, isInSquad):
        return (getHalloweenFightButtonTooltipData(prbValidation, isInSquad), False)

    @classmethod
    def _getOutSquadTooltipData(cls, _):
        squad = R.strings.halloween_platoon.headerButton.tooltips.squad
        return (squad.header(), squad.body(), {})
