# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/techtree/techtree_page.py
from logging import getLogger
import Keys
import nations
from blueprints.BlueprintTypes import BlueprintTypes
from constants import IS_DEVELOPMENT
from gui.Scaleform.genConsts.NODE_STATE_FLAGS import NODE_STATE_FLAGS
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.go_back_helper import BackButtonContextKeys
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import getPremiumVehiclesUrl
from gui.Scaleform.daapi.view.lobby.techtree import dumpers
from gui.Scaleform.daapi.view.lobby.techtree.data import NationTreeData
from gui.Scaleform.daapi.view.lobby.techtree.settings import SelectedNation
from gui.Scaleform.daapi.view.lobby.techtree.sound_constants import Sounds
from gui.Scaleform.daapi.view.lobby.techtree.techtree_dp import g_techTreeDP
from gui.Scaleform.daapi.view.meta.TechTreeMeta import TechTreeMeta
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.genConsts.CONTACTS_ALIASES import CONTACTS_ALIASES
from gui.Scaleform.genConsts.SESSION_STATS_CONSTANTS import SESSION_STATS_CONSTANTS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.impl import backport
from gui.impl.gen.resources import R
from gui.limited_ui.lui_rules_storage import LuiRules
from gui.shared import event_dispatcher as shared_events
from gui.shared import events, EVENT_BUS_SCOPE
from gui.shared.formatters import text_styles
from gui.shared.gui_items.items_actions import factory as ItemsActionsFactory
from gui.shared.utils.requesters.blueprints_requester import getNationalFragmentCD
from gui.shared.utils.vehicle_collector_helper import hasCollectibleVehicles
from gui.shop import canBuyGoldForVehicleThroughWeb
from helpers import dependency
from messenger.gui.Scaleform.view.lobby import MESSENGER_VIEW_ALIAS
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import ILimitedUIController
_logger = getLogger(__name__)
_VEHICLE_URL_FILTER_PARAM = 1

