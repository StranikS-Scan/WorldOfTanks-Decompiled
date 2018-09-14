# Embedded file name: scripts/client/gui/shared/fortifications/states.py
import BigWorld
from FortifiedRegionBase import FORT_STATE
from gui.Scaleform.genConsts.FORTIFICATION_ALIASES import FORTIFICATION_ALIASES
from gui.shared.fortifications import getClientFort, isStartingScriptDone
from gui.shared.fortifications.settings import CLIENT_FORT_STATE
from gui.LobbyContext import g_lobbyContext

class _ClientFortState(object):

    def __init__(self, stateID, isInitial = False, isDisabled = False):
        super(_ClientFortState, self).__init__()
        self._stateID = stateID
        self._isInitial = isInitial
        self._isDisabled = isDisabled

    def __repr__(self):
        return '{0:>s}(stateID={1:n}, isInitial={2!r:s}, isDisabled={3!r:s})'.format(self.__class__.__name__, self._stateID, self._isInitial, self._isDisabled)

    def getStateID(self):
        return self._stateID

    def isInitial(self):
        return self._isInitial

    def isDisabled(self):
        return self._isDisabled

    def update(self, provider):
        raise NotImplementedError

    def getUIMode(self, provider, transportingProgress = None):
        raise NotImplementedError


class RoamingState(_ClientFortState):

    def __init__(self):
        super(RoamingState, self).__init__(CLIENT_FORT_STATE.ROAMING, isDisabled=True)

    def update(self, provider):
        result = False
        serverSettings = g_lobbyContext.getServerSettings()
        if serverSettings is not None and not serverSettings.roaming.isInRoaming():
            state = NoClanState()
            result = state.update(provider)
            if not result:
                result = True
                provider.changeState(state)
        return result


class NoClanState(_ClientFortState):

    def __init__(self):
        super(NoClanState, self).__init__(CLIENT_FORT_STATE.NO_CLAN, isInitial=True)

    def update(self, provider):
        result = False
        cache = provider.getClanCache()
        if cache.isInClan:
            state = CenterUnavailableState()
            result = state.update(provider)
            if not result:
                result = True
                provider.changeState(state)
        return result


class CenterUnavailableState(_ClientFortState):

    def __init__(self):
        super(CenterUnavailableState, self).__init__(CLIENT_FORT_STATE.CENTER_UNAVAILABLE, isDisabled=True)

    def update(self, provider):
        result = False
        if not getattr(BigWorld.player(), 'isLongDisconnectedFromCenter', False):
            state = UnsubscribeState()
            result = state.update(provider)
            if not result:
                result = True
                provider.changeState(state)
        return result


class UnsubscribeState(_ClientFortState):

    def __init__(self):
        super(UnsubscribeState, self).__init__(CLIENT_FORT_STATE.UNSUBSCRIBED)

    def update(self, provider):
        result = False
        if provider.isSubscribed():
            state = NoFortState()
            result = state.update(provider)
            if not result:
                result = True
                provider.changeState(state)
        return result


class NoFortState(_ClientFortState):

    def __init__(self):
        super(NoFortState, self).__init__(CLIENT_FORT_STATE.NO_FORT, isInitial=True)

    def update(self, provider):
        cache = provider.getClanCache()
        result = False
        state = None
        fort = getClientFort()
        if not fort.isEmpty():
            if isStartingScriptDone():
                state = HasFortState()
            elif provider.getController().getPermissions().canCreate():
                state = WizardState()
        if state:
            result = state.update(provider)
            if not result:
                result = True
                provider.changeState(state)
        return result


class WizardState(_ClientFortState):

    def __init__(self):
        super(WizardState, self).__init__(CLIENT_FORT_STATE.WIZARD)

    def update(self, provider):
        result = False
        fort = getClientFort()
        if not fort.isEmpty() and fort.isStartingScriptDone():
            state = HasFortState()
            result = state.update(provider)
            if not result:
                result = True
                provider.changeState(state)
        return result

    def getUIMode(self, provider, transportingProgress = None):
        fort = getClientFort()
        if fort.state & FORT_STATE.FIRST_DIR_OPEN == 0:
            return FORTIFICATION_ALIASES.MODE_DIRECTIONS_TUTORIAL
        elif fort.state & FORT_STATE.FIRST_BUILD_START == 0:
            return FORTIFICATION_ALIASES.MODE_COMMON_TUTORIAL
        else:
            if transportingProgress is not None:
                if fort.isTransportationAvailable():
                    return transportingProgress
                else:
                    return FORTIFICATION_ALIASES.MODE_TRANSPORTING_NOT_AVAILABLE
            elif fort.state & FORT_STATE.FIRST_BUILD_DONE == 0:
                return FORTIFICATION_ALIASES.MODE_TRANSPORTING_TUTORIAL
            return FORTIFICATION_ALIASES.MODE_COMMON


class HasFortState(_ClientFortState):

    def __init__(self):
        super(HasFortState, self).__init__(CLIENT_FORT_STATE.HAS_FORT)

    def update(self, provider):
        return False

    def getUIMode(self, provider, transportingProgress = None):
        fort = getClientFort()
        if not fort.getOpenedDirections() and provider.getController().getPermissions().canOpenDirection():
            return FORTIFICATION_ALIASES.MODE_DIRECTIONS
        else:
            if transportingProgress is not None:
                if fort.isTransportationAvailable():
                    return transportingProgress
                else:
                    return FORTIFICATION_ALIASES.MODE_TRANSPORTING_NOT_AVAILABLE
            return FORTIFICATION_ALIASES.MODE_COMMON


def create(provider):
    state = RoamingState()
    result = state.update(provider)
    if not result:
        provider.changeState(state)
