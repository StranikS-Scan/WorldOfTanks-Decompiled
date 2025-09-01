# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/Scaleform/daapi/view/lobby/header/helpers/fight_btn_tooltips.py
from __future__ import absolute_import
from gui.Scaleform.daapi.view.lobby.header.helpers.fight_btn_tooltips import getRandomTooltipData
from gui.impl import backport
from gui.impl.gen import R
from gui.periodic_battles.models import PrimeTimeStatus
from gui.shared.utils.functions import makeTooltip
from helpers import dependency, int2roman
from skeletons.gui.game_control import IComp7LightController

@dependency.replace_none_kwargs(comp7LightController=IComp7LightController)
def _getPrimeTimeStatus(comp7LightController=None):
    status, _, _ = comp7LightController.getPrimeTimeStatus()
    return status


@dependency.replace_none_kwargs(comp7LightController=IComp7LightController)
def getComp7LightFightBtnTooltipData(result, isInSquad, comp7LightController=None):
    resShortCut = R.strings.menu.headerButtons.fightBtn.tooltip
    if not comp7LightController.hasSuitableVehicles():
        romanLevels = list(map(int2roman, comp7LightController.getModeSettings().levels))
        delimiter = backport.text(resShortCut.comp7LightVehLevel.delimiter())
        vehicleLevelsStr = delimiter.join(romanLevels)
        header = backport.text(resShortCut.comp7LightVehLevel.header())
        body = backport.text(resShortCut.comp7LightVehLevel.body(), levels=vehicleLevelsStr)
    elif _getPrimeTimeStatus() != PrimeTimeStatus.AVAILABLE:
        header = backport.text(resShortCut.comp7LightDisabled.header())
        body = backport.text(resShortCut.comp7LightDisabled.body())
    else:
        return getRandomTooltipData(result, isInSquad)
    return makeTooltip(header, body)