class TechTree(TechTreeMeta):
    __settingsCore = dependency.descriptor(ISettingsCore)
    __limitedUIController = dependency.descriptor(ILimitedUIController)

    def __init__(self, ctx=None):
        super(TechTree, self).__init__(NationTreeData(dumpers.NationObjDumper()))
        self._resolveLoadCtx(ctx=ctx)
        self.__blueprintMode = ctx.get(BackButtonContextKeys.BLUEPRINT_MODE, False)
        self.__intelligenceAmount = 0
        self.__nationalFragmentsData = {}

    def __del__(self):
        _logger.debug('TechTree deleted')

    def goToBlueprintView(self, vehicleCD):
        self.__stopTopOfTheTreeSounds()
        super(TechTree, self).goToBlueprintView(vehicleCD)

    def goToNationChangeView(self, vehicleCD):
        self.__stopTopOfTheTreeSounds()
        super(TechTree, self).goToNationChangeView(vehicleCD)

    def goToVehicleCollection(self, nationName):
        self.__stopTopOfTheTreeSounds()
        super(TechTree, self).goToVehicleCollection(nationName)

    def redraw(self):
        self.as_refreshNationTreeDataS(SelectedNation.getName())

    def requestNationTreeData(self):
        self.as_setAvailableNationsS(g_techTreeDP.getNationsMenuDataProvider())
        self.as_setSelectedNationS(SelectedNation.getName())
        return True

    def getNationTreeData(self, nationName):
        if nationName not in nations.INDICES:
            _logger.error('Nation with name %s not found', nationName)
            return {}
        self.__stopTopOfTheTreeSounds()
        nationIdx = nations.INDICES[nationName]
        SelectedNation.select(nationIdx)
        if not self.__limitedUIController.isRuleCompleted(LuiRules.TECH_TREE_EVENTS):
            g_techTreeDP.techTreeEventsListener.setNationViewed(nationIdx)
        self.__updateBlueprintBalance()
        self.__setVehicleCollectorState()
        self._data.load(nationIdx)
        self.__playBlueprintPlusSound()
        return self._data.dump()

    def clearSelectedNation(self):
        SelectedNation.clear()

    def getPremiumPanelLabels(self):
        vehicleLabel = backport.text(R.strings.menu.techtree.premiumPanel.btnLabel(), count=text_styles.gold(backport.text(R.strings.menu.techtree.premiumPanel.btnLabel.count())))
        labels = {'panelTitle': backport.text(R.strings.menu.techtree.premiumPanel.title()),
         'vehicleLabel': vehicleLabel.split(backport.text(R.strings.menu.techtree.premiumPanel.btnLabel.count()))}
        return labels

    def request4Unlock(self, itemCD):
        itemCD = int(itemCD)
        node = self._data.getNodeByItemCD(itemCD)
        unlockProps = node.getUnlockProps() if node is not None else None
        if unlockProps is not None:
            ItemsActionsFactory.doAction(ItemsActionsFactory.UNLOCK_ITEM, itemCD, unlockProps)
        return

    def request4Buy(self, itemCD):
        itemCD = int(itemCD)
        vehicle = self._itemsCache.items.getItemByCD(itemCD)
        if canBuyGoldForVehicleThroughWeb(vehicle):
            shared_events.showVehicleBuyDialog(vehicle)
        else:
            ItemsActionsFactory.doAction(ItemsActionsFactory.BUY_VEHICLE, itemCD)

    def request4VehCompare(self, vehCD):
        self._cmpBasket.addVehicle(int(vehCD))

    def request4Restore(self, itemCD):
        ItemsActionsFactory.doAction(ItemsActionsFactory.BUY_VEHICLE, int(itemCD))

    def goToNextVehicle(self, vehCD):
        loadEvent = events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_RESEARCH), ctx={BackButtonContextKeys.ROOT_CD: vehCD,
         BackButtonContextKeys.EXIT: self._createExitEvent()})
        self.soundManager.playInstantSound(Sounds.RESET)
        self.__stopTopOfTheTreeSounds()
        self.fireEvent(loadEvent, scope=EVENT_BUS_SCOPE.LOBBY)

    def onCloseTechTree(self):
        if self._canBeClosed:
            self.__stopTopOfTheTreeSounds()
            shared_events.showHangar()

    def onBlueprintModeSwitch(self, enabled):
        if self.__blueprintMode == enabled:
            return
        self.__blueprintMode = enabled
        if enabled:
            self.soundManager.playInstantSound(Sounds.BLUEPRINT_VIEW_ON_SOUND_ID)
            self.__playBlueprintPlusSound()
        else:
            self.soundManager.playInstantSound(Sounds.BLUEPRINT_VIEW_OFF_SOUND_ID)

    def onGoToPremiumShop(self, nationName, level):
        self.__stopTopOfTheTreeSounds()
        params = {'nation': nationName,
         'level': level,
         'vehicleFilterByUrl': _VEHICLE_URL_FILTER_PARAM}
        shared_events.showShop(url=getPremiumVehiclesUrl(), params=params)

    def onPlayHintAnimation(self, isEnabled=True):
        if isEnabled:
            g_techTreeDP.techTreeEventsListener.setNationViewed(SelectedNation.getIndex())
            self.soundManager.playInstantSound(Sounds.TOP_OF_THE_TREE_ANIMATION_ON_SOUND_ID)
        else:
            self.soundManager.playInstantSound(Sounds.TOP_OF_THE_TREE_ANIMATION_OFF_SOUND_ID)

    def invalidateBlueprintMode(self, isEnabled):
        if isEnabled:
            self.as_setBlueprintsSwitchButtonStateS(enabled=True, selected=self.__blueprintMode, tooltip=TOOLTIPS.TECHTREEPAGE_BLUEPRINTSSWITCHTOOLTIP, visible=True)
        else:
            self.__blueprintMode = False
            self.__disableBlueprintsSwitchButton(isEnabled)
            self.__stopTopOfTheTreeSounds()
            shared_events.showHangar()
        self.redraw()

    def invalidateVehLocks(self, locks):
        if self._data.invalidateLocks(locks):
            self.redraw()

    def invalidateVTypeXP(self, xps):
        super(TechTree, self).invalidateVTypeXP(xps)
        result = self._data.invalidateXpCosts()
        if result:
            self.as_setUnlockPropsS(result)

    def invalidateWalletStatus(self, status):
        self.invalidateFreeXP()
        self.invalidateGold()

    def invalidateRent(self, vehicles):
        pass

    def invalidateRestore(self, vehicles):
        if self._data.invalidateRestore(vehicles):
            self.redraw()

    def invalidateBlueprints(self, blueprints):
        if not blueprints:
            return
        if self.__isBlueprintsDeleted(blueprints):
            result = self._data.invalidateBlueprints(blueprints)
            if result:
                self.as_setNodesStatesS(NODE_STATE_FLAGS.BLUEPRINT, result)
        else:
            self.redraw()

    def invalidateVehicleCollectorState(self):
        self.__setVehicleCollectorState()

    def _updatePrevUnlockedItems(self, prevUnlocked):
        self.as_setNodesStatesS(NODE_STATE_FLAGS.LAST_2_BUY, prevUnlocked)

    def _resolveLoadCtx(self, ctx=None):
        nation = ctx[BackButtonContextKeys.NATION] if ctx is not None and BackButtonContextKeys.NATION in ctx else None
        if nation is not None and nation in nations.INDICES:
            nationIdx = nations.INDICES[nation]
            SelectedNation.select(nationIdx)
        else:
            SelectedNation.byDefault()
        return

    def _populate(self):
        super(TechTree, self)._populate()
        if IS_DEVELOPMENT:
            from gui import InputHandler
            InputHandler.g_instance.onKeyUp += self.__handleReloadData
        eventsListener = g_techTreeDP.techTreeEventsListener
        if eventsListener is not None:
            eventsListener.onSettingsChanged += self.__onSettingsChanged
        if self.__blueprintMode:
            self.as_setBlueprintModeS(True)
        isBlueprintsEnabled = self._lobbyContext.getServerSettings().blueprintsConfig.isBlueprintsAvailable()
        self.__disableBlueprintsSwitchButton(isBlueprintsEnabled)
        self.__setVehicleCollectorState()
        self.__addListeners()
        return

    def _dispose(self):
        if IS_DEVELOPMENT:
            from gui import InputHandler
            InputHandler.g_instance.onKeyUp -= self.__handleReloadData
        self.__removeListeners()
        super(TechTree, self)._dispose()

    def _createExitEvent(self):
        return events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_TECHTREE), ctx={BackButtonContextKeys.NATION: SelectedNation.getName(),
         BackButtonContextKeys.BLUEPRINT_MODE: self.__blueprintMode})

    def __addListeners(self):
        self.addListener(MESSENGER_VIEW_ALIAS.CHANNEL_MANAGEMENT_WINDOW, self.__onClosePremiumPanel, scope=EVENT_BUS_SCOPE.LOBBY)
        self.addListener(CONTACTS_ALIASES.CONTACTS_POPOVER, self.__onClosePremiumPanel, scope=EVENT_BUS_SCOPE.LOBBY)
        self.addListener(SESSION_STATS_CONSTANTS.SESSION_STATS_POPOVER, self.__onClosePremiumPanel, scope=EVENT_BUS_SCOPE.LOBBY)
        self.addListener(VIEW_ALIAS.NOTIFICATIONS_LIST, self.__onClosePremiumPanel, scope=EVENT_BUS_SCOPE.LOBBY)
        self.addListener(events.ReferralProgramEvent.SHOW_REFERRAL_PROGRAM_WINDOW, self.__onClosePremiumPanel, scope=EVENT_BUS_SCOPE.LOBBY)
        self.addListener(events.ChannelCarouselEvent.OPEN_BUTTON_CLICK, self.__onClosePremiumPanel, scope=EVENT_BUS_SCOPE.LOBBY)

    def __removeListeners(self):
        self.removeListener(MESSENGER_VIEW_ALIAS.CHANNEL_MANAGEMENT_WINDOW, self.__onClosePremiumPanel, scope=EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(CONTACTS_ALIASES.CONTACTS_POPOVER, self.__onClosePremiumPanel, scope=EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(SESSION_STATS_CONSTANTS.SESSION_STATS_POPOVER, self.__onClosePremiumPanel, scope=EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(VIEW_ALIAS.NOTIFICATIONS_LIST, self.__onClosePremiumPanel, scope=EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(events.ReferralProgramEvent.SHOW_REFERRAL_PROGRAM_WINDOW, self.__onClosePremiumPanel, scope=EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(events.ChannelCarouselEvent.OPEN_BUTTON_CLICK, self.__onClosePremiumPanel, scope=EVENT_BUS_SCOPE.LOBBY)
        eventsListener = g_techTreeDP.techTreeEventsListener
        if eventsListener is not None:
            eventsListener.onSettingsChanged -= self.__onSettingsChanged
        return

    def __onClosePremiumPanel(self, _=None):
        self.as_closePremiumPanelS()

    def __handleReloadData(self, event):
        if event.key is Keys.KEY_R:
            g_techTreeDP.load(isReload=True)
            self.redraw()

    def __hasConversionPlusesOnTree(self):
        for node in self._data.getNodes():
            bpfProps = node.getBpfProps()
            if bpfProps and bpfProps.canConvert:
                return True

        return False

    def __playBlueprintPlusSound(self):
        if self.__blueprintMode and self.__hasConversionPlusesOnTree():
            self.soundManager.playInstantSound(Sounds.BLUEPRINT_VIEW_PLUS_SOUND_ID)

    def __disableBlueprintsSwitchButton(self, isEnabled):
        if not isEnabled:
            self.as_setBlueprintsSwitchButtonStateS(enabled=False, selected=self.__blueprintMode, tooltip=TOOLTIPS.TECHTREEPAGE_BLUEPRINTSSWITCHTOOLTIPDISABLED, visible=True)

    def __formatBlueprintBalance(self):
        bpRequester = self._itemsCache.items.blueprints
        self.__intelligenceAmount = bpRequester.getIntelligenceCount()
        self.__nationalFragmentsData = bpRequester.getAllNationalFragmentsData()
        selectedNation = SelectedNation.getIndex()
        nationalAmount = self.__nationalFragmentsData.get(selectedNation, 0)
        balanceStr = text_styles.main(backport.text(R.strings.blueprints.blueprintScreen.resourcesOnStorage()))
        intFragmentVO = {'iconPath': backport.image(R.images.gui.maps.icons.blueprints.fragment.special.intelligence()),
         'title': backport.getIntegralFormat(self.__intelligenceAmount),
         'fragmentCD': BlueprintTypes.INTELLIGENCE_DATA}
        natFragmentVO = {'iconPath': backport.image(R.images.gui.maps.icons.blueprints.fragment.special.dyn(SelectedNation.getName())()),
         'title': backport.getIntegralFormat(nationalAmount),
         'fragmentCD': getNationalFragmentCD(selectedNation)}
        balanceVO = {'balanceStr': balanceStr,
         'internationalItemVO': intFragmentVO,
         'nationalItemVO': natFragmentVO}
        return balanceVO

    def __updateBlueprintBalance(self):
        self.as_setBlueprintBalanceS(self.__formatBlueprintBalance())

    def __setVehicleCollectorState(self):
        isVehicleCollectorEnabled = self._lobbyContext.getServerSettings().isCollectorVehicleEnabled()
        self.as_setVehicleCollectorStateS(isVehicleCollectorEnabled and hasCollectibleVehicles(SelectedNation.getIndex()))

    def __onSettingsChanged(self):
        self.as_setAvailableNationsS(g_techTreeDP.getNationsMenuDataProvider())

    def __stopTopOfTheTreeSounds(self):
        self.soundManager.playInstantSound(Sounds.TOP_OF_THE_TREE_ANIMATION_STOP_ANIMATION)

    @staticmethod
    def __isBlueprintsDeleted(blueprints):
        return all((value is None for value in blueprints.values()))
