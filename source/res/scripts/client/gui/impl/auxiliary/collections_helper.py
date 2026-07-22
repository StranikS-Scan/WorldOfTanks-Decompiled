# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/auxiliary/collections_helper.py
import typing
from account_helpers import AccountSettings
from account_helpers.AccountSettings import IS_BATTLE_PASS_COLLECTION_SEEN
from gui.collection.collections_constants import COLLECTION_ITEM_BONUS_NAME
from gui.collection.collections_helpers import getItemName, getItemResKey
from gui.impl import backport
from gui.impl.backport import createTooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.collection.reward_model import RewardModel
from gui.shared.missions.packers.bonus import getDefaultBonusPackersMap, BonusUIPacker, SimpleBonusUIPacker, CustomizationBonusUIPacker, TmanTemplateBonusPacker
from gui.shared.money import Currency
from helpers.dependency import replace_none_kwargs
from skeletons.gui.game_control import ICollectionsSystemController
if typing.TYPE_CHECKING:
    from typing import Dict
    from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel
    from gui.impl.gen.view_models.common.missions.bonuses.icon_bonus_model import IconBonusModel
    from gui.impl.gen.view_models.views.lobby.battle_pass.collection_entry_point_view_model import CollectionEntryPointViewModel
    from gui.server_events.bonuses import SimpleBonus, CollectionEntitlementBonus, BpcoinBonus, CustomizationsBonus
    from gui.impl.backport import TooltipData

@replace_none_kwargs(collectionsSystem=ICollectionsSystemController)
def fillCollectionModel(model, collectionId, collectionsSystem=None):
    isEnabled = collectionsSystem.isEnabled() and collectionsSystem.getCollection(collectionId) is not None
    model.setIsCollectionsEnabled(isEnabled)
    if isEnabled:
        model.setCollectionItemCount(collectionsSystem.getReceivedProgressItemCount(collectionId))
        model.setMaxCollectionItemCount(collectionsSystem.getMaxProgressItemCount(collectionId))
        model.setNewCollectionItemCount(collectionsSystem.getNewLinkedCollectionsItemCount(collectionId))
        model.setIsFirstEnter(not AccountSettings.getSettings(IS_BATTLE_PASS_COLLECTION_SEEN))
    return


def getCollectionsBonusPacker():
    mapping = getDefaultBonusPackersMap()
    currencyPacker = CurrencyBonusUIPacker()
    mapping.update({COLLECTION_ITEM_BONUS_NAME: CollectionItemBonusPacker(),
     Currency.BPCOIN: BattlePassCoinBonusPacker(),
     Currency.CREDITS: currencyPacker,
     Currency.CRYSTAL: currencyPacker,
     Currency.GOLD: currencyPacker,
     'customizations': CustomizationsBonusPacker(),
     'freeXP': currencyPacker,
     'tmanToken': TmanTemplateBonusPacker()})
    return BonusUIPacker(mapping)


class CurrencyBonusUIPacker(SimpleBonusUIPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, label):
        label = str(bonus.getValue())
        model = super(CurrencyBonusUIPacker, cls)._packSingleBonus(bonus, label)
        return model


class BattlePassCoinBonusPacker(CurrencyBonusUIPacker):

    @classmethod
    def _getContentId(cls, bonus):
        return [R.views.lobby.battle_pass.tooltips.BattlePassCoinTooltipView()]

    @classmethod
    def _packSingleBonus(cls, bonus, label):
        model = super(BattlePassCoinBonusPacker, cls)._packSingleBonus(bonus, label)
        model.setLabel(backport.text(R.strings.battle_pass.tooltips.battlePassCoins.title()))
        return model


class CustomizationsBonusPacker(CustomizationBonusUIPacker):
    _3D_STYLE_ICON_NAME = 'style_3d'

    @classmethod
    def _packSingleBonus(cls, bonus, item, label):
        model = super(CustomizationsBonusPacker, cls)._packSingleBonus(bonus, item, label)
        customizationItem = bonus.getC11nItem(item)
        iconName = customizationItem.itemTypeName
        if iconName == 'style' and customizationItem.modelsSet:
            iconName = 'style_3d'
        model.setIcon(iconName)
        model.setLabel(customizationItem.userName)
        return model


class CollectionItemBonusPacker(SimpleBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        return [cls._packSingleBonus(bonus, '')]

    @classmethod
    def _packSingleBonus(cls, bonus, label):
        model = super(CollectionItemBonusPacker, cls)._packSingleBonus(bonus, label)
        item = bonus.getItem()
        collectionId = bonus.getCollectionId()
        model.setIcon(getItemResKey(collectionId, item))
        model.setLabel(getItemName(collectionId, item))
        model.setValue('')
        return model

    @classmethod
    def _getContentId(cls, bonus):
        return [R.views.lobby.collection.tooltips.CollectionItemTooltipView()]

    @classmethod
    def _getToolTip(cls, bonus):
        itemId = bonus.getItemId()
        collectionId = bonus.getCollectionId()
        tooltipData = [createTooltipData(tooltip=None, isSpecial=True, specialAlias=None, specialArgs=[itemId, collectionId])]
        return tooltipData

    @classmethod
    def _getBonusModel(cls):
        return RewardModel()
