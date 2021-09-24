# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wt_event/wt_event_bonuses_packers.py
import logging
import typing
from collections import namedtuple
from constants import LOOTBOX_TOKEN_PREFIX, PREMIUM_ENTITLEMENTS
from gui.battle_pass.battle_pass_award import BattlePassAwardsManager, awardsFactory
from gui.battle_pass.battle_pass_bonuses_packers import TmanTemplateBonusPacker
from gui.impl import backport
from gui.impl.auxiliary.rewards_helper import formatEliteVehicle
from gui.impl.backport import TooltipData, createTooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel
from gui.impl.gen.view_models.views.lobby.wt_event.wt_bonus_model import WtBonusModel
from gui.impl.gen.view_models.views.lobby.wt_event.wt_compensation_bonus_model import WtCompensationBonusModel
from gui.impl.gen.view_models.views.lobby.postbattle.events.wt_event_quest_model import WtEventQuestModel
from gui.impl.lobby.wt_event.wt_event_constants import EventCollections
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.VEHICLE_CUSTOMIZATION import VEHICLE_CUSTOMIZATION
from gui.shared.gui_items.customization.c11n_items import isStyle3D
from gui.shared.gui_items.Vehicle import getNationLessName
from gui.shared.money import Currency
from gui.shared.missions.packers.bonus import BonusUIPacker, getDefaultBonusPackersMap, TokenBonusUIPacker, ItemBonusUIPacker, CustomizationBonusUIPacker, VehiclesBonusUIPacker, SimpleBonusUIPacker, GroupsBonusUIPacker
from gui.shared.utils.functions import makeTooltip, replaceHyphenToUnderscore
from helpers import dependency, int2roman
from helpers.i18n import makeString
from skeletons.gui.game_control import IGameEventController, ILootBoxesController
from skeletons.gui.shared import IItemsCache
from shared_utils import first
if typing.TYPE_CHECKING:
    from gui.server_events.bonuses import TokensBonus
    from gui.server_events.bonuses import SimpleBonus
_logger = logging.getLogger(__name__)
_GroupedBonuses = namedtuple('_GroupedBonuses', ('main', 'additional', 'vehicle'))
_MAX_MAIN_BONUSES = 3
_COLLECTION_STR_PATH = R.strings.event.WtEventPortals.inside.rewards.hunterCollectionElement
BOSS_ALL_BONUSES_ORDER = ('vehicles',
 'customizations',
 'battleToken',
 Currency.GOLD,
 Currency.CREDITS,
 'crewBooks',
 'goodies',
 PREMIUM_ENTITLEMENTS.PLUS,
 'items',
 'slots')

def getWtEventBonusPacker():
    mapping = getDefaultBonusPackersMap()
    mapping.update({'items': WtItemBonusUIPacker(),
     'battleToken': WtLootboxTokenBonusPacker(),
     'ticket': WtTicketTokenBonusPacker(),
     'customizations': WtCustomizationBonusUIPacker(),
     'tmanToken': WtTmanTemplateBonusPacker(),
     'vehicles': WtVehiclesBonusUIPacker(),
     'groups': WTEventGroupsBonusUIPacker(),
     'slots': WtSlotBonusPacker()})
    return BonusUIPacker(mapping)


class WtItemBonusUIPacker(ItemBonusUIPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, item, count):
        model = super(WtItemBonusUIPacker, cls)._packSingleBonus(bonus, item, count)
        model.setName(item.getGUIEmblemID())
        return model


