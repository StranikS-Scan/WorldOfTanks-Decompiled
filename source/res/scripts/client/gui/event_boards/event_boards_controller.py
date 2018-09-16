# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/event_boards/event_boards_controller.py
from account_helpers import AccountSettings
from account_helpers.AccountSettings import ELEN_NOTIFICATIONS
from adisp import process, async
from client_request_lib.exceptions import ResponseCodes
from gui import SystemMessages
from gui.Scaleform.genConsts.MISSIONS_CONSTANTS import MISSIONS_CONSTANTS
from gui.Scaleform.locale.EVENT_BOARDS import EVENT_BOARDS
from gui.SystemMessages import SM_TYPE
from gui.event_boards.event_boards_items import EventBoardsSettings, HangarFlagData, LeaderBoard, MyInfoInLeaderBoard, SET_DATA_STATUS_CODE, EVENT_STATE, PLAYER_STATE_REASON as _psr
from gui.event_boards.event_boards_items import EventSettings
from gui.event_boards.listener import IEventBoardsListener
from gui.shared.utils.requesters.abstract import Response
from gui.wgcg import IWebController
from gui.wgcg.elen.contexts import EventBoardsGetEventDataCtx, EventBoardsGetPlayerDataCtx, EventBoardsJoinEventCtx, EventBoardsLeaveEventCtx, EventBoardsGetMyEventTopCtx, EventBoardsGetMyLeaderboardPositionCtx, EventBoardsGetLeaderboardCtx, EventBoardsGetHangarFlagCtx, EventBoardsGetFootballEventDataCtx
from gui.wgcg.settings import WebRequestDataType as _crdt
from helpers import dependency
from helpers.i18n import makeString as _ms
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.event_boards_controllers import IEventBoardController
from skeletons.gui.shared import IItemsCache
SUCCESS_STATUSES = (200, 201, 304)

