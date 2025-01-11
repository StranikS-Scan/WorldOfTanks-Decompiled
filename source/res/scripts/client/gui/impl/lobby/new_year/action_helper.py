# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/action_helper.py
import typing
from gui.impl.gen.view_models.views.lobby.new_year.ny_constants import ButtonActionType
from gui.impl.new_year.navigation import ViewAliases
from gui.impl.new_year.new_year_helper import ADDITIONAL_BONUS_NAME_GETTERS
from items.components.ny_constants import NyATMReward
from new_year.ny_constants import NYObjects
if typing.TYPE_CHECKING:
    from gui.server_events.bonuses import SimpleBonus
_FIRST_LVL = 1
ACTION_TO_OBJECT = {ButtonActionType.TOEVENT: (NYObjects.TOWN, None),
 ButtonActionType.TOGUESTD: (NYObjects.CELEBRITY_D, None),
 ButtonActionType.TOGUESTC: (NYObjects.CELEBRITY_CAT, None),
 ButtonActionType.TOMARKERTPLACE: (NYObjects.MARKETPLACE, None),
 ButtonActionType.TOGIFTMACHINE: (NYObjects.GIFT_MACHINE, None),
 ButtonActionType.TOREWARDS: (None, ViewAliases.REWARDS_VIEW)}
BONUS_NAME_TO_BUTTON_ACTION = {NyATMReward.DOG: ButtonActionType.TOGUESTD,
 NyATMReward.CAT: ButtonActionType.TOGUESTC,
 NyATMReward.MARKETPLACE: ButtonActionType.TOMARKERTPLACE}

def getBonusesNames(bonuses):
    names = []
    for b in bonuses:
        bonusName = b.getName()
        getAdditionalName = ADDITIONAL_BONUS_NAME_GETTERS.get(bonusName)
        if getAdditionalName is not None:
            bonusName = getAdditionalName(b)
        names.append(bonusName)

    return names


def getButtonAction(level, bonuses):
    if level == _FIRST_LVL:
        return ButtonActionType.TOEVENT
    bonusesNames = getBonusesNames(bonuses)
    for bonusName, action in BONUS_NAME_TO_BUTTON_ACTION.iteritems():
        if bonusName in bonusesNames:
            return action

    return ButtonActionType.UNDEFINED
