# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/paragons/paragons_helpers/paragons_helpers.py
import typing
from account_helpers.AccountSettings import AccountSettings, Paragons as ParagonsAccountSettingsKeys
from account_helpers.settings_core.settings_constants import OnceOnlyHints
from CurrentVehicle import g_currentVehicle
from customization_quests_common import serializeToken
from helpers import dependency
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.event_dispatcher import showStyleProgressionPreview
from gui.shared.utils.requesters import REQ_CRITERIA
from items.vehicles import VehicleDescriptor
from shared_utils import first
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.game_control import IParagonsController
from skeletons.gui.shared import IItemsCache
from skeletons.account_helpers.settings_core import ISettingsCore
if typing.TYPE_CHECKING:
    from helpers.server_settings import ParagonsConfig

def addParagonsUnlockIDToShow(needToShowParagonsUnlockID):
    paragonsUnlockIDsToShow = AccountSettings.getParagons(ParagonsAccountSettingsKeys.NEED_TO_SHOW_ANIMATION_FOR_PARAGONS_UNLOCK_IDS)
    paragonsUnlockIDsToShow.add(needToShowParagonsUnlockID)
    AccountSettings.setParagons(ParagonsAccountSettingsKeys.NEED_TO_SHOW_ANIMATION_FOR_PARAGONS_UNLOCK_IDS, paragonsUnlockIDsToShow)


def deleteParagonsUnlockIDToShow(shownParagonsUnlockID):
    paragonsUnlockIDsToShow = AccountSettings.getParagons(ParagonsAccountSettingsKeys.NEED_TO_SHOW_ANIMATION_FOR_PARAGONS_UNLOCK_IDS)
    paragonsUnlockIDsToShow.discard(shownParagonsUnlockID)
    AccountSettings.setParagons(ParagonsAccountSettingsKeys.NEED_TO_SHOW_ANIMATION_FOR_PARAGONS_UNLOCK_IDS, paragonsUnlockIDsToShow)


@dependency.replace_none_kwargs(settingsCore=ISettingsCore)
def getFirstResetHintShown(settingsCore=None):
    return settingsCore.serverSettings.getOnceOnlyHintsSetting(OnceOnlyHints.PARAGONS_FIRST_RESET_HINT) if settingsCore else False


def setParagonsResetBranchToShow(isShow):
    AccountSettings.setParagons(ParagonsAccountSettingsKeys.NEED_TO_SHOW_ANIMATION_FOR_PARAGONS_RESET_BRANCH, isShow)


def getParagonsResetBranchToShow():
    return AccountSettings.getParagons(ParagonsAccountSettingsKeys.NEED_TO_SHOW_ANIMATION_FOR_PARAGONS_RESET_BRANCH)


def getMaxChapterLevelPoints(paragonsConfig, chapterID, levelID):
    return paragonsConfig.getParagonsCoinsAmountForLevelUnlock(chapterID, levelID)


def getMaxChapterLevel(paragonsConfig, chapterID):
    return max(paragonsConfig.getChapterLevelIDs(chapterID))


@dependency.replace_none_kwargs(c11nService=ICustomizationService)
def onProgressionStylePreview(styleID, group, previewCallback, styleLevel=1, c11nService=None, soundSpace=None):
    style = c11nService.getItemByID(GUI_ITEM_TYPE.STYLE, styleID)
    vehicleCD = _getPreviewVehicle(style)
    availableLevel = _getCurrentStyleProgressLevel(style, group)
    showStyleProgressionPreview(vehicleCD, style, style.getDescription(), previewCallback, backport.text(R.strings.paragons.progressStylePreview.backButton()), styleLevel=styleLevel, availableLevel=availableLevel, progressStyleGroupID=group, notificationText=backport.text(R.strings.paragons.progressStylePreview.progress.description()), showCloseBtn=True, soundSpace=soundSpace)


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def _getCurrentStyleProgressLevel(style, group, itemsCache=None):
    tokenID = serializeToken(style.id, group)
    tokenCount = itemsCache.items.tokens.getTokenCount(tokenID)
    styleLevel = style.descriptor.questsProgression.getLevel(tokenID, tokenCount)
    return styleLevel


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def _getPreviewVehicle(style, itemsCache=None):
    if g_currentVehicle.isPresent() and style.mayInstall(g_currentVehicle.item) and g_currentVehicle.isCustomizationEnabled():
        return g_currentVehicle.item.intCD

    def getVehicle(nextVeh):
        return nextVeh.isInInventory and style.mayInstall(nextVeh) and nextVeh.isCustomizationEnabled()

    getVehicles = itemsCache.items.getVehicles
    sortedVehicles = sorted(getVehicles(REQ_CRITERIA.CUSTOM(getVehicle)).values(), key=lambda vehicle: vehicle.level, reverse=True)
    if sortedVehicles:
        return sortedVehicles[0].intCD
    vehicleDescr = VehicleDescriptor(typeName='germany:G42_Maus')
    return vehicleDescr.type.compactDescr


@dependency.replace_none_kwargs(paragonsCtrl=IParagonsController)
def calculateReceivedLevel(prevTotalCoins, pointsGranted, chapterId, paragonsCtrl=None):
    resultCoins = prevTotalCoins + pointsGranted
    receivedLevel = first((level for level, data in paragonsCtrl.config.rewards.get(chapterId)['levels'].iteritems() if data.get('paragonsCoin') > resultCoins), len(paragonsCtrl.config.getChapterLevelIDs(chapterId)) + 1) - 1
    return receivedLevel
