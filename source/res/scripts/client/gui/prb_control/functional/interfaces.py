# Embedded file name: scripts/client/gui/prb_control/functional/interfaces.py
from debug_utils import LOG_DEBUG
from gui.prb_control.items import prb_items, unit_items
from gui.prb_control.restrictions.interfaces import IPrbPermissions, IPreQueuePermissions
from gui.prb_control.restrictions.interfaces import IUnitPermissions
from gui.prb_control.settings import PREBATTLE_ROSTER, makePrebattleSettings
from gui.prb_control.settings import FUNCTIONAL_EXIT, FUNCTIONAL_INIT_RESULT, CTRL_ENTITY_TYPE

class IPrbEntry(object):

    def makeDefCtx(self):
        return None

    def create(self, ctx, callback = None):
        pass

    def join(self, ctx, callback = None):
        pass

    def select(self, ctx, callback = None):
        pass


class IPrbListUpdater(object):

    def start(self, callback):
        pass

    def stop(self):
        pass


class IPrbListRequester(IPrbListUpdater):

    def request(self, ctx = None):
        pass


class IStatefulFunctional(object):

    def getStates(self):
        return ({}, None)

    def applyStates(self, states):
        pass


class IClientFunctional(object):

    def init(self, **kwargs):
        return FUNCTIONAL_INIT_RESULT.INITED

    def fini(self, **kwargs):
        pass

    def getExit(self):
        return FUNCTIONAL_EXIT.NO_FUNC

    def setExit(self, exit):
        pass

    def isPlayerJoined(self, ctx):
        return False

    def canPlayerDoAction(self):
        return (True, '')

    def doAction(self, action = None, dispatcher = None):
        return False

    def doSelectAction(self, action):
        pass

    def doLeaveAction(self, dispatcher, ctx = None):
        pass

    def showGUI(self):
        return False

    def getConfirmDialogMeta(self, funcExit = FUNCTIONAL_EXIT.NO_FUNC):
        return None

    def getID(self):
        return 0

    def getPrbType(self):
        return 0

    def getPrbTypeName(self):
        return 'N/A'

    def hasEntity(self):
        return False

    def hasLockedState(self):
        return False

    def getUnitFullData(self, unitIdx = None):
        return None

    def isCreator(self, dbID = None):
        return False

    def leave(self, ctx, callback = None):
        pass

    def request(self, ctx, callback = None):
        pass

    def reset(self):
        pass


class IListenersCollection(object):

    def addListener(self, listener):
        pass

    def removeListener(self, listener):
        pass


class IPrbFunctional(IClientFunctional, IListenersCollection):

    def __init__(self):
        LOG_DEBUG('Prebattle functional inited:', self)

    def __del__(self):
        LOG_DEBUG('Prebattle functional deleted:', self)

    def init(self, clientPrb = None, ctx = None):
        return FUNCTIONAL_INIT_RESULT.INITED

    def fini(self, clientPrb = None, woEvents = False):
        pass

    def getEntityType(self):
        return CTRL_ENTITY_TYPE.PREBATTLE

    def getSettings(self):
        return makePrebattleSettings()

    def getRosterKey(self, pID = None):
        return PREBATTLE_ROSTER.UNKNOWN

    def getRosters(self, keys = None):
        return dict.fromkeys(PREBATTLE_ROSTER.ALL, [])

    def getPlayerInfo(self, pID = None, rosterKey = None):
        return prb_items.PlayerPrbInfo(-1L)

    def getPlayerInfoByDbID(self, dbID):
        return prb_items.PlayerPrbInfo(-1L)

    def getPlayerTeam(self, pID = None):
        return 0

    def getTeamState(self, team = None):
        return prb_items.TeamStateInfo(0)

    def getPlayersStateStats(self):
        return prb_items.PlayersStateStats(0, False, 0, 0)

    def getRoles(self, pDatabaseID = None, clanDBID = None, team = None):
        return 0

    def getPermissions(self, pID = None):
        return IPrbPermissions()

    def getLimits(self):
        return None

    def exitFromQueue(self):
        return False

    def hasGUIPage(self):
        return False

    def isGUIProcessed(self):
        return False


class IIntoPrbListener(object):

    def onIntroPrbFunctionalInited(self):
        pass

    def onIntroPrbFunctionalFinished(self):
        pass

    def onPrbListReceived(self, result):
        pass

    def onPrbRosterReceived(self, prebattleID, iterator):
        pass


class IPrbListener(IIntoPrbListener):

    def onPrbFunctionalInited(self):
        pass

    def onPrbFunctionalFinished(self):
        pass

    def onSettingUpdated(self, functional, settingName, settingValue):
        pass

    def onTeamStatesReceived(self, functional, team1State, team2State):
        pass

    def onPlayerAdded(self, functional, playerInfo):
        pass

    def onPlayerRemoved(self, functional, playerInfo):
        pass

    def onRostersChanged(self, functional, rosters, full):
        pass

    def onPlayerTeamNumberChanged(self, functional, team):
        pass

    def onPlayerRosterChanged(self, functional, actorInfo, playerInfo):
        pass

    def onPlayerStateChanged(self, functional, roster, accountInfo):
        pass


