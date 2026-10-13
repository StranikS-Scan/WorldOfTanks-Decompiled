# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/scaleform/daapi/view/lobby/header/helpers/controls_helpers.py
from __future__ import absolute_import
from gui.Scaleform.daapi.view.lobby.header.helpers.controls_helpers import DefaultLobbyHeaderHelper
from gui.Scaleform.daapi.view.lobby.header.helpers.fight_btn_tooltips import getCommonFightBtnTooltipData, getRandomTooltipData

class FortRushLobbyHeaderHelper(DefaultLobbyHeaderHelper):
    __slots__ = ()
    _OUT_SQUAD_TOOLTIP_KEY = 'fortRushSquad'

    @classmethod
    def _getDisabledFightTooltipData(cls, prbValidation, isInSquad):
        return (getCommonFightBtnTooltipData(prbValidation) or getRandomTooltipData(prbValidation, isInSquad), False)