class WtSlotBonusPacker(SimpleBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        label = cls._getLocalizedBonusName(bonus.getName(), bonus.getValue())
        return [cls._packSingleBonus(bonus, label if label else '')]

    @classmethod
    def _getLocalizedBonusName(cls, name, count):
        labelStr = R.strings.quests.bonusName.slots if count > 1 else R.strings.event.bonusName.slots
        if labelStr.exists():
            return backport.text(labelStr())
        _logger.warning('Localized text for the label for %s reward was not found', name)


class WtCustomizationBonusUIPacker(CustomizationBonusUIPacker):
    _boxCtrl = dependency.descriptor(ILootBoxesController)

    @classmethod
    def _packSingleBonus(cls, bonus, item, label):
        model = WtBonusModel()
        customizationItem = bonus.getC11nItem(item)
        cls._packCommon(bonus, model)
        model.setValue(str(item.get('value', 0)))
        model.setIcon(cls.__getIcon(customizationItem))
        model.setLabel(cls.__getLabel(customizationItem))
        if isStyle3D(customizationItem):
            model.setSpecialId(customizationItem.intCD)
        return model

    @classmethod
    def __getIcon(cls, item):
        itemName = 'style3d' if isStyle3D(item) else str(item.itemTypeName)
        return '_'.join([itemName, str(item.id)])

    @classmethod
    def __getLabel(cls, customizationItem):
        from gui.Scaleform.daapi.view.lobby.customization.shared import getSuitableText
        if isStyle3D(customizationItem):
            vehicles = getSuitableText(customizationItem, formatVehicle=False)
            return backport.text(R.strings.event.elementBonus.desc.style3d(), value=customizationItem.userName, vehicle=vehicles)
        else:
            key = VEHICLE_CUSTOMIZATION.getElementBonusDesc(customizationItem.itemFullTypeName)
            if key is not None:
                collectionName = cls._boxCtrl.getCollectionType(customizationItem.intCD)
                itemName = makeString(key, value=customizationItem.userName)
                if collectionName is not None and collectionName == EventCollections.HUNTER:
                    return '\n'.join([backport.text(_COLLECTION_STR_PATH()), itemName])
                return itemName
            return ''


class WtTmanTemplateBonusPacker(TmanTemplateBonusPacker):
    _boxCtrl = dependency.descriptor(ILootBoxesController)

    @classmethod
    def _getIcon(cls, recruitInfo, bonusImageName):
        return recruitInfo.getSmallIcon()

    @classmethod
    def _getLabel(cls, bonus, recruitInfo):
        bonusID = first(list(bonus.getValue().iterkeys()))
        collectionName = cls._boxCtrl.getCollectionType(bonusID)
        return '\n'.join([backport.text(_COLLECTION_STR_PATH()), backport.text(R.strings.lootboxes.rewardView.congratsLabel.tankman()), recruitInfo.getFullUserName()]) if collectionName is not None and collectionName == EventCollections.HUNTER else ''


class WtTokenBonusPacker(TokenBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        result = super(WtTokenBonusPacker, cls)._pack(bonus)
        bonusTokens = bonus.getTokens()
        for tokenID, token in bonusTokens.iteritems():
            if cls._isSuitable(tokenID, token):
                model = cls._getBonusModel()
                cls._packToken(token, model)
                result.append(model)

        return result

    @classmethod
    def _getBonusModel(cls):
        return BonusModel()

    @classmethod
    def _isSuitable(cls, tokenID, token):
        return False

    @classmethod
    def _packToken(cls, token, model):
        pass

    @classmethod
    def _getToolTip(cls, bonus):
        result = super(WtTokenBonusPacker, cls)._getToolTip(bonus)
        bonusTokens = bonus.getTokens()
        for tokenID, token in bonusTokens.iteritems():
            if cls._isSuitable(tokenID, token):
                result.append(cls._packTokenTooltip(token))

        return result

    @classmethod
    def _packTokenTooltip(cls, token):
        pass


class WtLootboxTokenBonusPacker(WtTokenBonusPacker):
    _itemsCache = dependency.descriptor(IItemsCache)

    @classmethod
    def _isSuitable(cls, tokenID, token):
        return tokenID.startswith(LOOTBOX_TOKEN_PREFIX) and token.count >= 0 and cls.__isBoxAvailable(tokenID)

    @classmethod
    def _packToken(cls, token, model):
        lootBox = cls._itemsCache.items.tokens.getLootBoxByTokenID(token.id)
        model.setName(lootBox.getType())
        model.setLabel(lootBox.getUserName())
        model.setValue(str(token.count))

    @classmethod
    def _packTokenTooltip(cls, token):
        lootBox = cls._itemsCache.items.tokens.getLootBoxByTokenID(token.id)
        return createTooltipData(isWulfTooltip=True, specialAlias=TOOLTIPS_CONSTANTS.EVENT_LOOTBOX, specialArgs=(lootBox.getType(),))

    @classmethod
    def __isBoxAvailable(cls, tokenID):
        return cls._itemsCache.items.tokens.getLootBoxByTokenID(tokenID) is not None


class WtTicketTokenBonusPacker(WtTokenBonusPacker):
    _gameEventCtrl = dependency.descriptor(IGameEventController)

    @classmethod
    def _isSuitable(cls, tokenID, token):
        return tokenID == cls._gameEventCtrl.getConfig().ticketToken

    @classmethod
    def _packToken(cls, token, model):
        model.setValue(str(token.count))
        model.setName(token.id)

    @classmethod
    def _packTokenTooltip(cls, token):
        return createTooltipData(isWulfTooltip=True, specialAlias=TOOLTIPS_CONSTANTS.EVENT_BATTLES_TICKET, specialArgs=[])


class WtVehiclesBonusUIPacker(VehiclesBonusUIPacker):

    @classmethod
    def _getLabel(cls, vehicle):
        return vehicle.shortUserName

    @classmethod
    def _getCompensationPacker(cls):
        return WtCompensationBonusPacker()

    @classmethod
    def _packTooltip(cls, bonus, vehicle, vehInfo):
        compensation = bonus.compensation(vehicle, bonus)
        return first(cls._packCompensationTooltip(first(compensation), vehicle)) if bonus.compensation(vehicle, bonus) else super(WtVehiclesBonusUIPacker, cls)._packTooltip(bonus, vehicle, vehInfo)

    @classmethod
    def _packCompensationTooltip(cls, bonusComp, vehicle):
        tooltipDataList = super(WtVehiclesBonusUIPacker, cls)._packCompensationTooltip(bonusComp, vehicle)
        return [ cls.__convertCompensationTooltip(bonusComp, vehicle, tooltipData) for tooltipData in tooltipDataList ]

    @classmethod
    def __convertCompensationTooltip(cls, bonusComp, vehicle, _):
        normalizeVehicleName = getNationLessName(replaceHyphenToUnderscore(vehicle.name))
        vehicleIcon = R.images.gui.maps.shop.vehicles.c_180x135.dyn(normalizeVehicleName)()
        specialArgs = {'iconBefore': backport.image(vehicleIcon),
         'labelBefore': '',
         'iconAfter': backport.image(R.images.gui.maps.icons.quests.bonuses.big.gold()),
         'labelAfter': bonusComp.getIconLabel(),
         'bonusName': bonusComp.getName(),
         'vehicleName': vehicle.shortUserName,
         'vehicleType': formatEliteVehicle(vehicle.isElite, vehicle.type),
         'isElite': vehicle.isElite,
         'vehicleLvl': int2roman(vehicle.level)}
        return createTooltipData(isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.EVENT_VEHICLE_COMPENSATION, specialArgs=specialArgs)


class WTEventGroupsBonusUIPacker(GroupsBonusUIPacker):
    __boxesCtrl = dependency.descriptor(ILootBoxesController)
    _IDS_GETTER_MAP = {'battleToken': lambda b: [ t for t in b.getTokens() ],
     'tmanToken': lambda b: [ t for t in b.getTokens() ],
     'customizations': lambda b: [ c.get('id') for c in b.getValue() ]}

    @classmethod
    def _getBonusModel(cls):
        return BonusModel()

    @classmethod
    def _pack(cls, bonus):
        collectionType = cls.__getCollectionType(bonus)
        if not collectionType:
            _logger.warning("Can't recognize collection type: %r", bonus.getValue())
            return super(WTEventGroupsBonusUIPacker, cls)._pack(bonus)
        model = cls._getBonusModel()
        cls._packModel(model, bonus, collectionType)
        return [model]

    @classmethod
    def _packModel(cls, model, bonus, collectionType):
        if collectionType == EventCollections.BOSS:
            uiCollectionType = WtEventQuestModel.BOSS_COLLECTION_ITEM
        else:
            uiCollectionType = WtEventQuestModel.HUNTER_COLLECTION_ITEM
        model.setName(uiCollectionType)
        model.setIsCompensation(bonus.isCompensation())

    @classmethod
    def _getToolTip(cls, bonus):
        collectionType = cls.__getCollectionType(bonus)
        if not collectionType:
            _logger.warning("Can't recognize collection type: %r", bonus.getValue())
            return super(WTEventGroupsBonusUIPacker, cls)._getToolTip(bonus)
        collectionName = 'boss' if collectionType == EventCollections.BOSS else 'hunter'
        collectionRes = R.strings.event.bonuses.dyn('%s_collection' % collectionName)
        return [createTooltipData(makeTooltip(backport.text(collectionRes.tooltip.header()), backport.text(collectionRes.tooltip.body())))]

    @classmethod
    def __getCollectionType(cls, bonus):
        subBonuses = []
        for item in bonus.getValue():
            subBonuses.extend(awardsFactory(item))

        optionalBonuses = []
        for item in subBonuses:
            _, bonuses = item.getOptionalBonusesWithProbability()
            optionalBonuses.extend(bonuses)

        for item in optionalBonuses:
            idsGetter = cls._IDS_GETTER_MAP.get(item.getName())
            if idsGetter is None:
                continue
            ids = idsGetter(item)
            for idx in ids:
                collectionType = cls.__boxesCtrl.getCollectionType(idx)
                if collectionType is not None:
                    return collectionType

        return


class WtCompensationBonusPacker(SimpleBonusUIPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, label):
        model = super(WtCompensationBonusPacker, cls)._packSingleBonus(bonus, label)
        compensationBonus = bonus.getCompensationReason()
        if compensationBonus is not None:
            vehicle = first([ vehicle for vehicle, _ in compensationBonus.getVehicles() ])
            model.setCompensationSource(vehicle.shortUserName)
        return model

    @classmethod
    def _getBonusModel(cls):
        return WtCompensationBonusModel()


class LootBoxAwardsManager(BattlePassAwardsManager):

    @classmethod
    def processCompensation(cls, rewards):
        bonuses, goldBonuses = [], []
        totalCompensation = 0
        for reward in rewards:
            if reward.getName() == Currency.GOLD:
                goldBonuses.append(reward)
            bonuses.append(reward)
            if reward.getName() == 'vehicles':
                totalCompensation += sum(reward.getCompensation())

        if goldBonuses and totalCompensation > 0:
            totalGold = sum((bonus.getValue() for bonus in goldBonuses))
            if totalGold > totalCompensation:
                goldBonus = first(goldBonuses)
                goldBonus.setValue(totalGold - totalCompensation)
                bonuses.append(goldBonus)
        else:
            bonuses.extend(goldBonuses)
        return bonuses

    @classmethod
    def getBossGroupedBonuses(cls, bonuses):
        main, additional, bonusVehicle = [], [], None
        for bonus in bonuses:
            bonusName = bonus.getName()
            if bonusName == 'vehicles':
                bonusVehicle = cls.__getVehicleBonus(bonus)
            if cls._isSpecialAward(bonus):
                main.append(bonus)
            additional.append(bonus)

        if len(bonuses) <= _MAX_MAIN_BONUSES and additional:
            main.extend(additional)
            additional = []
        return _GroupedBonuses(main=main, additional=additional, vehicle=bonusVehicle)

    @classmethod
    def __getVehicleBonus(cls, bonus):
        return first([ vehicle for vehicle, _ in bonus.getVehicles() ])

    @classmethod
    def _isSpecialAward(cls, bonus):
        bonusName = bonus.getName()
        if bonusName == 'vehicles':
            return True
        if bonusName == 'customizations':
            for item in bonus.getCustomizations():
                customizationItem = bonus.getC11nItem(item)
                if isStyle3D(customizationItem):
                    return True

        return False
