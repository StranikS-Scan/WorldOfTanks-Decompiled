# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/header/battle_type_selector_config.py
from __future__ import absolute_import
import logging
from functools import partial
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from soft_exception import SoftException

def getBattlePopoverToolTip(tooltip, isSpecial=False, isWulf=False):
    return partial(getPartialBattlePopoverToolTip, tooltip=tooltip, isSpecial=isSpecial, isWulf=isWulf)


def getPartialBattlePopoverToolTip(isDisable, tooltip, isSpecial, isWulf):
    return (tooltip, isSpecial, isWulf)


def getBattleStrongHoldTooltip(itemIsDisabled):
    return (TOOLTIPS.BATTLETYPES_STRONGHOLDS if not itemIsDisabled else TOOLTIPS.BATTLETYPES_STRONGHOLDS_DISABLED, False, False)


def getBattleDefaultTooltip(_):
    return ('', False, False)


def getRankedAvailabilityData(_):
    from helpers import dependency
    from skeletons.gui.game_control import IRankedBattlesController
    rankedController = dependency.descriptor(IRankedBattlesController)
    return (TOOLTIPS_CONSTANTS.RANKED_SELECTOR_INFO if rankedController.isAvailable() else TOOLTIPS_CONSTANTS.RANKED_UNAVAILABLE_INFO, True, False)


BATTLE_POPOVER_TOOLTIPS = {PREBATTLE_ACTION_NAME.RANDOM: getBattlePopoverToolTip(TOOLTIPS.BATTLETYPES_STANDART),
 PREBATTLE_ACTION_NAME.EPIC: getBattlePopoverToolTip(TOOLTIPS_CONSTANTS.EPIC_BATTLE_SELECTOR_INFO, isSpecial=True),
 PREBATTLE_ACTION_NAME.E_SPORT: getBattlePopoverToolTip(TOOLTIPS.BATTLETYPES_UNIT),
 PREBATTLE_ACTION_NAME.TRAININGS_LIST: getBattlePopoverToolTip(TOOLTIPS.BATTLETYPES_TRAINING),
 PREBATTLE_ACTION_NAME.EPIC_TRAINING_LIST: getBattlePopoverToolTip(TOOLTIPS.BATTLETYPES_EPIC_TRAINING),
 PREBATTLE_ACTION_NAME.SPEC_BATTLES_LIST: getBattlePopoverToolTip(TOOLTIPS.BATTLETYPES_SPEC),
 PREBATTLE_ACTION_NAME.BATTLE_ROYALE: getBattlePopoverToolTip(TOOLTIPS_CONSTANTS.BATTLE_ROYALE_SELECTOR_INFO, isSpecial=True),
 PREBATTLE_ACTION_NAME.MAPBOX: getBattlePopoverToolTip(TOOLTIPS_CONSTANTS.MAPBOX_SELECTOR_INFO, isSpecial=True),
 PREBATTLE_ACTION_NAME.STRONGHOLDS_BATTLES_LIST: getBattleStrongHoldTooltip,
 PREBATTLE_ACTION_NAME.RANKED: getRankedAvailabilityData}

def addBattlePopoverTooltip(tooltip, data):
    if tooltip in BATTLE_POPOVER_TOOLTIPS:
        raise SoftException('BATTLE_POPOVER_TOOLTIPS already has tooltip:{tooltip}.'.format(tooltip=tooltip))
    BATTLE_POPOVER_TOOLTIPS.update({tooltip: data})
    msg = 'tooltip:{tooltip} was added to BATTLE_POPOVER_TOOLTIPS.'.format(tooltip=tooltip)
    logging.debug(msg)
