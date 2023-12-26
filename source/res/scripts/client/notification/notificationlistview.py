# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/notification/NotificationListView.py
import typing
from debug_utils import LOG_ERROR
from frameworks.wulf import WindowLayer
from gui.Scaleform.daapi.view.meta.NotificationsListMeta import NotificationsListMeta
from gui.Scaleform.genConsts.NOTIFICATIONS_CONSTANTS import NOTIFICATIONS_CONSTANTS
from gui.Scaleform.locale.MESSENGER import MESSENGER
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.impl.gen import R
from gui.impl.lobby.gf_notifications import GFNotificationInject
from gui.shared import g_eventBus, EVENT_BUS_SCOPE, events
from gui.shared.formatters import icons
from gui.shared.notifications import NotificationGroup
from helpers import dependency
from helpers.i18n import makeString as _ms
from messenger.formatters import TimeFormatter
from notification import NotificationMVC
from notification.BaseNotificationView import BaseNotificationView
from notification.settings import LIST_SCROLL_STEP_FACTOR, NOTIFICATION_STATE
from skeletons.gui.game_control import IPromoController, IWinbackController
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache

class NotificationListView(NotificationsListMeta, BaseNotificationView):
    _lobbyContext = dependency.descriptor(ILobbyContext)
    __itemsCache = dependency.descriptor(IItemsCache)
    __winbackController = dependency.descriptor(IWinbackController)
    __promoController = dependency.descriptor(IPromoController)
    __guiLoader = dependency.descriptor(IGuiLoader)

    def __init__(self, _):
        super(NotificationListView, self).__init__()
        self.setModel(NotificationMVC.g_instance.getModel())
        self.__currentGroup = NotificationGroup.INFO
        self.__countersLabels = [''] * 3

    def registerGFNotification(self, component, alias, gfViewName, isPopUp, linkageData):
        from gui.Scaleform.framework import g_entitiesFactories
        idx = WindowLayer.UNDEFINED
        componentPy = g_entitiesFactories.initialize(GFNotificationInject(gfViewName, isPopUp, linkageData), component, idx)
        self.components[alias] = componentPy
        componentPy.setEnvironment(self.app)
        componentPy.create()
        g_eventBus.handleEvent(events.ComponentEvent(events.ComponentEvent.COMPONENT_REGISTERED, self, componentPy, alias), EVENT_BUS_SCOPE.GLOBAL)
        self._onRegisterFlashComponent(componentPy, alias)

    def onClickAction(self, typeID, entityID, action):
        NotificationMVC.g_instance.handleAction(typeID, self._getNotificationID(entityID), action)

    def onGroupChange(self, groupIdx):
        self.__currentGroup = NotificationGroup.ALL[groupIdx]
        self.__setNotificationList()
        self.__updateCounters()

    def getMessageActualTime(self, msTime):
        return TimeFormatter.getActualMsgTimeStr(msTime)

    def onCheckNewsClick(self):
        if not self.__promoController.isPromoOpen:
            self.__promoController.showPromo(self.__winbackController.winbackPromoURL)
        else:
            browserView = self.__guiLoader.windowsManager.getViewByLayoutID(R.views.lobby.common.BrowserView())
            if browserView is not None and browserView.browser is not None:
                browserView.browser.navigate(self.__winbackController.winbackPromoURL)
        self.destroy()
        return

    def _populate(self):
        super(NotificationListView, self)._populate()
        self._model.onNotificationReceived += self.__onNotificationReceived
        self._model.onNotificationUpdated += self.__onNotificationUpdated
        self._model.onNotificationRemoved += self.__onNotificationRemoved
        self.__winbackController.onConfigUpdated += self.__updateWinbackPromo
        self.__itemsCache.onSyncCompleted += self.__updateWinbackPromo
        self.__setInitData()
        self.__updateWinbackPromo()
        self.__setNotificationList()
        self.__updateCounters()

    def _dispose(self):
        if self._model.getDisplayState() == NOTIFICATION_STATE.LIST:
            self._model.setPopupsDisplayState()
        else:
            LOG_ERROR('Invalid state of the Notifications Model')
        self._model.onNotificationReceived -= self.__onNotificationReceived
        self._model.onNotificationUpdated -= self.__onNotificationUpdated
        self._model.onNotificationRemoved -= self.__onNotificationRemoved
        self.cleanUp()
        self._lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChange
        self.__winbackController.onConfigUpdated -= self.__updateWinbackPromo
        self.__itemsCache.onSyncCompleted -= self.__updateWinbackPromo
        super(NotificationListView, self)._dispose()

    def __setInitData(self):
        if self._model.getNotifiedMessagesCount(NotificationGroup.INVITE) > 0:
            self.__currentGroup = NotificationGroup.INVITE
        else:
            self.__currentGroup = NotificationGroup.INFO
        self._lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChange
        self.as_setInitDataS({'scrollStepFactor': LIST_SCROLL_STEP_FACTOR,
         'btnBarSelectedIdx': NotificationGroup.ALL.index(self.__currentGroup),
         'tabsData': {'tabs': [self.__makeTabItemVO(NOTIFICATIONS_CONSTANTS.TAB_INFO, icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_NOTIF_FILTERS_INFORMATION_16X16, 16, 16, -4, 0), TOOLTIPS.NOTIFICATIONSVIEW_TAB_INFO), self.__makeTabItemVO(NOTIFICATIONS_CONSTANTS.TAB_INVITES, icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_NOTIF_FILTERS_INVITATIONS_24X16, 24, 16, -5, 0), TOOLTIPS.NOTIFICATIONSVIEW_TAB_INVITES), self.__makeTabItemVO(NOTIFICATIONS_CONSTANTS.TAB_OFFERS, icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_ICON_BELL_24X16, 24, 16, -5, 0), TOOLTIPS.NOTIFICATIONSVIEW_TAB_OFFERS)]}})
        if self._lobbyContext.getServerSettings().getProgressiveRewardConfig().isEnabled:
            self.as_setProgressiveRewardEnabledS(True)

    def __updateWinbackPromo(self, *_):
        self.as_setIsNewsBlockEnabledS(self.__winbackController.isPromoEnabled())

    def __onServerSettingsChange(self, diff):
        if 'progressive_reward_config' in diff:
            self.as_setProgressiveRewardEnabledS(self._lobbyContext.getServerSettings().getProgressiveRewardConfig().isEnabled)

    def __updateCounters(self):

        def formatCount(count):
            return str(count) if count > 0 else ''

        counts = [ formatCount(self._model.getNotifiedMessagesCount(group)) for group in NotificationGroup.ALL ]
        if self.__countersLabels != counts:
            self.__countersLabels = counts
            self.as_updateCountersS(counts)

    def __setNotificationList(self):
        messages = self.__getMessagesList()
        self.as_setMessagesListS({'messages': messages,
         'emptyListText': self.__getEmptyListMsg(len(messages) > 0),
         'btnBarSelectedIdx': NotificationGroup.ALL.index(self.__currentGroup)})
        self._model.resetNotifiedMessagesCount(self.__currentGroup)

    def __getMessagesList(self):
        filtered = [ item for item in self._model.collection.getListIterator() if item.getGroup() == self.__currentGroup and not item.onlyPopUp() ]
        return [ self.__getListVO(item) for item in filtered ]

    def __getEmptyListMsg(self, hasMessages):
        return _ms(MESSENGER.LISTVIEW_EMPTYLIST_TEMPLATE, listType=_ms(MESSENGER.listview_emptylist(self.__currentGroup))) if not hasMessages else ''

    def __onNotificationReceived(self, notification):
        if notification.isAlert():
            NotificationMVC.g_instance.getAlertController().showAlertMessage(notification)
        if notification.getGroup() == self.__currentGroup:
            self.__setNotificationList()
        elif notification.getGroup() == NotificationGroup.INVITE:
            self.__currentGroup = NotificationGroup.INVITE
            self.__setNotificationList()
        elif notification.isNotify():
            self._model.incrementNotifiedMessagesCount(*notification.getCounterInfo())
        self.__updateCounters()

    def __onNotificationUpdated(self, notification, isStateChanged):
        if notification.getGroup() == self.__currentGroup:
            if notification.isOrderChanged():
                self.__setNotificationList()
            else:
                self.as_updateMessageS(self.__getListVO(notification))
        elif notification.getGroup() == NotificationGroup.INVITE:
            self.__currentGroup = NotificationGroup.INVITE
            self.__setNotificationList()
        elif isStateChanged and notification.isNotify():
            self._model.incrementNotifiedMessagesCount(*notification.getCounterInfo())
        self.__updateCounters()

    def __onNotificationRemoved(self, typeID, entityID, groupID, countOnce):
        if groupID == self.__currentGroup:
            self.__setNotificationList()
        else:
            self._model.decrementNotifiedMessagesCount(groupID, typeID, entityID, countOnce)
        self.__updateCounters()

    def __makeTabItemVO(self, tabId, label, tooltip):
        return {'id': tabId,
         'label': label,
         'tooltip': tooltip}

    def __getListVO(self, notificaton):
        flashId = self._getFlashID(notificaton.getCounterInfo())
        return notificaton.getListVO(flashId)
