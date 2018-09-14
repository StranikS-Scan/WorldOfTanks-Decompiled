# Embedded file name: scripts/client/messenger/gui/Scaleform/data/ChannelsCarouselHandler.py
from debug_utils import LOG_ERROR
from gui.Scaleform.daapi.view.meta.ChannelCarouselMeta import ChannelCarouselMeta
from gui.Scaleform.framework import ViewTypes
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView
from gui.Scaleform.framework.managers.containers import ExternalCriteria
from gui.app_loader.decorators import sf_lobby
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import ChannelManagementEvent, ChannelCarouselEvent, PreBattleChannelEvent
from gui.shared.events import FocusEvent, ComponentEvent
from messenger.ext import channel_num_gen
from messenger.gui import events_dispatcher
from messenger.gui.Scaleform.data.ChannelsDataProvider import ChannelsDataProvider

class ChannelFindCriteria(ExternalCriteria):

    def __init__(self, criteria = None):
        super(ChannelFindCriteria, self).__init__(criteria)

    def find(self, name, obj):
        return getattr(obj, '_clientID', 0) == self._criteria


class ChannelsCarouselHandler(object):

    def __init__(self, guiEntry):
        super(ChannelsCarouselHandler, self).__init__()
        self.__guiEntry = guiEntry
        self.__channelsDP = None
        self.__preBattleChannelsDP = None
        self.__handlers = {}
        self.__showByReqs = {}
        return

    @sf_lobby
    def app(self):
        return None

    def init(self):
        self.__channelsDP = ChannelsDataProvider()
        self.__preBattleChannelsDP = ChannelsDataProvider()
        add = g_eventBus.addListener
        add(ChannelManagementEvent.REQUEST_TO_ADD, self.__handleRequestToAdd, scope=EVENT_BUS_SCOPE.LOBBY)
        add(PreBattleChannelEvent.REQUEST_TO_ADD_PRE_BATTLE_CHANNEL, self.__handleRequestToAddPrebattle, scope=EVENT_BUS_SCOPE.LOBBY)
        add(PreBattleChannelEvent.REQUEST_TO_REMOVE_PRE_BATTLE_CHANNEL, self.__handleRequestToRemovePreBattle, scope=EVENT_BUS_SCOPE.LOBBY)
        add(ChannelManagementEvent.REQUEST_TO_REMOVE, self.__handleRequestToRemove, scope=EVENT_BUS_SCOPE.LOBBY)
        add(ChannelManagementEvent.REQUEST_TO_CHANGE, self.__handleRequestToChange, scope=EVENT_BUS_SCOPE.LOBBY)
        add(ChannelManagementEvent.REQUEST_TO_SHOW, self.__handleRequestToShow, scope=EVENT_BUS_SCOPE.LOBBY)
        add(FocusEvent.COMPONENT_FOCUSED, self.__handleComponentFocusIn)
        add(ComponentEvent.COMPONENT_REGISTERED, self.__handleComponentRegistered)
        add(ComponentEvent.COMPONENT_UNREGISTERED, self.__handleComponentUnregistered)

    def __handleComponentRegistered(self, _):
        self.__checkOpenedWindows()

    def __handleComponentUnregistered(self, _):
        self.__checkOpenedWindows()

    def __checkOpenedWindows(self):
        self.___checkOpenedWindows(self.__channelsDP)
        self.___checkOpenedWindows(self.__preBattleChannelsDP)

    def ___checkOpenedWindows(self, targetDataProvider):
        listItems = targetDataProvider.collection
        for item in listItems:
            clientID = item['clientID']
            if not clientID:
                return
            if clientID not in self.__handlers:
                return
            criteria, openHandler, viewType = self.__handlers[clientID]
            app = self.app
            if not app:
                return
            containerMgr = app.containerManager
            if containerMgr is not None:
                container = containerMgr.getContainer(viewType)
                if container is not None:
                    window = container.getView(criteria)
                    targetDataProvider.setItemField(clientID, 'isWindowOpened', window is not None)

        return

    def clear(self):
        self.__guiEntry = None
        self.__handlers.clear()
        if self.__channelsDP is not None:
            self.__channelsDP.clear()
            self.__channelsDP.finiGUI()
            self.__channelsDP = None
        if self.__preBattleChannelsDP is not None:
            self.__preBattleChannelsDP.clear()
            self.__preBattleChannelsDP.finiGUI()
            self.__preBattleChannelsDP = None
        remove = g_eventBus.removeListener
        remove(ChannelManagementEvent.REQUEST_TO_ADD, self.__handleRequestToAdd, scope=EVENT_BUS_SCOPE.LOBBY)
        remove(PreBattleChannelEvent.REQUEST_TO_ADD_PRE_BATTLE_CHANNEL, self.__handleRequestToAddPrebattle, scope=EVENT_BUS_SCOPE.LOBBY)
        remove(PreBattleChannelEvent.REQUEST_TO_REMOVE_PRE_BATTLE_CHANNEL, self.__handleRequestToRemovePreBattle, scope=EVENT_BUS_SCOPE.LOBBY)
        remove(ChannelManagementEvent.REQUEST_TO_REMOVE, self.__handleRequestToRemove, scope=EVENT_BUS_SCOPE.LOBBY)
        remove(ChannelManagementEvent.REQUEST_TO_CHANGE, self.__handleRequestToChange, scope=EVENT_BUS_SCOPE.LOBBY)
        remove(ChannelManagementEvent.REQUEST_TO_SHOW, self.__handleRequestToShow, scope=EVENT_BUS_SCOPE.LOBBY)
        remove(FocusEvent.COMPONENT_FOCUSED, self.__handleComponentFocusIn)
        remove(ComponentEvent.COMPONENT_REGISTERED, self.__handleComponentRegistered)
        remove(ComponentEvent.COMPONENT_UNREGISTERED, self.__handleComponentUnregistered)
        return

    def start(self):
        add = g_eventBus.addListener
        add(ChannelCarouselEvent.CAROUSEL_INITED, self.__handleCarouselInited, scope=EVENT_BUS_SCOPE.LOBBY)
        add(ChannelCarouselEvent.CAROUSEL_DESTROYED, self.__handleCarouselDestroyed, scope=EVENT_BUS_SCOPE.LOBBY)
        add(ChannelCarouselEvent.OPEN_BUTTON_CLICK, self.__handleOpenButtonClick, scope=EVENT_BUS_SCOPE.LOBBY)
        add(ChannelCarouselEvent.MINIMIZE_ALL_CHANNELS, self.__handlerMinimizeAll, scope=EVENT_BUS_SCOPE.LOBBY)
        add(ChannelCarouselEvent.CLOSE_ALL_EXCEPT_CURRENT, self.__handlerCloseAllExceptCurrent, scope=EVENT_BUS_SCOPE.LOBBY)
        add(ChannelCarouselEvent.CLOSE_BUTTON_CLICK, self.__handleCloseButtonClick, scope=EVENT_BUS_SCOPE.LOBBY)

    def stop(self):
        remove = g_eventBus.removeListener
        remove(ChannelCarouselEvent.CAROUSEL_INITED, self.__handleCarouselInited, scope=EVENT_BUS_SCOPE.LOBBY)
        remove(ChannelCarouselEvent.CAROUSEL_DESTROYED, self.__handleCarouselDestroyed, scope=EVENT_BUS_SCOPE.LOBBY)
        remove(ChannelCarouselEvent.OPEN_BUTTON_CLICK, self.__handleOpenButtonClick, scope=EVENT_BUS_SCOPE.LOBBY)
        remove(ChannelCarouselEvent.MINIMIZE_ALL_CHANNELS, self.__handlerMinimizeAll, scope=EVENT_BUS_SCOPE.LOBBY)
        remove(ChannelCarouselEvent.CLOSE_ALL_EXCEPT_CURRENT, self.__handlerCloseAllExceptCurrent, scope=EVENT_BUS_SCOPE.LOBBY)
        remove(ChannelCarouselEvent.CLOSE_BUTTON_CLICK, self.__handleCloseButtonClick, scope=EVENT_BUS_SCOPE.LOBBY)
        self.__channelsDP.finiGUI()
        self.__preBattleChannelsDP.finiGUI()
        self.__showByReqs.clear()

    def addChannel(self, channel, lazy = False, isNotified = False):
        clientID = channel.getClientID()
        isSystem = channel.isSystem()
        if lazy:
            order = channel_num_gen.getOrder4LazyChannel(channel.getName())
            openHandler = lambda : events_dispatcher.showLazyChannelWindow(clientID)
        else:
            order = channel_num_gen.genOrder4Channel(channel)
            openHandler = lambda : events_dispatcher.showLobbyChannelWindow(clientID)
        self.__handlers[clientID] = (ChannelFindCriteria(clientID), openHandler, ViewTypes.WINDOW)
        self.__channelsDP.addItem(clientID, {'label': channel.getFullName(),
         'canClose': not isSystem,
         'isNotified': isNotified,
         'icon': None,
         'order': order,
         'isInProgress': False})
        return

    def removeChannel(self, channel):
        clientID = channel.getClientID()
        if clientID in self.__handlers:
            criteria, openHandler, viewType = self.__handlers.pop(clientID)
            window = None
            app = self.app
            if app is not None and app.containerManager is not None:
                window = app.containerManager.getView(viewType, criteria)
            if window is not None:
                window.destroy()
        self.__channelsDP.removeItem(clientID)
        return

    def notifyChannel(self, channel, isNotified = True):
        clientID = channel.getClientID()
        self.__setItemField(clientID, 'isNotified', isNotified)

    def __setItemField(self, clientID, key, value):
        result = self.__preBattleChannelsDP.setItemField(clientID, key, value)
        if not result:
            result = self.__channelsDP.setItemField(clientID, key, value)
        return result

    def updateChannel(self, channel):
        self.__setItemField(channel.getClientID(), 'label', channel.getFullName())

    def removeChannels(self):
        if self.__channelsDP is not None:
            self.__channelsDP.clear()
        if self.__preBattleChannelsDP is not None:
            self.__preBattleChannelsDP.clear()
        self.__handlers.clear()
        self.__showByReqs.clear()
        return

    def __handleCarouselInited(self, event):
        carousel = event.target
        if isinstance(carousel, ChannelCarouselMeta):
            self.__channelsDP.initGUI(carousel.as_getDataProviderS())
            self.__preBattleChannelsDP.initGUI(carousel.as_getBattlesDataProviderS())
        else:
            LOG_ERROR('Channel carousel must be extends ChannelCarouselMeta', carousel)

    def __handleCarouselDestroyed(self, _):
        self.__channelsDP.finiGUI()
        self.__preBattleChannelsDP.finiGUI()

    def __handleRequestToAddPrebattle(self, event):
        self.__adjustAndAddChannel(event, self.__preBattleChannelsDP)

    def __handleRequestToAdd(self, event):
        self.__adjustAndAddChannel(event, self.__channelsDP)

    def __adjustAndAddChannel(self, event, targetList):
        ctx = event.ctx
        label = ctx.get('label')
        if label is None:
            LOG_ERROR('Label is not defined', event.ctx)
            return
        else:
            criteria = ctx.get('criteria')
            if criteria is None:
                LOG_ERROR('Criteria is not defined', event.ctx)
                return
            openHandler = ctx.get('openHandler')
            if openHandler is None:
                LOG_ERROR('Open handler is not defined', event.ctx)
                return
            viewType = ctx.get('viewType')
            if viewType is None:
                LOG_ERROR('View type is not defined', event.ctx)
                return
            clientID = event.clientID
            if clientID not in self.__handlers:
                self.__handlers[clientID] = (criteria, openHandler, viewType)
                targetList.addItem(clientID, ctx)
            return

    def __handleRequestToRemovePreBattle(self, event):
        self.__removeChannelFromList(event, self.__preBattleChannelsDP)

    def __handleRequestToRemove(self, event):
        self.__removeChannelFromList(event, self.__channelsDP)

    def __removeChannelFromList(self, event, targetList):
        clientID = event.clientID
        if clientID in self.__handlers:
            criteria, openHandler, viewType = self.__handlers.pop(clientID)
            window = None
            if self.app is not None:
                window = self.app.containerManager.getView(viewType, criteria)
            if window is not None:
                window.destroy()
            targetList.removeItem(clientID)
            self.__showByReqs.pop(clientID, None)
        return

    def __handleRequestToChange(self, event):
        ctx = event.ctx
        key = ctx.get('key')
        if key is None:
            LOG_ERROR('Key of item field is not defined', ctx)
            return
        else:
            value = ctx.get('value')
            if value is None:
                LOG_ERROR('Value of item field is not defined', ctx)
                return
            clientID = event.clientID
            if 'isShowByReq' in ctx and ctx['isShowByReq'] is True:
                self.__showByReqs[clientID] = (key, value)
                isShow = ctx.get('showIfClosed', False)
                if isShow:
                    if clientID not in self.__handlers:
                        return
                    criteria, _, viewType = self.__handlers[clientID]
                    window = self.app.containerManager.getView(viewType, criteria)
                    if window is None:
                        if not self.__setItemField(clientID, key, value):
                            self.__showByReqs.pop(clientID)
            else:
                self.__setItemField(clientID, key, value)
                self.__showByReqs.pop(clientID, None)
            return

    def __handleComponentFocusIn(self, event):
        clientID = event.ctx.get('clientID', None)
        self.__checkFocusedWindow(clientID, self.__channelsDP)
        self.__checkFocusedWindow(clientID, self.__preBattleChannelsDP)
        return

    def __checkFocusedWindow(self, targetClientID, targetDataProvider):
        listItems = targetDataProvider.collection
        for item in listItems:
            clientID = item['clientID']
            targetDataProvider.setItemField(clientID, 'isWindowFocused', clientID == targetClientID)

    def __handleRequestToShow(self, event):
        ctx = event.ctx
        show = ctx.get('show')
        if show is None:
            LOG_ERROR('Flag "show" is not defined', ctx)
            return
        else:
            clientID = event.clientID
            if not clientID:
                return
            if clientID in self.__showByReqs:
                key, value = self.__showByReqs[clientID]
                if show:
                    if not self.__setItemField(clientID, key, value):
                        self.__showByReqs.pop(clientID)
                elif not self.__channelsDP.clearItemField(clientID, key):
                    if not self.__preBattleChannelsDP.clearItemField(clientID, key):
                        self.__showByReqs.pop(clientID)
            return

    def __handleOpenButtonClick(self, event):
        clientID = event.clientID
        if not clientID:
            return
        elif clientID not in self.__handlers:
            return
        else:
            criteria, openHandler, viewType = self.__handlers[clientID]
            viewContainer = self.app.containerManager
            if viewType == ViewTypes.WINDOW:
                window = viewContainer.getView(viewType, criteria)
                if window is not None:
                    wName = window.uniqueName
                    isOnTop = viewContainer.as_isOnTopS(ViewTypes.WINDOW, wName)
                    if not isOnTop:
                        viewContainer.as_bringToFrontS(ViewTypes.WINDOW, wName)
                    else:
                        window.onWindowMinimize()
                    return
            elif viewType == ViewTypes.LOBBY_SUB:
                view = viewContainer.getView(viewType, criteria)
                if hasattr(view, 'onWindowMinimize') and callable(getattr(view, 'onWindowMinimize')):
                    view.onWindowMinimize()
                    return
            fields = {'isNotified': False,
             'isInProgress': False}
            if not self.__channelsDP.setItemFields(clientID, fields):
                self.__preBattleChannelsDP.setItemFields(clientID, fields)
            openHandler()
            return

    def __handlerMinimizeAll(self, _):
        for criteria, _, viewType in self.__handlers.itervalues():
            viewContainer = self.app.containerManager
            if isinstance(criteria, ChannelFindCriteria):
                window = viewContainer.getView(viewType, criteria)
                if window is not None:
                    window.onWindowMinimize()

        return

    def __handlerCloseAllExceptCurrent(self, event):
        self.__closeExcept(event.clientID)

    def __closeExcept(self, clientID):
        for key in self.__handlers.keys():
            if key != clientID:
                cntrler = self.__guiEntry.channelsCtrl.getController(key)
                if cntrler is not None:
                    channel = cntrler.getChannel()
                    if not channel.isSystem():
                        self.__closeChannel(key)

        return

    def __handleCloseButtonClick(self, event):
        clientID = event.clientID
        channel = self.__guiEntry.channelsCtrl.getController(clientID).getChannel()
        if not channel.isSystem():
            self.__closeChannel(clientID)

    def __closeChannel(self, clientID):
        if not clientID:
            return
        elif clientID not in self.__handlers:
            return
        else:
            self.__showByReqs.pop(clientID, None)
            viewContainer = self.app.containerManager
            criteria, openHandler, viewType = self.__handlers[clientID]
            if viewType == ViewTypes.WINDOW:
                window = viewContainer.getView(viewType, criteria)
                if window is not None:
                    window.onWindowClose()
                    return
            if self.__guiEntry:
                controller = self.__guiEntry.channelsCtrl.getController(clientID)
                if controller:
                    controller.exit()
            return