class EventBoardsController(IEventBoardController, IEventBoardsListener):
    clanController = dependency.descriptor(IWebController)
    connectionMgr = dependency.descriptor(IConnectionManager)
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        super(EventBoardsController, self).__init__()
        self.__isLoggedIn = False
        self.__eventBoardsSettings = EventBoardsSettings()
        self.__hangarFlagData = HangarFlagData()
        self.__footballEventSettings = EventBoardsSettings()

    def fini(self):
        self.__eventBoardsSettings.fini()
        self.__footballEventSettings.fini()

    def getPlayerEventsData(self):
        return self.__eventBoardsSettings.getPlayerEventsData() if self.__eventBoardsSettings is not None else None

    def getEventsSettingsData(self):
        return self.__eventBoardsSettings.getEventsSettings() if self.__eventBoardsSettings is not None else None

    def hasEvents(self):
        return self.__eventBoardsSettings.hasEvents() if self.__eventBoardsSettings is not None else False

    def getMyEventsTopData(self):
        return self.__eventBoardsSettings.getMyEventsTop() if self.__eventBoardsSettings is not None else None

    def getHangarFlagData(self):
        return self.__hangarFlagData

    def getFootballSettingsData(self):
        return self.__footballEventSettings.getEventsSettings() if self.__footballEventSettings is not None else None

    def hasFootballEvents(self):
        return self.__footballEventSettings.hasEvents() if self.__footballEventSettings is not None else False

    def updateHangarFlag(self):
        self._invokeListeners('onUpdateHangarFlag')

    def cleanEventsData(self):
        self.__isLoggedIn = False
        if self.__eventBoardsSettings is not None:
            self.__eventBoardsSettings.cleanEventsData()
        if self.__hangarFlagData is not None:
            self.__hangarFlagData.cleanEventsData()
        return

    def cleanFootballEventsData(self):
        if self.__footballEventSettings is not None:
            self.__footballEventSettings.cleanEventsData()
        return

    @async
    @process
    def sendRequest(self, ctx, callback):
        response = yield self.clanController.sendRequest(ctx)
        self.__handleResponseNotifications(response, ctx)
        callback(response if self.__isSuccessResponse(response) else None)
        return

    @async
    @process
    def joinEvent(self, eventID, callback):
        yield self.sendRequest(EventBoardsJoinEventCtx(eventID))
        callback(self)

    @async
    @process
    def leaveEvent(self, eventID, callback):
        yield self.sendRequest(EventBoardsLeaveEventCtx(eventID))
        callback(self)

    @async
    @process
    def getHangarFlag(self, callback, onLogin=False):
        if not self.__isLoggedIn or self.__isLoggedIn and not onLogin:
            response = yield self.sendRequest(EventBoardsGetHangarFlagCtx())
            if response is not None:
                self.__isLoggedIn = True
                self.__hangarFlagData.setData(response.getData())
                self.updateHangarFlag()
        callback(self)
        return

    @async
    @process
    def getEvents(self, callback, onlySettings=False, isTabVisited=False, onLogin=False, prefetchKeyArtBig=True):
        statusCode = SET_DATA_STATUS_CODE.ERROR
        eventsSettings = self.__eventBoardsSettings.getEventsSettings()
        playerData = self.__eventBoardsSettings.getPlayerEventsData()
        if not self.__isLoggedIn or self.__isLoggedIn and not onLogin:
            edResponse = yield self.sendRequest(EventBoardsGetEventDataCtx(needShowErrorNotification=not onlySettings))
            if edResponse is not None:
                statusCode = eventsSettings.setData(edResponse.getData(), prefetchKeyArtBig)
                if statusCode == SET_DATA_STATUS_CODE.OK:
                    self.__checkStartedFinishedEvents(isTabVisited)
                    if onlySettings:
                        statusCode = SET_DATA_STATUS_CODE.RETURN
                else:
                    self.updateHangarFlag()
            else:
                playerData.clearData()
        if statusCode == SET_DATA_STATUS_CODE.OK:
            pdResponse = yield self.sendRequest(EventBoardsGetPlayerDataCtx())
            if pdResponse is not None:
                statusCode = playerData.setData(pdResponse.getData())
            else:
                statusCode = SET_DATA_STATUS_CODE.ERROR
                playerData.clearData()
        if statusCode == SET_DATA_STATUS_CODE.OK and eventsSettings is not None:
            myTopData = self.__eventBoardsSettings.getMyEventsTop()
            newEventsMyTop = []
            for event in eventsSettings.getEvents():
                eventID = event.getEventID()
                pState = playerData.getPlayerStateByEventId(eventID)
                vehicles = event.getLimits().getVehiclesWhiteList()
                if not self.__getAvailableVehicles(vehicles) and pState is not None:
                    pState.updateStateReason(_psr.VEHICLESMISSING)
                if not event.isStarted() or pState is None or pState.getPlayerState() != EVENT_STATE.JOINED:
                    continue
                myETop = dict()
                metResponse = yield self.sendRequest(EventBoardsGetMyEventTopCtx(eventID))
                if metResponse is not None:
                    myETop['data'] = metResponse.getData()
                    myETop['event_id'] = eventID
                    newEventsMyTop.append(myETop)

            myTopData.setData(newEventsMyTop)
        callback(self)
        return

    @async
    @process
    def getMyLeaderboardInfo(self, eventID, leaderboardID, callback):
        statusCode = SET_DATA_STATUS_CODE.ERROR
        milbResponse = yield self.sendRequest(EventBoardsGetMyLeaderboardPositionCtx(eventID, leaderboardID))
        if milbResponse is not None:
            myInfoData = MyInfoInLeaderBoard()
            statusCode = myInfoData.setData(milbResponse.getData(), eventID, leaderboardID)
        if statusCode == SET_DATA_STATUS_CODE.OK:
            callback(myInfoData)
        else:
            callback(None)
        return

    @async
    @process
    def getLeaderboard(self, eventID, leaderboardID, pageNumber, callback):
        statusCode = SET_DATA_STATUS_CODE.ERROR
        lbResponse = yield self.sendRequest(EventBoardsGetLeaderboardCtx(eventID, leaderboardID, pageNumber))
        if lbResponse is not None:
            eventSettings = self.__eventBoardsSettings.getEventsSettings().getEvent(eventID)
            mType = eventSettings.getMethod()
            lbType = eventSettings.getType()
            leaderboardData = LeaderBoard()
            statusCode = leaderboardData.setData(lbResponse.getData(), leaderboardID, mType, lbType)
        if statusCode == SET_DATA_STATUS_CODE.OK:
            callback(leaderboardData)
        else:
            callback(None)
        return

    @async
    @process
    def getFootballEvents(self, callback):
        footballSettings = self.__footballEventSettings.getEventsSettings()
        edResponse = yield self.sendRequest(EventBoardsGetFootballEventDataCtx(needShowErrorNotification=False))
        if edResponse is not None:
            footballSettings.setData(edResponse.getData())
            self._invokeListeners('onUpdateFootballEvents')
        callback(self)
        return

    def __isSuccessResponse(self, response):
        return isinstance(response, Response) and (response.getCode() == ResponseCodes.NO_ERRORS or response.extraCode in SUCCESS_STATUSES)

    def __checkStartedFinishedEvents(self, isTabVisited):
        eventsSettings = self.__eventBoardsSettings
        events = eventsSettings.getEventsSettings().getEvents()
        if events:
            notifications = AccountSettings.getNotifications(ELEN_NOTIFICATIONS)
            started = notifications.get(MISSIONS_CONSTANTS.ELEN_EVENT_STARTED_NOTIFICATION)
            finished = notifications.get(MISSIONS_CONSTANTS.ELEN_EVENT_FINISHED_NOTIFICATION)
            visited = notifications.get(MISSIONS_CONSTANTS.ELEN_EVENT_TAB_VISITED)
            allEventID = [ event.getEventID() for event in events ]
            started = started.intersection(allEventID)
            finished = finished.intersection(allEventID)
            visited = visited.intersection(allEventID)
            notifications[MISSIONS_CONSTANTS.ELEN_EVENT_STARTED_NOTIFICATION] = started
            notifications[MISSIONS_CONSTANTS.ELEN_EVENT_FINISHED_NOTIFICATION] = finished
            notifications[MISSIONS_CONSTANTS.ELEN_EVENT_TAB_VISITED] = visited
            for event in events:
                eventID = event.getEventID()
                if isTabVisited and event.isStarted() and not event.isFinished():
                    visited.add(eventID)
                if event.isAtBeginning():
                    if eventID not in started:
                        SystemMessages.pushMessage(_ms(EVENT_BOARDS.NOTIFICATION_EVENTSTARTED_BODY, eventName=event.getName()), messageData={'header': _ms(EVENT_BOARDS.NOTIFICATION_EVENTSTARTED_HEADER)}, type=SM_TYPE.OpenEventBoards)
                        started.add(eventID)
                if event.isAfterEnd() and eventID in visited:
                    if eventID not in finished:
                        self.__complexWarningNotification(_ms(EVENT_BOARDS.NOTIFICATION_EVENTFINISHED_HEADER), _ms(EVENT_BOARDS.NOTIFICATION_EVENTFINISHED_BODY, eventName=event.getName()))
                        finished.add(eventID)

            AccountSettings.setNotifications(ELEN_NOTIFICATIONS, notifications)

    def __handleResponseNotifications(self, response, ctx):
        requestType = ctx.getRequestType()
        if ctx.needShowErrorNotification():
            if requestType == _crdt.EVENT_BOARDS_JOIN_EVENT:
                self.__handleJoinEventNotification(response, ctx)
            elif requestType == _crdt.EVENT_BOARDS_LEAVE_EVENT:
                self.__handleLeaveEventNotification(response, ctx)
            elif not self.__isSuccessResponse(response):
                self.__standardErrorNotification()

    def __handleJoinEventNotification(self, response, ctx):
        if not self.__isSuccessResponse(response):
            data = response.getData()
            extra = data.get('extra_data') if data else None
            if extra and 'RegistrationDeadline' in extra:
                SystemMessages.pushMessage(_ms(EVENT_BOARDS.NOTIFICATION_EVENTJOIN_REGISTRATIONDEADLINE_BODY), type=SM_TYPE.ErrorSimple)
            elif extra and 'OperationNotPermitted' in extra:
                SystemMessages.pushMessage(_ms(EVENT_BOARDS.NOTIFICATION_EVENTJOIN_CONDITIONSFAILED_BODY), type=SM_TYPE.ErrorSimple)
            else:
                self.__standardErrorNotification()
        else:
            eventID = ctx.getEventID()
            eventSettings = self.__eventBoardsSettings.getEventsSettings().getEvent(eventID)
            if eventSettings:
                if eventSettings.isStarted():
                    self.__complexWarningNotification(_ms(EVENT_BOARDS.NOTIFICATION_EVENTJOIN_AFTERSTART_HEADER), _ms(EVENT_BOARDS.NOTIFICATION_EVENTJOIN_AFTERSTART_BODY))
                else:
                    self.__complexWarningNotification(_ms(EVENT_BOARDS.NOTIFICATION_EVENTJOIN_BEFORESTART_HEADER), _ms(EVENT_BOARDS.NOTIFICATION_EVENTJOIN_BEFORESTART_BODY))
        return

    def __handleLeaveEventNotification(self, response, ctx):
        if not self.__isSuccessResponse(response):
            data = response.getData()
            extra = data.get('extra_data') if data else None
            if extra and 'RegistrationDeadline' in extra:
                SystemMessages.pushMessage(_ms(EVENT_BOARDS.NOTIFICATION_EVENTLEAVE_REGISTRATIONDEADLINE_BODY), type=SM_TYPE.ErrorSimple)
            else:
                self.__standardErrorNotification()
        else:
            eventID = ctx.getEventID()
            eventSettings = self.__eventBoardsSettings.getEventsSettings().getEvent(eventID)
            if eventSettings:
                if eventSettings.isStarted():
                    self.__complexWarningNotification(_ms(EVENT_BOARDS.NOTIFICATION_EVENTLEAVE_AFTERSTART_HEADER), _ms(EVENT_BOARDS.NOTIFICATION_EVENTLEAVE_AFTERSTART_BODY))
                else:
                    self.__complexWarningNotification(_ms(EVENT_BOARDS.NOTIFICATION_EVENTLEAVE_BEFORESTART_HEADER), _ms(EVENT_BOARDS.NOTIFICATION_EVENTLEAVE_BEFORESTART_BODY))
        return

    def __complexWarningNotification(self, header, body):
        SystemMessages.pushMessage(body, messageData={'header': header}, type=SM_TYPE.WarningHeader)

    def __standardErrorNotification(self):
        SystemMessages.pushMessage(_ms(EVENT_BOARDS.NOTIFICATION_UNKNOWNERROR_BODY), type=SM_TYPE.Error)

    def __getAvailableVehicles(self, vehicleIds):
        items = self.itemsCache.items
        availableVehicles = []
        for vehCD in vehicleIds:
            if items.doesVehicleExist(vehCD):
                vehicle = items.getItemByCD(vehCD)
                if vehicle.isInInventory:
                    availableVehicles.append(vehicle)

        return availableVehicles
