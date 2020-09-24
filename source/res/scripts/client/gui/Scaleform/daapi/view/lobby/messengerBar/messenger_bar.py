# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/messengerBar/messenger_bar.py
from account_helpers.settings_core.settings_constants import SESSION_STATS
from adisp import process
from constants import PREBATTLE_TYPE
from frameworks.wulf import WindowLayer
from gui import makeHtmlString
from gui import SystemMessages
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.referral_program.referral_program_helpers import isReferralProgramEnabled
from gui.Scaleform.daapi.view.lobby.session_stats.session_stats_settings_controller import SessionStatsSettingsController
from gui.Scaleform.daapi.view.meta.MessengerBarMeta import MessengerBarMeta
from gui.Scaleform.framework import g_entitiesFactories
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.genConsts.VEHICLE_COMPARE_CONSTANTS import VEHICLE_COMPARE_CONSTANTS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.impl import backport
from gui.impl.gen import R
from gui.prb_control import prbDispatcherProperty
from gui.prb_control.entities.listener import IGlobalListener
from gui.shared import events
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.utils.functions import makeTooltip
from gui.shared.gui_items.processors.session_stats import ResetSessionStatsProcessor
from helpers import int2roman, dependency
from messenger.gui.Scaleform.view.lobby import MESSENGER_VIEW_ALIAS
from skeletons.gui.game_control import IVehicleComparisonBasket, IReferralProgramController
from skeletons.gui.shared import IItemsCache
from soft_exception import SoftException
from skeletons.gui.lobby_context import ILobbyContext