class IPreQueueFunctional(IListenersCollection):

    def __init__(self):
        LOG_DEBUG('Queue functional inited:', self)

    def __del__(self):
        LOG_DEBUG('Queue functional deleted:', self)

    def init(self, ctx = None):
        return FUNCTIONAL_INIT_RESULT.INITED

    def fini(self, woEvents = False):
        pass

    def getEntityType(self):
        return CTRL_ENTITY_TYPE.PREQUEUE

    def isPlayerJoined(self, ctx):
        return False

    def getQueueType(self):
        return 0

    def hasEntity(self):
        return False

    def canPlayerDoAction(self):
        pass

    def showGUI(self):
        return False

    def doAction(self, action = None, dispatcher = None):
        return False

    def doSelectAction(self, action):
        return False

    def isInQueue(self):
        return False

    def hasGUIPage(self):
        return False

    def hasLockedState(self):
        return False

    def exitFromQueue(self):
        return False

    def getConfirmDialogMeta(self, funcExit = FUNCTIONAL_EXIT.NO_FUNC):
        return None

    def getPermissions(self, pID = None):
        return IPreQueuePermissions()


class IPreQueueListener(object):

    def onPreQueueFunctionalInited(self):
        pass

    def onPreQueueFunctionalFinished(self):
        pass

    def onEnqueued(self):
        pass

    def onDequeued(self):
        pass

    def onEnqueueError(self, *args):
        pass

    def onKickedFromQueue(self, *args):
        pass

    def onKickedFromArena(self, *args):
        pass

    def onPreQueueSettingsChanged(self, diff):
        pass


class IUnitFunctional(IClientFunctional, IListenersCollection):

    def __init__(self):
        LOG_DEBUG('Unit functional inited:', self)

    def __del__(self):
        LOG_DEBUG('Unit functional deleted:', self)

    def init(self, ctx = None):
        return FUNCTIONAL_INIT_RESULT.INITED

    def fini(self, woEvents = False):
        pass

    def getEntityType(self):
        return CTRL_ENTITY_TYPE.UNIT

    def rejoin(self):
        pass

    def initEvents(self, listener):
        pass

    def getUnitIdx(self):
        return 0

    def setLastError(self, errorCode):
        pass

    def isKicked(self):
        return False

    def getPermissions(self, dbID = None, unitIdx = None):
        return IUnitPermissions()

    def getUnit(self, unitIdx = None, safe = False):
        return (0, None)

    def getRosterSettings(self):
        return unit_items.UnitRosterSettings()

    def getPlayerInfo(self, dbID = None, unitIdx = None):
        return unit_items.PlayerUnitInfo(-1L, 0, None)

    def getReadyStates(self, unitIdx = None):
        return []

    def getSlotState(self, slotIdx, unitIdx = None):
        return unit_items.SlotState(-1)

    def getPlayers(self, unitIdx = None):
        return {}

    def getCandidates(self, unitIdx = None):
        return {}

    def getRoster(self, unitIdx = None):
        return None

    def getVehicleInfo(self, dbID = None, unitIdx = None):
        return unit_items.VehicleInfo()

    def getFlags(self, unitIdx = None):
        return unit_items.UnitFlags(0)

    def getStats(self, unitIdx = None):
        return unit_items.UnitStats(0, 0, 0, 0, [], 0, 0)

    def getComment(self, unitIdx = None):
        return ''

    def getCensoredComment(self, unitIdx = None):
        return ''

    def isGUIProcessed(self):
        return False

    def getShowLeadershipNotification(self):
        return False

    def doLeadershipNotificationShown(self):
        pass

    def validateLevels(self, stats = None, flags = None, vInfo = None):
        return (True, '')

    def getUnitInvalidLevels(self, stats = None):
        return []


class IIntroUnitListener(object):

    def onIntroUnitFunctionalInited(self):
        pass

    def onIntroUnitFunctionalFinished(self):
        pass

    def onUnitAutoSearchStarted(self, timeLeft):
        pass

    def onUnitAutoSearchFinished(self):
        pass

    def onUnitAutoSearchSuccess(self, acceptDelta):
        pass

    def onUnitBrowserErrorReceived(self, errorCode):
        pass


class IUnitListener(IIntroUnitListener):

    def onUnitFunctionalInited(self):
        pass

    def onUnitFunctionalFinished(self):
        pass

    def onUnitFlagsChanged(self, flags, timeLeft):
        pass

    def onUnitPlayerStateChanged(self, pInfo):
        pass

    def onUnitPlayerRolesChanged(self, pInfo, pPermissions):
        pass

    def onUnitPlayerOnlineStatusChanged(self, pInfo):
        pass

    def onUnitPlayerBecomeCreator(self, pInfo):
        pass

    def onUnitPlayerEnterOrLeaveArena(self, pInfo):
        pass

    def onUnitRosterChanged(self):
        pass

    def onUnitMembersListChanged(self):
        pass

    def onUnitPlayerAdded(self, pInfo):
        pass

    def onUnitPlayerInfoChanged(self, pInfo):
        pass

    def onUnitPlayerRemoved(self, pInfo):
        pass

    def onUnitPlayersListChanged(self):
        pass

    def onUnitVehicleChanged(self, dbID, vInfo):
        pass

    def onUnitPlayerVehDictChanged(self, pInfo):
        pass

    def onUnitSettingChanged(self, opCode, value):
        pass

    def onUnitRejoin(self):
        pass

    def onUnitErrorReceived(self, errorCode):
        pass

    def onUnitExtraChanged(self, extra):
        pass

    def onUnitCurfewChanged(self):
        pass


class IGlobalListener(IPrbListener, IUnitListener, IPreQueueListener):
    pass
