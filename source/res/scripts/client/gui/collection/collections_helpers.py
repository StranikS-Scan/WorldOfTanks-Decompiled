# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/collection/collections_helpers.py
import typing
import SoundGroups
import nations
from CurrentVehicle import g_currentVehicle
from collections_common import UNUSABLE_COLLECTION_ENTITIES, USABLE_COLLECTION_ENTITIES
from gui.battle_pass.battle_pass_helpers import getSingleVehicleForCustomization
from gui.collection.collections_constants import COLLECTION_ITEM_RES_KEY_TEMPLATE, COLLECTION_RES_PREFIX
from gui.collection.sounds import Sounds
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.collection.collection_item_preview_model import ItemType
from gui.server_events.bonuses import getNonQuestBonuses, mergeBonuses, splitBonuses
from gui.server_events.events_dispatcher import showMissionsBattlePass
from gui.shared.event_dispatcher import showHangar, showStylePreview, showStyleProgressionPreview
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.sounds.filters import switchHangarFilteredFilter
from helpers import dependency
from helpers.dependency import replace_none_kwargs
from items.tankmen import getNationConfig, getNationGroups
from shared_utils import findFirst, first
from skeletons.gui.game_control import ICollectionsSystemController
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from typing import List, Dict, Optional, Tuple, Union
    from collections_common import CollectionItem
    from gui.impl.gen_utils import DynAccessor
    from gui.shared.gui_items.Vehicle import Vehicle

@replace_none_kwargs(itemsCache=IItemsCache)
def showCollectionStylePreview(styleCD, backCallback=None, backBtnDescrLabel='', itemsCache=None):
    style = itemsCache.items.getItemByCD(styleCD)
    vehicle = getVehicleForCollectionStyle(style)
    (showStyleProgressionPreview if style.isProgression else showStylePreview)(vehicle.intCD, style, style.getDescription(), backCallback or showHangar, backBtnDescrLabel)


@replace_none_kwargs(itemsCache=IItemsCache)
def getVehicleForCollectionStyle(style, itemsCache=None):

    def mayInstall(veh):
        return not veh.descriptor.type.isCustomizationLocked and style.mayInstall(veh)

    vehicle = g_currentVehicle.item if g_currentVehicle.isPresent() else None
    if vehicle is not None and mayInstall(vehicle):
        return vehicle
    else:
        suitableVehicles = (v for v in itemsCache.items.getVehicles(criteria=REQ_CRITERIA.VEHICLE.FOR_ITEM(style)).itervalues() if mayInstall(v))
        isInInventory, isNotSecret = (None, None)
        for v in sorted(suitableVehicles, key=lambda item: item.level, reverse=True):
            if isInInventory is None and v.isInInventory:
                isInInventory = v
                break
            if isNotSecret is None and not v.isSecret:
                isNotSecret = v

        return isInInventory or isNotSecret


def setHangarState():
    SoundGroups.g_instance.setState(Sounds.STATE_PLACE.value, Sounds.STATE_PLACE_GARAGE.value)
    switchHangarFilteredFilter(on=False)


def loadHangarFromCollections():
    showHangar()
    setHangarState()


def loadBattlePassFromCollections(layoutID=None, chapterID=0):
    showMissionsBattlePass(layoutID, chapterID)
    SoundGroups.g_instance.setState(Sounds.STATE_PLACE.value, Sounds.STATE_PLACE_TASKS.value)


@replace_none_kwargs(collections=ICollectionsSystemController)
def getItemInfo(itemId, collectionId, collections=None):
    item = collections.getCollectionItem(collectionId, itemId)
    name = getItemName(collectionId, item, collectionsSystem=collections)
    itemResKey = getItemResKey(collectionId, item)
    collectionRes = getCollectionRes(collectionId, collectionsSystem=collections)
    descriptionRes = collectionRes.item.description.dyn(itemResKey)
    description = backport.text(descriptionRes()) if descriptionRes.exists() else ''
    largeImageRes = R.images.gui.maps.icons.collectionItems.c_1000x680.dyn(itemResKey)
    largeImage = backport.image(largeImageRes()) if largeImageRes.exists() else ''
    mediumImageRes = R.images.gui.maps.icons.collectionItems.c_600x450.dyn(itemResKey)
    mediumImage = backport.image(mediumImageRes()) if mediumImageRes.exists() else ''
    smallImageRes = R.images.gui.maps.icons.collectionItems.c_400x300.dyn(itemResKey)
    smallImage = backport.image(smallImageRes()) if smallImageRes.exists() else ''
    itemType = getItemPreviewType(item)
    return (name,
     itemType,
     description,
     largeImage,
     mediumImage,
     smallImage)


