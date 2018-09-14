# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/Hangar.py
import BigWorld
import SoundGroups
from CurrentVehicle import g_currentVehicle
from PlayerEvents import g_playerEvents
from debug_utils import LOG_DEBUG
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.meta.HangarMeta import HangarMeta
from gui.Scaleform.framework import ViewTypes
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.CHRISTMAS import CHRISTMAS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.christmas.christmas_controller import g_christmasCtrl
from gui.christmas.christmas_items import NY_OBJECT_TYPE
from gui.prb_control.ctrl_events import g_prbCtrlEvents
from gui.prb_control.entities.listener import IGlobalListener
from gui.shared import g_itemsCache, events, EVENT_BUS_SCOPE
from gui.shared.ItemsCache import CACHE_SYNC_REASON
from gui.shared.events import LobbySimpleEvent
from gui.shared.formatters import text_styles
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.utils.HangarSpace import g_hangarSpace
from gui.shared.utils.MethodsRules import MethodsRules
from gui.shared.utils.functions import makeTooltip
from helpers import dependency
from helpers import int2roman
from helpers.i18n import makeString as _ms
from skeletons.gui.game_control import IFalloutController
from skeletons.gui.game_control import IIGRController
from christmas_shared import EVENT_STATE
CHRISTMAS_3D_ITEMS = ('h07_newyear_tree', 'h07_newyear_box')

