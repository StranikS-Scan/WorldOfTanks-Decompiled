# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/loot_box/ny_loot_box_helper.py
import logging
from collections import namedtuple
import typing
import BigWorld
from constants import LOOTBOX_TOKEN_PREFIX
from gui import SystemMessages
from gui.impl import backport
from gui.impl.auxiliary.rewards_helper import getRewardTooltipContent, LootVehicleVideoRewardPresenter, LootNewYearToyPresenter, LootNewYearFragmentsCompensationPresenter, LootTankmanCongratsRewardPresenter, LootStyleCongratsRewardPresenter
from gui.impl.gen import R
from gui.impl.lobby.new_year.tooltips.ny_decoration_tooltip import NyDecorationTooltip
from gui.impl.lobby.new_year.tooltips.ny_guaranteed_reward_tooltip import NyGuaranteedRewardTooltip
from gui.shared.notifications import NotificationPriorityLevel
from helpers import dependency
from items.components.ny_constants import CurrentNYConstants
from shared_utils import first
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.loot_box import LootBox
MAX_PREMIUM_BOXES_TO_OPEN = 5
SpecialRewardData = namedtuple('SpecialRewardData', ('sourceName', 'congratsType', 'congratsSourceId', 'vehicleName', 'vehicleLvl', 'vehicleIsElite', 'vehicleType', 'backToSingleOpening', 'isGuaranteedReward'))
_MODEL_PRESENTERS = {'vehicles': LootVehicleVideoRewardPresenter(),
 'tmanToken': LootTankmanCongratsRewardPresenter(),
 'customizations': LootStyleCongratsRewardPresenter(),
 CurrentNYConstants.TOYS: LootNewYearToyPresenter(),
 CurrentNYConstants.TOY_FRAGMENTS: LootNewYearFragmentsCompensationPresenter()}
_logger = logging.getLogger(__name__)

def showRestrictedSysMessage():

    def _showRestrictedSysMessage():
        SystemMessages.pushMessage(text=backport.text(R.strings.lootboxes.restrictedMessage.body()), type=SystemMessages.SM_TYPE.ErrorHeader, priority=NotificationPriorityLevel.MEDIUM, messageData={'header': backport.text(R.strings.lootboxes.restrictedMessage.header())})

    BigWorld.callback(0.0, _showRestrictedSysMessage)


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def isLootboxValid(boxType, itemsCache=None):
    return any((box.getType() == boxType for box in itemsCache.items.tokens.getLootBoxes().itervalues()))


def getTooltipContent(event, storedTooltipData):
    tooltipContent = getRewardTooltipContent(event, storedTooltipData)
    if tooltipContent is not None:
        return tooltipContent
    else:
        tooltipContentRes = R.views.lobby.new_year.tooltips
        if event.contentID == tooltipContentRes.NyDecorationTooltip():
            toyID = event.getArgument('toyID')
            return NyDecorationTooltip(toyID, isToyIconEnabled=False)
        return NyGuaranteedRewardTooltip() if event.contentID == R.views.lobby.new_year.tooltips.NyGuaranteedRewardTooltip() else None


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def getOpenedLootBoxFromRewards(rewards, itemsCache=None):
    return first((itemsCache.items.tokens.getLootBoxByTokenID(tID) for tID, tData in rewards.get('tokens', {}).iteritems() if tID.startswith(LOOTBOX_TOKEN_PREFIX) and tData.get('count', 0) < 0))