def getImagePath(imageResource):
    return backport.image(imageResource()) if imageResource.exists() else ''


def getItemResKey(collectionId, item):
    return COLLECTION_ITEM_RES_KEY_TEMPLATE.format(item.type, collectionId, item.itemId)


@replace_none_kwargs(collectionsSystem=ICollectionsSystemController)
def getCollectionRes(collectionId, collectionsSystem=None):
    collectionName = collectionsSystem.getCollection(collectionId).name
    return R.strings.dyn(COLLECTION_RES_PREFIX + collectionName)


@replace_none_kwargs(collectionsSystem=ICollectionsSystemController)
def getItemName(collectionId, item, collectionsSystem=None):
    return getUnusableItemName(collectionId, item, collectionsSystem=collectionsSystem) if item.type in UNUSABLE_COLLECTION_ENTITIES else getUsableItemName(item)


def getUsableItemName(item):
    if item.type == 'customizationItem':
        return getCustomizationName(item.relatedId)
    if item.type == 'dossier':
        return getDossierName(item.relatedId)
    return getTankmanFullName(item.relatedId) if item.type == 'tankman' else ''


@replace_none_kwargs(collectionsSystem=ICollectionsSystemController)
def getUnusableItemName(collectionId, item, collectionsSystem=None):
    itemTextRes = getCollectionRes(collectionId, collectionsSystem=collectionsSystem).item
    return backport.text(itemTextRes.name.dyn(getItemResKey(collectionId, item))())


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def getCustomizationName(itemCD, itemsCache=None):
    customizationItem = itemsCache.items.getItemByCD(itemCD)
    textRes = R.strings.tooltips.vehiclePreview.boxTooltip.dyn(customizationItem.itemTypeName)
    return backport.text(textRes.header(), value=customizationItem.userName)


def getDossierName(itemName):
    _, recordName = itemName
    recordRes = backport.text(R.strings.achievements.dyn(recordName)())
    return backport.text(R.strings.collections.tooltips.item.achievement(), name=recordRes)


def getTankmanFullName(groupName):
    for nationId in nations.MAP.iterkeys():
        group = findFirst(lambda nationGroup: nationGroup.name == groupName, getNationGroups(nationId, True).values() + getNationGroups(nationId, False).values())
        if group is not None:
            firstNameId, lastNameId = first(group.firstNamesList), first(group.lastNamesList)
            nationConfig = getNationConfig(nationId)
            firstName, lastName = nationConfig.getFirstName(firstNameId), nationConfig.getLastName(lastNameId)
            return '{} {}'.format(firstName, lastName)

    return ''


def getItemPreviewType(item):
    itemType = item.type
    if itemType in USABLE_COLLECTION_ENTITIES:
        if itemType == 'customizationItem':
            return getCustomizationPreviewType(item.relatedId)
        if itemType == 'dossier':
            return ItemType.MEDAL
    return ItemType(itemType)


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def getCustomizationPreviewType(itemCD, itemsCache=None):
    customizationItem = itemsCache.items.getItemByCD(itemCD)
    if customizationItem.itemTypeID == GUI_ITEM_TYPE.STYLE:
        if customizationItem.modelsSet:
            return ItemType.STYLE3D
        return ItemType.STYLE2D
    return ItemType.OTHERCUSTOMIZATION


@dependency.replace_none_kwargs(itemsCache=IItemsCache, collectionsSystem=ICollectionsSystemController)
def getVehicleForStyleItem(item, itemsCache=None, collectionsSystem=None):
    customizationItem = itemsCache.items.getItemByCD(item.relatedId)
    vehicleCD = getSingleVehicleForCustomization(customizationItem)
    return itemsCache.items.getItemByCD(vehicleCD) if vehicleCD is not None else None


def composeBonuses(bonuses):
    composedBonuses = []
    for bonus in bonuses:
        for key, value in bonus.iteritems():
            composedBonuses.extend(getNonQuestBonuses(key, value, ctx=None))

    mergedBonuses = mergeBonuses(composedBonuses)
    return splitBonuses(mergedBonuses)
