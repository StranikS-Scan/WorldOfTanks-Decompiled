# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/techtree/techtree_page.py
from logging import getLogger
import datetime
import Keys
import nations
from account_helpers.settings_core.settings_constants import GuiSettingsBehavior
from account_helpers import AccountSettings
from account_helpers.AccountSettings import GUI_START_BEHAVIOR, TECHTREE_INTRO_BLUEPRINTS
from helpers import time_utils
from constants import IS_DEVELOPMENT
from blueprints.BlueprintTypes import BlueprintTypes
from gui import GUI_SETTINGS
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.go_back_helper import BackButtonContextKeys
from gui.Scaleform.daapi.view.lobby.store.browser.ingameshop_helpers import isIngameShopEnabled, getPremiumVehiclesUrl
from gui.Scaleform.daapi.view.lobby.techtree import dumpers
from gui.Scaleform.daapi.view.lobby.techtree.data import NationTreeData
from gui.Scaleform.daapi.view.lobby.techtree.settings import SelectedNation
from gui.Scaleform.daapi.view.lobby.techtree.sound_constants import Sounds
from gui.Scaleform.daapi.view.lobby.techtree.techtree_dp import g_techTreeDP
from gui.Scaleform.daapi.view.meta.TechTreeMeta import TechTreeMeta
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.genConsts.STORE_CONSTANTS import STORE_CONSTANTS
from gui.Scaleform.genConsts.STORE_TYPES import STORE_TYPES
from gui.impl import backport
from gui.impl.gen.resources import R
from gui.ingame_shop import canBuyGoldForVehicleThroughWeb
from gui.shared import event_dispatcher as shared_events
from gui.shared import events, EVENT_BUS_SCOPE
from gui.shared.formatters import text_styles
from gui.shared.gui_items.items_actions import factory as ItemsActionsFactory
from gui.shared.utils.vehicle_collector_helper import hasCollectibleVehicles
from gui.shared.utils.requesters.blueprints_requester import getNationalFragmentCD
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from messenger.gui.Scaleform.view.lobby import MESSENGER_VIEW_ALIAS
from gui.Scaleform.genConsts.CONTACTS_ALIASES import CONTACTS_ALIASES
from gui.Scaleform.genConsts.SESSION_STATS_CONSTANTS import SESSION_STATS_CONSTANTS
_logger = getLogger(__name__)
_VEHICLE_URL_FILTER_PARAM = 1

