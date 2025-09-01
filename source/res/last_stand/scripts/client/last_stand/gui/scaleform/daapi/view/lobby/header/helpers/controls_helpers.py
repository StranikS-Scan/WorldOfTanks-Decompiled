# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/scaleform/daapi/view/lobby/header/helpers/controls_helpers.py
from __future__ import absolute_import
import typing
from gui.impl.gen import R
from gui.Scaleform.daapi.view.lobby.header.helpers.controls_helpers import DefaultLobbyHeaderHelper
from last_stand.gui.scaleform.daapi.view.lobby.header.helpers.fight_btn_tooltips import getLSFightButtonTooltipData
from last_stand.gui.impl.lobby.page.ls_lobby_header import LSLobbyHeader
if typing.TYPE_CHECKING:
    from gui.impl.pub.view_component import ViewComponent

class LSLobbyHeaderHelper(DefaultLobbyHeaderHelper):
    __slots__ = ()

    @classmethod
    def getHeaderType(cls):
        return LSLobbyHeader

    @classmethod
    def _getDisabledFightTooltipData(cls, prbValidation, isInSquad):
        return (getLSFightButtonTooltipData(prbValidation, isInSquad), False)

    @classmethod
    def _getOutSquadTooltipData(cls, _):
        squad = R.strings.last_stand_platoon.headerButton.tooltips.squad
        return (squad.header(), squad.body(), {})
