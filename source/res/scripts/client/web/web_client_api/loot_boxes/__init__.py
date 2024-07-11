# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/loot_boxes/__init__.py
from helpers import dependency
from skeletons.gui.game_control import IGuiLootBoxesController
from skeletons.gui.game_control import IReferralProgramController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from web.web_client_api import Field, W2CSchema, w2c, w2capi
from web.web_client_api.common import ItemPackType, sanitizeResPath, ItemPackTypeGroup
from web.web_client_api.loot_boxes.bonus_wrappers import RandomCrewBooksWrapper, RandomGuideWrapper, RandomNationalBlueprintWrapper, CollectionItemWrapper, BonusAggregateWrapper
from gui_lootboxes.gui.storage_context.context import ReturnPlaces
from gui.Scaleform.daapi.view.lobby.referral_program import referral_program_helpers

class _LootBoxSchema(W2CSchema):
    id = Field(required=True, type=int)


class _LootBoxStorageViewSchema(W2CSchema):
    id = Field(required=False, type=int, default=0)
    lootbox_id = Field(required=False, type=int, default=0)
    category = Field(required=False, type=basestring)
    lootBoxType = Field(required=False, type=basestring)


_BONUS_WRAPPERS = {ItemPackType.CREW_BOOK_BROCHURE: RandomCrewBooksWrapper,
 ItemPackType.CREW_BOOK_GUIDE: RandomGuideWrapper,
 ItemPackType.BLUEPRINT_NATIONAL: RandomNationalBlueprintWrapper,
 ItemPackType.CUSTOM_COLLECTION_ENTITLEMENT: CollectionItemWrapper}
_SPECIAL_BONUS_ALIASES = {}

def addBonusWrappers(bonusWrappers):
    _BONUS_WRAPPERS.update(bonusWrappers)


def addBonusAlias(bonusAliases):
    _SPECIAL_BONUS_ALIASES.update(bonusAliases)


@w2capi(name='loot_box', key='action')
class LootBoxWebApi(object):
    __itemsCache = dependency.descriptor(IItemsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __guiLootBoxes = dependency.descriptor(IGuiLootBoxesController)

    @w2c(_LootBoxSchema, 'get_loot_box_info')
    def getLootBoxInfo(self, cmd):
        result = dict()
        lootBox = self.__itemsCache.items.tokens.getLootBoxByID(cmd.id)
        if lootBox is not None:
            result = self.__parseBoxInfo(lootBox)
        return result

    def __parseBoxInfo(self, lootBox):
        result = dict()
        result.update({'slots': {}})
        if lootBox.getGuaranteedFrequency() > 0:
            attemptsAfterGuaranteed = self.__itemsCache.items.tokens.getAttemptsAfterGuaranteedRewards(lootBox)
            limitsSection = result.setdefault('limits', {})
            limitsSection['attempts_after_guaranteed'] = attemptsAfterGuaranteed
            limitsSection['guaranteed_frequency'] = lootBox.getGuaranteedFrequency()
            limitsSection['guaranteedLevels'] = lootBox.getGuaranteedVehicleLevelsRange()
        for idx, slotData in lootBox.getBonusSlots().iteritems():
            result['slots'][idx] = self.__parseSlot(slotData)

        if lootBox.hasLootLists():
            result['lootLists'] = []
            for lootList in lootBox.getLootLists():
                lootListSlots = {}
                for idx, lootListData in lootList.iteritems():
                    lootListSlots[idx] = self.__parseSlot(lootListData)

                result['lootLists'].append(lootListSlots)

        return result

    def __parseSlot(self, slotData):
        result = {}
        aggregatedBonusesMap = {}
        supportedTypesByWrappers = set(_BONUS_WRAPPERS.keys() + _SPECIAL_BONUS_ALIASES.keys())
        result.update({'probability': round(slotData.get('probability', [[0]])[0][0] * 100, 2),
         'bonuses': []})
        for bonus in slotData.get('bonuses', []):
            bonusList = bonus.getWrappedLootBoxesBonusList()
            for bonusEntry in bonusList:
                bonusType = bonusEntry['type']
                if bonusType in supportedTypesByWrappers:
                    alias = _SPECIAL_BONUS_ALIASES.get(bonusType, bonusType)
                    aggregatedBonuses = aggregatedBonusesMap.setdefault(alias, [])
                    aggregatedBonuses.append(bonusEntry)
                if not self.__isExistingVehicle(bonusEntry, result['bonuses']):
                    bonusEntry['icon'] = {size:sanitizeResPath(path) for size, path in bonusEntry['icon'].iteritems()}
                    result['bonuses'].append(bonusEntry)

        result['bonuses'].extend([ _BONUS_WRAPPERS.get(bType, BonusAggregateWrapper).getWrappedBonus(bValues) for bType, bValues in aggregatedBonusesMap.iteritems() ])
        return result

    @staticmethod
    def __isExistingVehicle(bonusEntry, bonuses):
        return bonusEntry['type'] in ItemPackTypeGroup.VEHICLE and bonusEntry['id'] in (b['id'] for b in bonuses)

    @w2c(W2CSchema, name='get_loot_boxes_key_info')
    def getLootBoxesKeyInfo(self, _):
        lootBoxes = self.__guiLootBoxes.getGuiLootBoxes()
        keysForLootBoxes = {}
        for lootBox in lootBoxes:
            unlockKeys = lootBox.getUnlockKeyIDs()
            for unlockKey in unlockKeys:
                keysForLootBoxes.setdefault(unlockKey, set()).add(lootBox.getID())

        configInfo = self.__lobbyContext.getServerSettings().getLootBoxKeyConfig().values()
        for config in configInfo:
            keyID = config['id']
            config.update({'count': self.__guiLootBoxes.getKeyByID(keyID).count,
             'lootBoxes': list(keysForLootBoxes[keyID])})

        return {'keyConfig': configInfo}


class LootBoxesWindowWebApiMixin(object):

    @w2c(_LootBoxStorageViewSchema, 'lootboxes_storage_window')
    def showLootBoxesStorage(self, cmd):
        from gui_lootboxes.gui.shared.event_dispatcher import showStorageView
        from gui_lootboxes.gui.shared.event_dispatcher import showSpecificBoxInStorageView
        if cmd.id:
            showStorageView(initialLootBoxId=cmd.id)
        else:
            showSpecificBoxInStorageView(category=cmd.category, lootBoxType=cmd.lootBoxType)


class ReferralLootBoxesWindowWebApiMixin(object):
    __referralCtrl = dependency.descriptor(IReferralProgramController)

    @w2c(_LootBoxStorageViewSchema, 'referral_lootboxes_storage_window')
    def showReferralLootBoxesStorage(self, cmd):
        from gui_lootboxes.gui.shared.event_dispatcher import showStorageView
        from gui_lootboxes.gui.shared.event_dispatcher import showSpecificBoxInStorageView

        def closeCallback():
            url = referral_program_helpers.getReferralShopURL()
            self.__referralCtrl.showWindow(url=url)

        if cmd.lootbox_id:
            showStorageView(initialLootBoxId=cmd.lootbox_id, returnPlace=ReturnPlaces.TO_REFERRAL)
        else:
            showSpecificBoxInStorageView(category=cmd.category, lootBoxType=cmd.lootBoxType, returnPlace=ReturnPlaces.TO_REFERRAL, closeCallback=closeCallback)