class TechTree(TechTreeMeta):
    __settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, ctx=None):
        super(TechTree, self).__init__(NationTreeData(dumpers.NationObjDumper()))
        self._resolveLoadCtx(ctx=ctx)
        self.__blueprintMode = ctx.get(BackButtonContextKeys.BLUEPRINT_MODE, False)
        self.__intelligenceAmount = 0
        self.__nationalFragmentsData = {}

    def __del__(self):
        _logger.debug('TechTree deleted')

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
        self.__updateBlueprintBalance()
        self.__setVehicleCollectorState()
        self._data.load(nationIdx)
        self.__playBlueprintPlusSound()
        return self._data.dump()

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
        loadEvent = events.LoadViewEvent(VIEW_ALIAS.LOBBY_RESEARCH, ctx={BackButtonContextKeys.ROOT_CD: vehCD,
         BackButtonContextKeys.EXIT: self.__exitEvent()})
        self.fireEvent(loadEvent, scope=EVENT_BUS_SCOPE.LOBBY)

    def onCloseTechTree(self):
        if self._canBeClosed:
            self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_HANGAR), scope=EVENT_BUS_SCOPE.LOBBY)

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
        if isIngameShopEnabled():
            params = {'nation': nationName,
             'level': level,
             'vehicleFilterByUrl': _VEHICLE_URL_FILTER_PARAM}
            shared_events.showWebShop(url=getPremiumVehiclesUrl(), params=params)
        else:
            shared_events.showOldShop(ctx={'tabId': STORE_TYPES.SHOP,
             'component': STORE_CONSTANTS.VEHICLE})

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

    def invalidateVehicleCollectorState(self):
        self.__setVehicleCollectorState()

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
        self._populateAfter()
        return

    def _populateAfter(self):
        blueprints = {}
        defaults = AccountSettings.getFilterDefault(GUI_START_BEHAVIOR)
        settings = self.__settingsCore.serverSettings.getSection(GUI_START_BEHAVIOR, defaults)
        if self.__needShowTechTreeIntro(settings):
            if settings[GuiSettingsBehavior.TECHTREE_INTRO_BLUEPRINTS_RECEIVED]:
                blueprints = AccountSettings.getSettings(TECHTREE_INTRO_BLUEPRINTS)
            shared_events.showTechTreeIntro(parent=self.getParentWindow(), blueprints=blueprints)

    def _dispose(self):
        if IS_DEVELOPMENT:
            from gui import InputHandler
            InputHandler.g_instance.onKeyUp -= self.__handleReloadData
        self.__removeListeners()
        self.__stopTopOfTheTreeSounds()
        super(TechTree, self)._dispose()

    def _blueprintExitEvent(self, vehicleCD):
        return self.__exitEvent()

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

    def __exitEvent(self):
        return events.LoadViewEvent(VIEW_ALIAS.LOBBY_TECHTREE, ctx={BackButtonContextKeys.NATION: SelectedNation.getName(),
         BackButtonContextKeys.BLUEPRINT_MODE: self.__blueprintMode})

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
        self.__intelligenceAmount = bpRequester.getIntelligenceData()
        self.__nationalFragmentsData = bpRequester.getAllNationalFragmentsData()
        selectedNation = SelectedNation.getIndex()
        nationalAmount = self.__nationalFragmentsData.get(selectedNation, 0)
        balanceStr = text_styles.main(backport.text(R.strings.blueprints.blueprintScreen.resourcesOnStorage()))
        intFragmentVO = {'iconPath': backport.image(R.images.gui.maps.icons.blueprints.fragment.small.intelligence()),
         'title': backport.getIntegralFormat(self.__intelligenceAmount),
         'fragmentCD': BlueprintTypes.INTELLIGENCE_DATA}
        natFragmentVO = {'iconPath': backport.image(R.images.gui.maps.icons.blueprints.fragment.small.dyn(SelectedNation.getName())()),
         'title': backport.getIntegralFormat(nationalAmount),
         'fragmentCD': getNationalFragmentCD(selectedNation)}
        balanceVO = {'balanceStr': balanceStr,
         'internationalItemVO': intFragmentVO,
         'nationalItemVO': natFragmentVO}
        return balanceVO

    def __updateBlueprintBalance(self):
        self.as_setBlueprintBalanceS(self.__formatBlueprintBalance())

    def __needShowTechTreeIntro(self, settings):
        isShowed = settings[GuiSettingsBehavior.TECHTREE_INTRO_SHOWED]
        startTime = datetime.date(GUI_SETTINGS.techTreeIntroStartDate.get('year'), GUI_SETTINGS.techTreeIntroStartDate.get('month'), GUI_SETTINGS.techTreeIntroStartDate.get('day'))
        endTime = startTime + datetime.timedelta(seconds=time_utils.ONE_YEAR)
        registrationTime = self._itemsCache.items.getAccountDossier().getGlobalStats().getCreationTime()
        isOverdue = time_utils.getCurrentLocalServerTimestamp() >= time_utils.getTimestampFromLocal(endTime.timetuple())
        isNewPlayer = registrationTime >= time_utils.getTimestampFromLocal(startTime.timetuple())
        return not (isShowed or isOverdue or isNewPlayer)

    def __setVehicleCollectorState(self):
        isVehicleCollectorEnabled = self._lobbyContext.getServerSettings().isCollectorVehicleEnabled()
        self.as_setVehicleCollectorStateS(isVehicleCollectorEnabled and hasCollectibleVehicles(SelectedNation.getIndex()))

    def __onSettingsChanged(self):
        self.as_setAvailableNationsS(g_techTreeDP.getNationsMenuDataProvider())

    def __stopTopOfTheTreeSounds(self):
        self.soundManager.playInstantSound(Sounds.TOP_OF_THE_TREE_ANIMATION_STOP_ANIMATION)