class Hangar(LobbySubView, HangarMeta, IGlobalListener, MethodsRules):
    __background_alpha__ = 0.0
    falloutCtrl = dependency.descriptor(IFalloutController)
    igrCtrl = dependency.descriptor(IIGRController)

    def __init__(self, _=None):
        LobbySubView.__init__(self, 0)
        self.__isCursorOver3dScene = False
        self.__selected3DEntity = None
        self.__currentCarouselAlias = None
        self.__isChristmas3DObjectsSubscribed = False
        return

    def onEscape(self):
        dialogsContainer = self.app.containerManager.getContainer(ViewTypes.TOP_WINDOW)
        if not dialogsContainer.getView(criteria={POP_UP_CRITERIA.VIEW_ALIAS: VIEW_ALIAS.LOBBY_MENU}):
            self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_MENU), scope=EVENT_BUS_SCOPE.LOBBY)
        self.__checkSelectedEntity()

    def showHelpLayout(self):
        containerManager = self.app.containerManager
        dialogsContainer = containerManager.getContainer(ViewTypes.TOP_WINDOW)
        windowsContainer = containerManager.getContainer(ViewTypes.WINDOW)
        browserWindowContainer = containerManager.getContainer(ViewTypes.BROWSER)
        if not dialogsContainer.getViewCount() and not windowsContainer.getViewCount() and not browserWindowContainer.getViewCount():
            containerManager.onViewAddedToContainer += self.__onViewAddedToContainer
            self.fireEvent(LobbySimpleEvent(LobbySimpleEvent.SHOW_HELPLAYOUT), scope=EVENT_BUS_SCOPE.LOBBY)
            self.as_showHelpLayoutS()

    def closeHelpLayout(self):
        self.app.containerManager.onViewAddedToContainer -= self.__onViewAddedToContainer
        self.fireEvent(LobbySimpleEvent(LobbySimpleEvent.CLOSE_HELPLAYOUT), scope=EVENT_BUS_SCOPE.LOBBY)
        self.as_closeHelpLayoutS()

    @property
    def researchPanel(self):
        return self.getComponent(HANGAR_ALIASES.RESEARCH_PANEL)

    @property
    def headerComponent(self):
        return self.getComponent(HANGAR_ALIASES.HEADER)

    def onCacheResync(self, reason, diff):
        if reason == CACHE_SYNC_REASON.SHOP_RESYNC:
            self.__updateAll()
            return
        else:
            if reason in (CACHE_SYNC_REASON.STATS_RESYNC, CACHE_SYNC_REASON.INVENTORY_RESYNC, CACHE_SYNC_REASON.CLIENT_UPDATE):
                self.__updateCarouselParams()
                self.__updateCarouselEnabled()
            if diff is not None and GUI_ITEM_TYPE.VEHICLE in diff:
                self.__updateCarouselVehicles(diff.get(GUI_ITEM_TYPE.VEHICLE))
                self.__updateAmmoPanel()
            return

    def onPlayerStateChanged(self, entity, roster, accountInfo):
        if accountInfo.isCurrentPlayer():
            self.__updateState()
            self.__updateAmmoPanel()

    def onUnitPlayerStateChanged(self, pInfo):
        if pInfo.isCurrentPlayer():
            self.__onEntityChanged()

    def onPrbEntitySwitched(self):
        self.__onEntityChanged()

    def onEnqueued(self, queueType, *args):
        self.__onEntityChanged()

    def onDequeued(self, queueType, *args):
        self.__onEntityChanged()

    def onFittingUpdate(self, *args):
        self.__updateCarouselParams()

    def onMoneyUpdate(self, *args):
        self.__updateAmmoPanel()
        self.__updateCarouselParams()

    @property
    def tankCarousel(self):
        return self.getComponent(self.__currentCarouselAlias)

    @property
    def ammoPanel(self):
        return self.getComponent(HANGAR_ALIASES.AMMUNITION_PANEL)

    @property
    def paramsPanel(self):
        return self.getComponent(HANGAR_ALIASES.VEHICLE_PARAMETERS)

    @property
    def crewPanel(self):
        return self.getComponent(HANGAR_ALIASES.CREW)

    @MethodsRules.delayable()
    def _populate(self):
        LobbySubView._populate(self)
        g_playerEvents.onVehicleBecomeElite += self.__onVehicleBecomeElite
        g_playerEvents.onBattleResultsReceived += self.onFittingUpdate
        g_currentVehicle.onChanged += self.__onCurrentVehicleChanged
        self.igrCtrl.onIgrTypeChanged += self.__onIgrTypeChanged
        self.falloutCtrl.onSettingsChanged += self.__onFalloutSettingsChanged
        g_itemsCache.onSyncCompleted += self.onCacheResync
        g_hangarSpace.onObjectSelected += self.__on3DObjectSelected
        g_hangarSpace.onObjectUnselected += self.__on3DObjectUnSelected
        g_hangarSpace.onObjectClicked += self.__on3DObjectClicked
        g_prbCtrlEvents.onVehicleClientStateChanged += self.__onVehicleClientStateChanged
        g_clientUpdateManager.addCallbacks({'stats.credits': self.onMoneyUpdate,
         'stats.gold': self.onMoneyUpdate,
         'stats.vehicleSellsLeft': self.onFittingUpdate,
         'stats.slots': self.onFittingUpdate,
         'goodies': self.onFittingUpdate})
        self.startGlobalListening()
        g_christmasCtrl.onEventStarted += self.__setChristmasEntryData
        g_christmasCtrl.onEventStopped += self.__setChristmasEntryData
        g_christmasCtrl.onToysCacheChanged += self.__setChristmasEntryData
        g_christmasCtrl.switchToHangar()
        self.__updateAll()
        self.addListener(LobbySimpleEvent.HIDE_HANGAR, self._onCustomizationShow)
        self.addListener(LobbySimpleEvent.NOTIFY_CURSOR_OVER_3DSCENE, self.__onNotifyCursorOver3dScene)
        self.addListener(LobbySimpleEvent.WAITING_SHOWN, self.__onWaitingShown, EVENT_BUS_SCOPE.LOBBY)
        self.__setChristmasEntryData()
        self.__selected3DEntity = g_hangarSpace.selectedEntity
        if self.__selected3DEntity is not None:
            self.__highlight3DEntityAndShowTT(self.__selected3DEntity)
        return

    @MethodsRules.delayable('_populate')
    def _dispose(self):
        """
        Dispose method should never be called before populate finish. So, we're delaying
        its invoke til populate load is finished.
        """
        self.removeListener(LobbySimpleEvent.HIDE_HANGAR, self._onCustomizationShow)
        self.removeListener(LobbySimpleEvent.NOTIFY_CURSOR_OVER_3DSCENE, self.__onNotifyCursorOver3dScene)
        self.removeListener(LobbySimpleEvent.WAITING_SHOWN, self.__onWaitingShown, EVENT_BUS_SCOPE.LOBBY)
        g_christmasCtrl.onEventStarted -= self.__setChristmasEntryData
        g_christmasCtrl.onEventStopped -= self.__setChristmasEntryData
        g_christmasCtrl.onToysCacheChanged -= self.__setChristmasEntryData
        self.__removeCristmas3DObectsClickListeners()
        g_itemsCache.onSyncCompleted -= self.onCacheResync
        g_clientUpdateManager.removeObjectCallbacks(self)
        g_playerEvents.onVehicleBecomeElite -= self.__onVehicleBecomeElite
        g_playerEvents.onBattleResultsReceived -= self.onFittingUpdate
        g_currentVehicle.onChanged -= self.__onCurrentVehicleChanged
        self.igrCtrl.onIgrTypeChanged -= self.__onIgrTypeChanged
        self.falloutCtrl.onSettingsChanged -= self.__onFalloutSettingsChanged
        g_hangarSpace.onObjectSelected -= self.__on3DObjectSelected
        g_hangarSpace.onObjectUnselected -= self.__on3DObjectUnSelected
        g_hangarSpace.onObjectClicked -= self.__on3DObjectClicked
        g_prbCtrlEvents.onVehicleClientStateChanged -= self.__onVehicleClientStateChanged
        if self.__selected3DEntity is not None:
            BigWorld.wgDelEdgeDetectEntity(self.__selected3DEntity)
            self.__selected3DEntity = None
        self.closeHelpLayout()
        self.stopGlobalListening()
        LobbySubView._dispose(self)
        return

    def _onCustomizationShow(self, event):
        self.as_setVisibleS(not event.ctx)

    def __addCristmas3DObectsClickListeners(self):
        """
        adds on click callbacks on christmas 3d objects
        """
        if not self.__isChristmas3DObjectsSubscribed:
            g_christmasCtrl.setOnclickCallback((self.__onTreeClickedCallback, self.__onGiftClickedCallback, self.__onTankClickedCallback))
            self.__isChristmas3DObjectsSubscribed = True

    def __removeCristmas3DObectsClickListeners(self):
        """
        removes on click callbacks on christmas 3d objects
        """
        if self.__isChristmas3DObjectsSubscribed:
            g_christmasCtrl.clearOnclickCallback()
            self.__isChristmas3DObjectsSubscribed = False

    def __setChristmasEntryData(self, *args):
        label = ''
        newToysCountStr = ''
        tooltip = TOOLTIPS_CONSTANTS.XMAS_TREE
        isEnabled = g_christmasCtrl.isEventInProgress()
        if isEnabled:
            self.__addCristmas3DObectsClickListeners()
            ratingInfo = g_christmasCtrl.getRatingInfo()
            xmasTreeLvl = ratingInfo['level']
            if ratingInfo['rating'] == 0:
                label = text_styles.middleTitle(_ms(CHRISTMAS.HANGARBTN_LABEL_DECORATE))
            else:
                label = text_styles.middleTitle(_ms(CHRISTMAS.HANGARBTN_LABEL_TREELVL, lvl=int2roman(xmasTreeLvl)))
            newToysCount = g_christmasCtrl.newToysCount()
            if newToysCount > 0:
                newToysCountStr = text_styles.counterLabelText(str(newToysCount))
        else:
            self.__removeCristmas3DObectsClickListeners()
        data = {'isEnabled': isEnabled,
         'label': label,
         'newToysCount': newToysCountStr,
         'tooltip': tooltip}
        self.tankCarousel.setChristmasBtnData(data)

    def __onViewAddedToContainer(self, _, pyEntity):
        self.closeHelpLayout()

    def __switchCarousels(self):
        prevCarouselAlias = self.__currentCarouselAlias
        if self.falloutCtrl.isSelected():
            linkage = HANGAR_ALIASES.FALLOUT_TANK_CAROUSEL_UI
            newCarouselAlias = HANGAR_ALIASES.FALLOUT_TANK_CAROUSEL
        else:
            linkage = HANGAR_ALIASES.TANK_CAROUSEL_UI
            newCarouselAlias = HANGAR_ALIASES.TANK_CAROUSEL
        if prevCarouselAlias != newCarouselAlias:
            self.as_setCarouselS(linkage, newCarouselAlias)
            self.__currentCarouselAlias = newCarouselAlias

    def __updateAmmoPanel(self):
        if self.ammoPanel:
            self.ammoPanel.update()

    def __updateParams(self):
        if self.paramsPanel:
            self.paramsPanel.update()

    def __updateCarouselVehicles(self, vehicles=None):
        if self.tankCarousel is not None:
            self.tankCarousel.updateVehicles(vehicles)
        return

    def __updateCarouselParams(self):
        if self.tankCarousel is not None:
            self.tankCarousel.updateParams()
        return

    def __updateResearchPanel(self):
        if self.researchPanel is not None:
            self.researchPanel.onCurrentVehicleChanged()
        return

    def __updateHeader(self):
        if self.headerComponent is not None:
            self.headerComponent.update()
        return

    def __updateCrew(self):
        if self.crewPanel is not None:
            self.crewPanel.updateTankmen()
        return

    def __highlight3DEntityAndShowTT(self, entity):
        itemId = entity.selectionId
        if itemId not in CHRISTMAS_3D_ITEMS or g_christmasCtrl.isEventInProgress():
            entity.highlight(True)
        if len(itemId) > 0:
            if itemId in CHRISTMAS_3D_ITEMS:
                eventState = g_christmasCtrl.getGlobalState()
                if eventState == EVENT_STATE.IN_PROGRESS:
                    if itemId == 'h07_newyear_tree':
                        self.as_show3DSceneTooltipS(TOOLTIPS_CONSTANTS.XMAS_TREE, None)
                    else:
                        self.as_show3DSceneTooltipS(TOOLTIPS_CONSTANTS.ENVIRONMENT, [itemId])
                elif eventState == EVENT_STATE.SUSPENDED:
                    self.as_show3DSceneTooltipS(TOOLTIPS_CONSTANTS.ENVIRONMENT, ['christmas/eventSuspended'])
                elif eventState == EVENT_STATE.FINISHED:
                    self.as_show3DSceneTooltipS(TOOLTIPS_CONSTANTS.ENVIRONMENT, ['christmas/eventFinished'])
            else:
                self.as_show3DSceneTooltipS(TOOLTIPS_CONSTANTS.ENVIRONMENT, [itemId])
        return

    def __fade3DEntityAndHideTT(self, entity):
        entity.highlight(False)
        self.as_hide3DSceneTooltipS()

    def __onWaitingShown(self, event):
        self.closeHelpLayout()

    def __onNotifyCursorOver3dScene(self, event):
        self.__isCursorOver3dScene = event.ctx.get('isOver3dScene', False)
        if self.__selected3DEntity is not None:
            if self.__isCursorOver3dScene:
                self.__highlight3DEntityAndShowTT(self.__selected3DEntity)
            else:
                self.__fade3DEntityAndHideTT(self.__selected3DEntity)
        return

    def __on3DObjectSelected(self, entity):
        self.__selected3DEntity = entity
        if self.__isCursorOver3dScene:
            self.__highlight3DEntityAndShowTT(entity)
            if entity.mouseOverSoundName:
                SoundGroups.g_instance.playSound3D(entity.model.root, entity.mouseOverSoundName)

    def __on3DObjectUnSelected(self, entity):
        self.__selected3DEntity = None
        self.__fade3DEntityAndHideTT(entity)
        return

    def __on3DObjectClicked(self):
        if self.__isCursorOver3dScene:
            if self.__selected3DEntity is not None:
                self.__selected3DEntity.onClicked()
        return

    def __onTreeClickedCallback(self):
        self.__navigateToView({'objectType': NY_OBJECT_TYPE.TREE})

    def __onTankClickedCallback(self):
        self.__navigateToView({'objectType': NY_OBJECT_TYPE.TANK})

    def __navigateToView(self, ctx):
        if g_christmasCtrl.getClosedChestsCount():
            self.__showChestView()
        else:
            self.__showChristmasView(ctx)

    def __onGiftClickedCallback(self):
        self.__showChestView()

    def __checkSelectedEntity(self):
        selectedEntity = g_hangarSpace.selectedEntity
        if selectedEntity is not None:
            self.__on3DObjectSelected(selectedEntity)
        return

    def __showChristmasView(self, ctx=None):
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_CHRISTMAS, ctx=ctx), EVENT_BUS_SCOPE.LOBBY)

    def __showChestView(self):
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.CHRISTMAS_CHESTS), EVENT_BUS_SCOPE.LOBBY)

    def __onVehicleBecomeElite(self, vehTypeCompDescr):
        self.__updateCarouselVehicles([vehTypeCompDescr])

    def __updateAll(self):
        Waiting.show('updateVehicle')
        self.__switchCarousels()
        self.__updateState()
        self.__updateAmmoPanel()
        self.__updateCarouselVehicles()
        self.__updateCarouselParams()
        self.__updateParams()
        self.__updateResearchPanel()
        self.__updateHeader()
        self.__updateCrew()
        Waiting.hide('updateVehicle')

    def __onCurrentVehicleChanged(self):
        Waiting.show('updateVehicle')
        self.__updateState()
        self.__updateAmmoPanel()
        self.__updateParams()
        self.__updateResearchPanel()
        self.__updateHeader()
        self.__updateCrew()
        self.__updateCarouselParams()
        Waiting.hide('updateVehicle')

    def __onIgrTypeChanged(self, *args):
        self.__updateResearchPanel()
        self.__updateHeader()
        self.__updateParams()

    def __onFalloutSettingsChanged(self):
        self.__switchCarousels()
        self.__updateCarouselVehicles()

    def __updateState(self):
        state = g_currentVehicle.getViewState()
        self.as_setCrewEnabledS(state.isCrewOpsEnabled())
        self.__updateCarouselEnabled()
        if state.isOnlyForEventBattles():
            customizationTooltip = makeTooltip(_ms(TOOLTIPS.HANGAR_TUNING_DISABLEDFOREVENTVEHICLE_HEADER), _ms(TOOLTIPS.HANGAR_TUNING_DISABLEDFOREVENTVEHICLE_BODY))
        else:
            customizationTooltip = makeTooltip(_ms(TOOLTIPS.HANGAR_TUNING_HEADER), _ms(TOOLTIPS.HANGAR_TUNING_BODY))
        self.as_setupAmmunitionPanelS(state.isMaintenanceEnabled(), makeTooltip(_ms(TOOLTIPS.HANGAR_MAINTENANCE_HEADER), _ms(TOOLTIPS.HANGAR_MAINTENANCE_BODY)), state.isCustomizationEnabled(), customizationTooltip)
        self.as_setControlsVisibleS(state.isUIShown())

    def __updateCarouselEnabled(self):
        state = g_currentVehicle.getViewState()
        self.as_setCarouselEnabledS(not state.isLocked())

    def __onEntityChanged(self):
        self.__updateState()
        self.__updateAmmoPanel()

    def __onVehicleClientStateChanged(self, vehicles):
        self.__updateCarouselVehicles(vehicles)
        self.__updateAmmoPanel()
