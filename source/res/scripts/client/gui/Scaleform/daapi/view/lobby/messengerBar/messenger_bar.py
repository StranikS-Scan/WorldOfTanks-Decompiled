# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/messengerBar/messenger_bar.py
from gui import makeHtmlString
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.meta.MessengerBarMeta import MessengerBarMeta
from gui.Scaleform.framework import ViewTypes, g_entitiesFactories
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.Scaleform.genConsts.VEHICLE_COMPARE_CONSTANTS import VEHICLE_COMPARE_CONSTANTS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared import events
from gui.shared.event_bus import EVENT_BUS_SCOPE
from helpers import int2roman, dependency
from messenger.gui.Scaleform.view.lobby import MESSENGER_VIEW_ALIAS
from skeletons.gui.game_control import IVehicleComparisonBasket
from skeletons.gui.shared import IItemsCache
from soft_exception import SoftException

def _formatIcon(iconName, width=32, height=32):
    return makeHtmlString('html_templates:lobby/messengerBar', 'iconTemplate', {'iconName': iconName,
     'width': width,
     'height': height})


class _CompareBasketListener(object):
    itemsCache = dependency.descriptor(IItemsCache)
    comparisonBasket = dependency.descriptor(IVehicleComparisonBasket)

    def __init__(self, view):
        super(_CompareBasketListener, self).__init__()
        self.__currentCartPopover = None
        self.__view = view
        self.comparisonBasket.onChange += self.__onChanged
        self.comparisonBasket.onSwitchChange += self.__updateBtnVisibility
        self.__getContainerManager().onViewAddedToContainer += self.__onViewAddedToContainer
        self.__updateBtnVisibility()
        return

    def dispose(self):
        self.comparisonBasket.onChange -= self.__onChanged
        self.comparisonBasket.onSwitchChange -= self.__updateBtnVisibility
        self.__getContainerManager().onViewAddedToContainer -= self.__onViewAddedToContainer
        self.__view = None
        self.__clearCartPopover()
        return

    def __onChanged(self, changedData):
        if changedData.addedCDs:
            cMgr = self.__getContainerManager()
            if not cMgr.isViewAvailable(ViewTypes.LOBBY_SUB, {POP_UP_CRITERIA.VIEW_ALIAS: VIEW_ALIAS.VEHICLE_COMPARE}):
                vehCmpData = self.comparisonBasket.getVehicleAt(changedData.addedIDXs[-1])
                if not vehCmpData.isFromCache():
                    if self.comparisonBasket.getVehiclesCount() == 1:
                        self.__view.as_openVehicleCompareCartPopoverS(True)
                    else:
                        vehicle = self.itemsCache.items.getItemByCD(vehCmpData.getVehicleCD())
                        vehName = '  '.join([int2roman(vehicle.level), vehicle.shortUserName])
                        vehTypeIcon = RES_ICONS.maps_icons_vehicletypes_gold(vehicle.type + '.png')
                        self.__view.as_showAddVehicleCompareAnimS({'vehName': vehName,
                         'vehType': vehTypeIcon})
        if changedData.addedCDs or changedData.removedCDs:
            self.__updateBtnVisibility()

    def __updateBtnVisibility(self):
        isButtonVisible = self.__currentCartPopover is not None or self.comparisonBasket.getVehiclesCount() > 0
        self.__view.as_setVehicleCompareCartButtonVisibleS(isButtonVisible and self.comparisonBasket.isEnabled())
        return

    def __getContainerManager(self):
        return self.__view.app.containerManager

    def __onViewAddedToContainer(self, _, pyEntity):
        if pyEntity.viewType == ViewTypes.WINDOW and pyEntity.alias == VEHICLE_COMPARE_CONSTANTS.VEHICLE_COMPARE_CART_POPOVER:
            if self.__currentCartPopover is not None:
                raise SoftException('Attempt to initialize object 2nd time!')
            self.__currentCartPopover = pyEntity
            self.__currentCartPopover.onDispose += self.__onCartPopoverDisposed
        return

    def __onCartPopoverDisposed(self, _):
        self.__clearCartPopover()
        self.__updateBtnVisibility()

    def __clearCartPopover(self):
        if self.__currentCartPopover is not None:
            self.__currentCartPopover.onDispose -= self.__onCartPopoverDisposed
            self.__currentCartPopover = None
        return


class MessengerBar(MessengerBarMeta):

    def channelButtonClick(self):
        if not self.__manageWindow(MESSENGER_VIEW_ALIAS.CHANNEL_MANAGEMENT_WINDOW):
            self.fireEvent(events.LoadViewEvent(MESSENGER_VIEW_ALIAS.CHANNEL_MANAGEMENT_WINDOW), scope=EVENT_BUS_SCOPE.LOBBY)

    def destroy(self):
        if self.__compareBasketCtrl is not None:
            self.__compareBasketCtrl.dispose()
            self.__compareBasketCtrl = None
        super(MessengerBar, self).destroy()
        return

    def _populate(self):
        super(MessengerBar, self)._populate()
        self.as_setInitDataS({'channelsHtmlIcon': _formatIcon('iconChannels'),
         'contactsHtmlIcon': _formatIcon('iconContacts', width=16),
         'vehicleCompareHtmlIcon': _formatIcon('iconComparison'),
         'contactsTooltip': TOOLTIPS.LOBY_MESSENGER_CONTACTS_BUTTON,
         'vehicleCompareTooltip': TOOLTIPS.LOBY_MESSENGER_VEHICLE_COMPARE_BUTTON})
        self.__compareBasketCtrl = _CompareBasketListener(self)

    def __manageWindow(self, eventType):
        manager = self.app.containerManager
        window = manager.getView(ViewTypes.WINDOW, {POP_UP_CRITERIA.VIEW_ALIAS: g_entitiesFactories.getAliasByEvent(eventType)})
        result = window is not None
        if result:
            name = window.uniqueName
            isOnTop = manager.as_isOnTopS(ViewTypes.WINDOW, name)
            if not isOnTop:
                manager.as_bringToFrontS(ViewTypes.WINDOW, name)
            else:
                window.onWindowClose()
        return result
