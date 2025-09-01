# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/Scaleform/daapi/view/lobby/header/helpers/controls_helpers.py
from __future__ import absolute_import
import typing
from comp7_light.gui.Scaleform.daapi.view.lobby.header.helpers.fight_btn_tooltips import getComp7LightFightBtnTooltipData
from comp7_light.gui.impl.lobby.page.lobby_footer import Comp7LightLobbyFooter
from comp7_light.gui.impl.lobby.page.lobby_header import Comp7LightLobbyHeader
from gui.Scaleform.daapi.view.lobby.header.helpers.controls_helpers import DefaultLobbyHeaderHelper
from gui.impl.gen import R
from helpers import dependency, int2roman
from skeletons.gui.game_control import IComp7LightController, IPlatoonController
if typing.TYPE_CHECKING:
    from gui.prb_control.items import ValidationResult
    from gui.impl.pub.view_component import ViewComponent

class Comp7LightLobbyHeaderHelper(DefaultLobbyHeaderHelper):
    __slots__ = ()
    __comp7LightController = dependency.descriptor(IComp7LightController)
    __platoonController = dependency.descriptor(IPlatoonController)

    @classmethod
    def _getDisabledFightTooltipData(cls, prbValidation, isInSquad):
        return (getComp7LightFightBtnTooltipData(prbValidation, isInSquad), False)

    @classmethod
    def _getOutSquadTooltipData(cls, prbValidation):
        header = R.strings.platoon.headerButton.tooltips.comp7LightSquad.header()
        body = R.strings.platoon.headerButton.tooltips.comp7LightSquad.body()
        params = {}
        if cls.__platoonController.getPermissions().canCreateSquad():
            return (header, body, params)
        header = R.strings.platoon.headerButton.tooltips.comp7LightRestriction.header()
        if not cls.__comp7LightController.hasSuitableVehicles():
            body = R.strings.platoon.headerButton.tooltips.comp7LightNoSuitableVehicles.body()
            level = int2roman(cls.__comp7LightController.getModeSettings().levels[0])
            params = {'level': level}
        else:
            body = R.strings.platoon.headerButton.tooltips.comp7LightRestriction.body()
        return (header, body, params)

    @classmethod
    def getHeaderType(cls):
        return Comp7LightLobbyHeader

    @classmethod
    def getFooterType(cls):
        return Comp7LightLobbyFooter
