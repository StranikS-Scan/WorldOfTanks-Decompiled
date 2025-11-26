# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/lootbox_system/base/views_loaders.py
import logging
from typing import TYPE_CHECKING
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.customization.context.styled_mode import StyledMode
from gui.customization.constants import CustomizationModes
from gui.impl.gen import R
from gui.lootbox_system.base.common import ViewID, Views
from gui.lootbox_system.base.utils import getIntroVideoUrl, getIsShowIntro, getShopOverlayUrl, getVehicleForStyle
from gui.Scaleform.daapi.view.common.battle_royale.br_helpers import currentHangarIsBattleRoyale
from gui.shared.event_dispatcher import hideVehiclePreview, selectVehicleInHangar, showBrowserOverlayView, showStylePreview, showShop, showVehiclePreviewWithoutBottomPanel
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from shared_utils import first
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.shared import IItemsCache
from soft_exception import SoftException
if TYPE_CHECKING:
    from gui.shared.gui_items.customization.c11n_items import Style
_logger = logging.getLogger(__name__)

def showIntro(eventName):
    if getIsShowIntro(eventName):
        showBrowserOverlayView(getIntroVideoUrl(eventName), VIEW_ALIAS.LOOT_BOXES_INTRO_BROWSER_VIEW)


def showMain(eventName, subViewID=None, category='', count=0, bonuses=None, *args, **kwargs):
    from gui.impl.lobby.lootbox_system.states import LootBoxMainState
    LootBoxMainState.goTo({'subViewID': subViewID,
     'eventName': eventName,
     'count': count,
     'category': category,
     'bonuses': bonuses})


def showInfo(eventName, category=''):
    from gui.impl.lobby.lootbox_system.states import LootBoxInfoState
    LootBoxInfoState.goTo({'category': category,
     'eventName': eventName})


def showAutoOpen(eventName, rewards, boxes):
    from gui.impl.lobby.lootbox_system.states import LootBoxAutoOpenState
    LootBoxAutoOpenState.goTo({'eventName': eventName,
     'rewards': rewards,
     'boxes': boxes})


@dependency.replace_none_kwargs(customization=ICustomizationService, itemsCache=IItemsCache)
def showItemPreview(itemType, itemID, styleID, customization=None, itemsCache=None):
    if itemType == 'vehicles':
        vehicle = itemsCache.items.getItemByCD(itemID)
        if vehicle.isInInventory:
            window = findActiveWindow(R.views.mono.lootbox.main())
            if window is not None:
                window.destroyWindow()
            selectVehicleInHangar(itemID, loadHangar=True)
        else:
            style = customization.getItemByID(GUI_ITEM_TYPE.STYLE, styleID) if styleID else None
            showVehiclePreviewWithoutBottomPanel(itemID, style=style)
    elif itemType == 'customizations':
        style = customization.getItemByID(GUI_ITEM_TYPE.STYLE, itemID)
        if style.is3D and not currentHangarIsBattleRoyale():
            showCustomizationHangar(style)
        else:
            showVehicleStylePreview(style)
    else:
        _logger.error('Type "%s" is not supported for preview', itemType)
    return


def hideItemPreview():
    hideVehiclePreview(back=False, close=True)


@dependency.replace_none_kwargs(customization=ICustomizationService, itemsCache=IItemsCache)
def showCustomizationHangar(style, itemsCache=None, customization=None):

    def _callback():
        if style is not None:
            installedOn = style.getInstalledVehicles()
            if vehicle.intCD not in installedOn:
                ctx = customization.getCtx()
                ctx.changeMode(CustomizationModes.STYLE_3D if style.is3D else CustomizationModes.STYLE_2D)
                ctx.mode.installItem(style.intCD, StyledMode.STYLE_SLOT)
                ctx.selectItem(style.intCD)
        return

    vehicles = itemsCache.items.getVehicles(REQ_CRITERIA.CUSTOM(style.mayInstall))
    vehicle = first(vehicles.itervalues()) if vehicles else None
    if style.isInInventory and vehicle is not None and vehicle.isInInventory and vehicle.isCustomizationEnabled():
        customization.showCustomization(vehicle.invID, callback=_callback)
    else:
        showVehicleStylePreview(style)
    return


def showVehicleStylePreview(style):
    if style.isProgression:
        raise SoftException('Progression styles is not supported')
    vehicle = getVehicleForStyle(style)
    showStylePreview(vehicle.intCD, style)


def openShop(eventName, parent=None):
    showShop(getShopOverlayUrl(eventName))


@dependency.replace_none_kwargs(uiLoader=IGuiLoader)
def findActiveWindow(viewID, uiLoader=None):
    return uiLoader.windowsManager.getViewByLayoutID(viewID)


def registerViewsLoaders():
    Views.setLoaders({ViewID.INTRO: showIntro,
     ViewID.MAIN: showMain,
     ViewID.INFO: showInfo,
     ViewID.AUTOOPEN: showAutoOpen,
     ViewID.SHOP: openShop})


def unregisterViewsLoaders():
    Views.clear()