def _formatIcon(iconName, width=32, height=32, path='html_templates:lobby/messengerBar'):
    return makeHtmlString(path, 'iconTemplate', {'iconName': iconName,
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
            if not cMgr.isViewAvailable(WindowLayer.SUB_VIEW, {POP_UP_CRITERIA.VIEW_ALIAS: VIEW_ALIAS.VEHICLE_COMPARE}):
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
        if pyEntity.layer == WindowLayer.WINDOW and pyEntity.alias == VEHICLE_COMPARE_CONSTANTS.VEHICLE_COMPARE_CART_POPOVER:
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


class MessengerBar(MessengerBarMeta, IGlobalListener):
    _referralCtrl = dependency.descriptor(IReferralProgramController)
    _lobbyContext = dependency.descriptor(ILobbyContext)

    @prbDispatcherProperty
    def prbDispatcher(self):
        return None

    def channelButtonClick(self):
        if not self.__manageWindow(MESSENGER_VIEW_ALIAS.CHANNEL_MANAGEMENT_WINDOW):
            self.fireEvent(events.LoadViewEvent(SFViewLoadParams(MESSENGER_VIEW_ALIAS.CHANNEL_MANAGEMENT_WINDOW)), scope=EVENT_BUS_SCOPE.LOBBY)

    def referralButtonClick(self):
        self.fireEvent(events.ReferralProgramEvent(events.ReferralProgramEvent.SHOW_REFERRAL_PROGRAM_WINDOW), scope=EVENT_BUS_SCOPE.LOBBY)

    def sessionStatsButtonClick(self):
        if self.__sessionStatsBtnOnlyOnceHintShow:
            self.__onSessionStatsBtnOnlyOnceHintHidden(True)

    def destroy(self):
        if self.__compareBasketCtrl is not None:
            self.__compareBasketCtrl.dispose()
            self.__compareBasketCtrl = None
        super(MessengerBar, self).destroy()
        return

    def onPrbEntitySwitched(self):
        self.__updateSessionStatsBtn()

    def _populate(self):
        super(MessengerBar, self)._populate()
        self.__compareBasketCtrl = _CompareBasketListener(self)
        self._referralCtrl.onReferralProgramEnabled += self.__onReferralProgramEnabled
        self._referralCtrl.onReferralProgramDisabled += self.__onReferralProgramDisabled
        self._referralCtrl.onReferralProgramUpdated += self.__onReferralProgramUpdated
        self._lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingChanged
        self.addListener(events.FightButtonEvent.FIGHT_BUTTON_UPDATE, self.__handleFightButtonUpdated, scope=EVENT_BUS_SCOPE.LOBBY)
        self.startGlobalListening()
        self.as_setInitDataS({'channelsHtmlIcon': _formatIcon('iconChannels'),
         'isReferralEnabled': isReferralProgramEnabled(),
         'referralCounter': self._referralCtrl.getBubbleCount(),
         'isReferralFirstIndication': self._referralCtrl.isFirstIndication(),
         'referralHtmlIcon': _formatIcon('iconReferral', width=38, height=29, path='html_templates:lobby/referralButton'),
         'referralTooltip': TOOLTIPS.LOBY_MESSENGER_REFERRAL_BUTTON,
         'contactsHtmlIcon': _formatIcon('iconContacts', width=16),
         'vehicleCompareHtmlIcon': _formatIcon('iconComparison'),
         'contactsTooltip': TOOLTIPS.LOBY_MESSENGER_CONTACTS_BUTTON,
         'vehicleCompareTooltip': TOOLTIPS.LOBY_MESSENGER_VEHICLE_COMPARE_BUTTON,
         'sessionStatsHtmlIcon': _formatIcon('iconSessionStats')})
        sessionStatsSettings = SessionStatsSettingsController().getSettings()
        self.__sessionStatsBtnOnlyOnceHintShow = not sessionStatsSettings[SESSION_STATS.ONLY_ONCE_HINT_SHOWN_FIELD]
        self.__updateSessionStatsBtn()

    def _dispose(self):
        self.removeListener(events.FightButtonEvent.FIGHT_BUTTON_UPDATE, self.__handleFightButtonUpdated, scope=EVENT_BUS_SCOPE.LOBBY)
        self._lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingChanged
        self._referralCtrl.onReferralProgramUpdated -= self.__onReferralProgramUpdated
        self._referralCtrl.onReferralProgramDisabled -= self.__onReferralProgramDisabled
        self._referralCtrl.onReferralProgramEnabled -= self.__onReferralProgramEnabled
        self.stopGlobalListening()
        super(MessengerBar, self)._dispose()

    def __onReferralProgramEnabled(self):
        self.as_setReferralProgramButtonVisibleS(True)

    def __onReferralProgramDisabled(self):
        self.as_setReferralProgramButtonVisibleS(False)

    def __onReferralProgramUpdated(self, *_):
        self.as_setReferralBtnCounterS(self._referralCtrl.getBubbleCount())

    def __handleFightButtonUpdated(self, event):
        state = self.prbDispatcher.getFunctionalState()
        self.as_setReferralButtonEnabledS(not state.isNavigationDisabled())

    def __manageWindow(self, eventType):
        manager = self.app.containerManager
        window = manager.getView(WindowLayer.WINDOW, {POP_UP_CRITERIA.VIEW_ALIAS: g_entitiesFactories.getAliasByEvent(eventType)})
        result = window is not None
        if result:
            name = window.uniqueName
            isOnTop = manager.as_isOnTopS(WindowLayer.WINDOW, name)
            if not isOnTop:
                manager.as_bringToFrontS(WindowLayer.WINDOW, name)
            else:
                window.onWindowClose()
        return result

    def __onServerSettingChanged(self, diff):
        if 'sessionStats' in diff or ('sessionStats', '_r') in diff:
            self.__updateSessionStatsBtn()

    def __updateSessionStatsHint(self, visible):
        self.as_setSessionStatsButtonSettingsUpdateS(visible, '!')

    @process
    def __updateSessionStatsBtn(self):
        dispatcher = self.prbDispatcher
        if dispatcher is not None:
            isInSupportedMode = dispatcher.getFunctionalState().entityTypeID in (PREBATTLE_TYPE.SQUAD,)
        else:
            isInSupportedMode = False
        isSessionStatsEnabled = self._lobbyContext.getServerSettings().isSessionStatsEnabled()
        tooltip = self.__getSessionStatsBtnTooltip(isInSupportedMode and isSessionStatsEnabled)
        if not isSessionStatsEnabled:
            result = yield ResetSessionStatsProcessor().request()
            if result and result.userMsg:
                SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
        self.as_setSessionStatsButtonVisibleS(isSessionStatsEnabled)
        self.as_setSessionStatsButtonEnableS(isSessionStatsEnabled and isInSupportedMode, tooltip)
        self.__updateSessionStatsHint(self.__sessionStatsBtnOnlyOnceHintShow and isSessionStatsEnabled and isInSupportedMode)
        return

    @staticmethod
    def __getSessionStatsBtnTooltip(btnEnabled):
        return makeTooltip(backport.text(R.strings.session_stats.tooltip.mainBtn.header()), backport.text(R.strings.session_stats.tooltip.mainBtn.body.enabled())) if btnEnabled else makeTooltip(backport.text(R.strings.session_stats.tooltip.mainBtn.header()), backport.text(R.strings.session_stats.tooltip.mainBtn.body.disabled()))

    def __onSessionStatsBtnOnlyOnceHintHidden(self, record=False):
        if record:
            sessionStatsSettings = SessionStatsSettingsController().getSettings()
            sessionStatsSettings[SESSION_STATS.ONLY_ONCE_HINT_SHOWN_FIELD] = True
            SessionStatsSettingsController().setSettings(sessionStatsSettings)
        self.__sessionStatsBtnOnlyOnceHintShow = False
        self.__updateSessionStatsHint(self.__sessionStatsBtnOnlyOnceHintShow)
