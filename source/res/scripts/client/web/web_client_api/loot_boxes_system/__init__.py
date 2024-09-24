# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/loot_boxes_system/__init__.py
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.lootbox_system.bonuses_packers import mergeNeededBonuses
from gui.lootbox_system.common import ViewID, Views
from gui.server_events.awards_formatters import AWARDS_SIZES
from gui.shared.event_dispatcher import showHangar
from helpers import dependency
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from shared_utils import first
from skeletons.gui.game_control import ILootBoxSystemController
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.shared import IItemsCache
from web.web_client_api import Field, W2CSchema, WebCommandException, w2c, w2capi
from web.web_client_api.common import ItemPackType, ItemPackTypeGroup, sanitizeResPath

class ViewsIDs(object):
    OVERLAY = 'overlay'
    SHOP = 'shop'
    ALL = (OVERLAY, SHOP)


def _isValidViewID(_, data):
    viewID = data.get('view_id')
    if viewID in ViewsIDs.ALL:
        return True
    raise WebCommandException('viewID: "{}" is not supported'.format(viewID))


class _LootBoxInfo(W2CSchema):
    id = Field(required=True, type=int)


class _ShowViewSchema(W2CSchema):
    id = Field(required=True, type=int)
    view_id = Field(required=False, type=basestring, validator=_isValidViewID)


class _ShowInfoSchema(W2CSchema):
    view_id = Field(required=False, type=basestring, validator=_isValidViewID)


@w2capi(name='loot_box_system', key='action')
class LootBoxSystemWebApi(object):
    __lootBoxes = dependency.descriptor(ILootBoxSystemController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __guiLoader = dependency.instance(IGuiLoader)

    @w2c(_LootBoxInfo, 'get_loot_box_info')
    def getLootBoxInfo(self, cmd):
        result = dict()
        lootBox = self.__itemsCache.items.tokens.getLootBoxByID(cmd.id)
        if lootBox is not None:
            guaranteedFrequency = lootBox.getGuaranteedFrequency()
            attemptsAfterReward = self.__itemsCache.items.tokens.getAttemptsAfterGuaranteedRewards(lootBox)
            result['guaranteed_bonus_limit'] = guaranteedFrequency
            result['max_attempts_to_guaranteed_bonus'] = guaranteedFrequency - attemptsAfterReward
            result['category'] = lootBox.getCategory()
            result['slots'] = self.__addBonusesInfo(self.__lootBoxes.getBoxInfo(cmd.id).get('slots', {}))
        return result

    @w2c(_ShowViewSchema, 'show_box')
    def showBox(self, cmd):
        category = self.__itemsCache.items.tokens.getLootBoxByID(cmd.id).getCategory()
        if cmd.view_id == ViewsIDs.OVERLAY:
            self.__closeExistingShopOverlay()
            Views.load(ViewID.MAIN, None, category=category)
        elif cmd.view_id == ViewsIDs.SHOP:
            showHangar()
            Views.load(ViewID.MAIN, None, category=category)
        return

    @w2c(_ShowInfoSchema, 'show_info_page')
    def showInfoPage(self, cmd):
        Views.load(ViewID.INFO, cmd.view_id)
        if cmd.view_id == ViewsIDs.OVERLAY:
            self.__closeExistingShopOverlay()

    def __addBonusesInfo(self, slotsInfo):
        result = {}
        for idx, slotData in slotsInfo.iteritems():
            bonuses = mergeNeededBonuses(slotData.get('bonuses', []))
            result.update({idx: {'probability': int(slotData.get('probability', [0])[0] * 10000 + 1e-06) / 100.0,
                   'bonuses': []}})
            for bonus in bonuses:
                bonusList = bonus.getWrappedEventLootBoxesBonusList()
                for bonusEntry in bonusList:
                    if bonusEntry['type'] in ItemPackTypeGroup.VEHICLE:
                        bonusEntry['type'] = ItemPackType.VEHICLE
                        for size in AWARDS_SIZES.ALL():
                            bonusEntry['icon'][size] = RES_ICONS.getVehicleAwardIcon(size)

                    if not self.__isExistingBonus(bonusEntry, result[idx]['bonuses']):
                        bonusEntry['icon'] = {size:sanitizeResPath(path) for size, path in bonusEntry['icon'].iteritems()}
                        result[idx]['bonuses'].append(bonusEntry)
                        if bonusEntry.get('overlayIcon') is not None:
                            bonusEntry['overlayIcon'] = {size:sanitizeResPath(path) for size, path in bonusEntry['overlayIcon'].iteritems()}

        return result

    @staticmethod
    def __isExistingBonus(bonusEntry, bonuses):
        return bonusEntry['type'] in (b['type'] for b in bonuses)

    def __closeExistingShopOverlay(self):
        window = first(self.__guiLoader.windowsManager.findWindows(lambda w: w.content is not None and getattr(w.content, 'alias', None) == VIEW_ALIAS.OVERLAY_WEB_STORE))
        if window is not None:
            window.destroy()
        return
