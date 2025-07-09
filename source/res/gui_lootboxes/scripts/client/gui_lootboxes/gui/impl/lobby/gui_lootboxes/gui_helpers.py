# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/impl/lobby/gui_lootboxes/gui_helpers.py
from collections import namedtuple
from gui.impl.gen import R
from gui.impl.lobby.loot_box.loot_box_helper import getLootBoxIDFromToken
from gui.server_events.bonuses import VehiclesBonus
from gui.shared.gui_items.Vehicle import getNationLessName
from gui_lootboxes.gui.impl.gen.view_models.views.lobby.gui_lootboxes.lb_bonus_type_model import BonusType
from helpers import dependency
from shared_utils import first
from skeletons.gui.shared import IItemsCache
from constants import LOOTBOX_TOKEN_PREFIX
from gui_lootboxes.gui.shared.events import LootBoxesEvent
from gui_lootboxes.gui.impl.gen.view_models.views.lobby.gui_lootboxes.lootbox_key_view_model import LootboxKeyViewModel
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.gui_items.loot_box import LootBoxKey
VEHICLES_BONUS_NAME = 'vehicles'
_VideoRewardData = namedtuple('_VideoRewardData', ('bonus', 'video', 'isGuaranteed', 'lootbox'))

def detectBonusType(bonuses):
    isVehicleBonus = any((bonus.getName() == VEHICLES_BONUS_NAME for bonus in bonuses))
    if isVehicleBonus:
        for bonus in bonuses:
            if bonus.getName() == VEHICLES_BONUS_NAME:
                _, vehInfo = bonus.getVehicles()[0]
                isRentedVehicle = bonus.isRentVehicle(vehInfo)
                if isRentedVehicle:
                    return BonusType.RENTEDVEHICLE
                return BonusType.VEHICLE

    return BonusType.DEFAULT


def getVideoResForVehicle(vehicle):
    return getNationLessName(vehicle.name).replace('-', '_')


def getVideoExists(lbCategory, videoRes):
    resId = R.videos.lootbox_reward_video.dyn(lbCategory).dyn(videoRes)
    return resId.exists()


def isGuaranteedReward(limitName, usedLimits):
    return usedLimits is not None and limitName in usedLimits


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def getVideoResForLootbox(lootboxToken, itemsCache=None):
    lootBoxID = getLootBoxIDFromToken(lootboxToken)
    lootBox = itemsCache.items.tokens.getLootBoxByID(int(lootBoxID))
    return lootBox.getType()


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def getOpenedLootBoxFromRewards(rewards, itemsCache=None):
    return first((itemsCache.items.tokens.getLootBoxByTokenID(tID) for tID, tData in rewards.get('tokens', {}).iteritems() if tID.startswith(LOOTBOX_TOKEN_PREFIX) and tData.get('count', 0) < 0))


def _videoRewardsSortOrder(rewards, order):
    rewardName = rewards.bonus.getName()
    return order.index(rewardName) if rewardName in order else len(order)


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def processVehicles(rewardsData, vehiclesList, isGuaranteed, lootbox, itemsCache=None, rewardsCategory=None):
    for vehiclesDict in vehiclesList:
        for venIntCD, vehicleData in vehiclesDict.iteritems():
            vehicleBonus = VehiclesBonus('vehicles', {venIntCD: vehicleData})
            if {'rentCompensation', 'customCompensation'}.isdisjoint(vehicleData):
                vehicle = itemsCache.items.getItemByCD(venIntCD)
                video = getVideoResForVehicle(vehicle)
                if getVideoExists(lootbox.getCategory(), video):
                    rewardsData[rewardsCategory].append(_VideoRewardData(vehicleBonus, video, isGuaranteed, lootbox))


def repeatOpen(args=None):
    lootBoxID = int(args.get('lootBoxID', 0))
    count = int(args.get('count', 1))
    keyID = int(args.get('keyID', 0))
    g_eventBus.handleEvent(LootBoxesEvent(LootBoxesEvent.OPEN_LOOTBOXES, ctx={'lootBoxID': lootBoxID,
     'count': count,
     'keyID': keyID}), scope=EVENT_BUS_SCOPE.LOBBY)


def fillKeyModel(keyModel, key):
    keyModel.setKeyID(key.keyID)
    keyModel.setCount(key.count)
    keyModel.keyType.setValue(key.keyType)
    keyModel.setIconName(key.iconName)
    keyModel.setUserName(key.userName)
    keyModel.setOpenProbability(key.openProbability)
