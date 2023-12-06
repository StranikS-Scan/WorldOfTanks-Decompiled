# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/common/gui_lootboxes_common/constants_utils.py
import typing
if typing.TYPE_CHECKING:
    from typing import Optional, Dict, Tuple

def addBonusPackerToDefaultMap(packer):
    from gui_lootboxes.gui.bonuses.bonuses_packers import EXTRA_BONUS_PACKER_MAPS_DEFAULT
    EXTRA_BONUS_PACKER_MAPS_DEFAULT.update(packer)


def addBonusPackerToRewardsMap(packer):
    from gui_lootboxes.gui.bonuses.bonuses_packers import EXTRA_BONUS_PACKER_MAPS_REWARDS
    EXTRA_BONUS_PACKER_MAPS_REWARDS.update(packer)


def addBonusPackerToMainRewardsMap(packer):
    from gui_lootboxes.gui.bonuses.bonuses_packers import EXTRA_BONUS_PACKER_MAPS_MAIN_REWARDS
    EXTRA_BONUS_PACKER_MAPS_MAIN_REWARDS.update(packer)


def addBonusesOrder(bonusConfigPath, bonusesSortTags=None, bonusTagsHandlers=None, bonusesKeyFunc=None):
    from gui_lootboxes.gui.bonuses.bonuses_order_config import BONUSES_CONFIG_PATH_LIST
    BONUSES_CONFIG_PATH_LIST.append(bonusConfigPath)
    if bonusesSortTags is not None:
        from gui_lootboxes.gui.bonuses.bonuses_order_config import BonusesSortTags
        for tag in bonusesSortTags:
            setattr(BonusesSortTags, tag, tag)

        BonusesSortTags.RANGE += bonusesSortTags
    if bonusTagsHandlers is not None:
        from gui_lootboxes.gui.bonuses.bonuses_sorter import BONUS_TAG_HANDLER_MAP
        BONUS_TAG_HANDLER_MAP.update(bonusTagsHandlers)
    if bonusesKeyFunc is not None:
        from gui_lootboxes.gui.bonuses.bonuses_sorter import BONUSES_KEY_FUNC
        BONUSES_KEY_FUNC.update(bonusesKeyFunc)
    return


def addSecondaryRewardsProcessor(processor):
    from gui_lootboxes.gui.impl.lobby.gui_lootboxes.reward_screen import SECONDARY_REWARDS_PROCESSORS
    SECONDARY_REWARDS_PROCESSORS.append(processor)


def addBonusProbabilitiesSlotProcessor(processor):
    from gui_lootboxes.gui.impl.lobby.gui_lootboxes.bonus_probabilities_view import SLOT_BONUSES_PROCESSORS
    SLOT_BONUSES_PROCESSORS.append(processor)


def addBonusGroupTooltipProcessor(processor):
    from gui_lootboxes.gui.impl.lobby.gui_lootboxes.tooltips.bonus_group_tooltip import BONUS_GROUP_TOOLTIP_PROCESSORS
    BONUS_GROUP_TOOLTIP_PROCESSORS.append(processor)
