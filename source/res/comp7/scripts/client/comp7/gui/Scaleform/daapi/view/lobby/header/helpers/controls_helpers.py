# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/Scaleform/daapi/view/lobby/header/helpers/controls_helpers.py
from __future__ import absolute_import
import typing
from comp7.gui.Scaleform.daapi.view.lobby.header.helpers.fight_btn_tooltips import getComp7FightBtnTooltipData
from comp7.gui.impl.lobby.page.lobby_footer import Comp7LobbyFooter
from comp7.gui.impl.lobby.page.lobby_header import Comp7LobbyHeader
from gui.Scaleform.daapi.view.lobby.header.helpers.controls_helpers import DefaultLobbyHeaderHelper
from gui.impl.gen import R
from gui.prb_control.settings import PRE_QUEUE_RESTRICTION
from helpers import dependency, int2roman
from skeletons.gui.game_control import IComp7Controller, IPlatoonController
if typing.TYPE_CHECKING:
    from gui.prb_control.items import ValidationResult
    from gui.impl.pub.view_component import ViewComponent

class Comp7LobbyHeaderHelper(DefaultLobbyHeaderHelper):
    __slots__ = ()
    __comp7Controller = dependency.descriptor(IComp7Controller)
    __platoonController = dependency.descriptor(IPlatoonController)

    @classmethod
    def _getDisabledFightTooltipData(cls, prbValidation, isInSquad):
        return (getComp7FightBtnTooltipData(prbValidation, isInSquad), False)

    @classmethod
    def _getOutSquadTooltipData(cls, prbValidation):
        header = R.strings.platoon.headerButton.tooltips.comp7Squad.header()
        body = R.strings.platoon.headerButton.tooltips.comp7Squad.body()
        params = {}
        if cls.__platoonController.getPermissions().canCreateSquad():
            return (header, body, params)
        header = R.strings.platoon.headerButton.tooltips.comp7Restriction.header()
        if prbValidation.restriction == PRE_QUEUE_RESTRICTION.BAN_IS_SET:
            body = R.strings.platoon.headerButton.tooltips.comp7BanIsSet.body()
        elif not cls.__comp7Controller.hasSuitableVehicles():
            body = R.strings.platoon.headerButton.tooltips.comp7NoSuitableVehicles.body()
            level = int2roman(cls.__comp7Controller.getModeSettings().levels[0])
            params = {'level': level}
        elif not cls.__comp7Controller.isQualificationSquadAllowed():
            body = R.strings.platoon.headerButton.tooltips.comp7QualificationSquad.body()
        else:
            body = R.strings.platoon.headerButton.tooltips.comp7Restriction.body()
        return (header, body, params)

    @classmethod
    def getHeaderType(cls):
        return Comp7LobbyHeader

    @classmethod
    def getFooterType(cls):
        return Comp7LobbyFooter
