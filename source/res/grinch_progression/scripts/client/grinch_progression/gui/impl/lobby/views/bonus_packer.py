# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch_progression/scripts/client/grinch_progression/gui/impl/lobby/views/bonus_packer.py
import typing
from grinch_progression.gui.impl.gen.view_models.views.lobby.views.rewards_model import RewardsModel
from grinch_progression.gui.impl.gen.view_models.views.lobby.views.enums import RewardRarity
from gui.impl.gen.view_models.common.missions.bonuses.icon_bonus_model import IconBonusModel
from gui.server_events.bonuses import getNonQuestBonuses
from gui.shared.gui_items import getItemTypeID
from gui.shared.missions.packers.bonus import getDefaultBonusPacker
from helpers import dependency
from shared_utils import first
from skeletons.gui.customization import ICustomizationService
if typing.TYPE_CHECKING:
    from typing import Dict
ATTACHMENT_RARITY_TO_GP_RARITY = {'rare': RewardRarity.RARE,
 'epic': RewardRarity.EPIC,
 'legendary': RewardRarity.EPIC}

@dependency.replace_none_kwargs(c11n=ICustomizationService)
def updateRewardBonuses(bonusDict, model, c11n=None):
    packer = getDefaultBonusPacker()
    if not bonusDict:
        return None
    else:
        bonusType, bonusValues = bonusDict.items()[0]
        bonuses = getNonQuestBonuses(bonusType, bonusValues)
        firstBonus = first(bonuses)
        if not firstBonus:
            return None
        packed = packer.pack(firstBonus)[0]
        if bonusType == 'customizations':
            itemType = bonusValues[0].get('custType')
            itemTypeID = getItemTypeID(itemType)
            item = c11n.getItemByID(itemTypeID, bonusValues[0].get('id'))
            model.setId(str(item.intCD))
            if itemType == 'attachment':
                model.setRarity(ATTACHMENT_RARITY_TO_GP_RARITY.get(item.rarity))
                model.setIconName(item.name)
                model.setLabel(item.userName)
                model.setDescription(item.shortDescription)
            if itemType == 'style':
                model.setRarity(RewardRarity.UNCOMMON)
                model.setIconName(item.name)
                model.setLabel(item.userName)
                model.setDescription(item.shortDescription)
        model.setAmount(packed.getValue())
        name = packed.getName()
        if isinstance(packed, IconBonusModel):
            name = packed.getIcon()
        model.setName(name)
        return None
