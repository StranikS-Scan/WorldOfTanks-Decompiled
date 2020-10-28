# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/ScopeTemplates.py
from frameworks.wulf import WindowLayer
from soft_exception import SoftException

class SCOPE_TYPE(object):
    GLOBAL = 'global'
    DYNAMIC = 'dynamic'
    VIEW = WindowLayer.VIEW
    LOBBY_SUB = WindowLayer.SUB_VIEW
    LOBBY_TOP_SUB = WindowLayer.TOP_SUB_VIEW
    DEFAULT = VIEW
    WINDOW = WindowLayer.WINDOW
    TOP_WINDOW = WindowLayer.TOP_WINDOW
    FULLSCREEN = WindowLayer.FULLSCREEN_WINDOW
    WAITING = WindowLayer.WAITING
    WINDOW_VIEWED_MULTISCOPE = 'WindowViewed'


class SimpleScope(object):
    __slots__ = ('__scopeType', '__parentScope', '__dependencedScopes')

    def __init__(self, scopeType, parentScope):
        super(SimpleScope, self).__init__()
        if scopeType is None:
            raise SoftException('ScopeType cannot be None!')
        self.__scopeType = scopeType
        self.__parentScope = None
        self.__dependencedScopes = []
        self._setParentScope(parentScope)
        return

    def __repr__(self):
        return '{}[{}]=[scopeType={}, parentScope={}]'.format(self.__class__.__name__, hex(id(self)), self.__scopeType, self.__parentScope)

    def _setParentScope(self, parentScope):
        if self.__parentScope is not None:
            raise SoftException('parent scope can be set at one time only!')
        self.__parentScope = parentScope
        if self.__parentScope is not None:
            self.__parentScope.addDependencedScope(self)
        return

    def getScopeType(self):
        return self.__scopeType

    def isInScope(self, scopeType):
        return scopeType == self.getScopeType()

    def getRecommendedScopeData(self, currentScope):
        return (self.getScopeType(), False)

    def addDependencedScope(self, simpleScope):
        self.__dependencedScopes.append(simpleScope)

    def isOwnerFor(self, scope):
        return scope in self.__dependencedScopes

    def searchOwnersFor(self, scope):
        outcome = set([])
        if self.isOwnerFor(scope):
            outcome.add(self)
        else:
            for dependencedScope in self.__dependencedScopes:
                outcome |= dependencedScope.searchOwnersFor(scope)

        return outcome


class MultipleScope(SimpleScope):

    def __init__(self, scopeType, parentScopes):
        if not parentScopes:
            raise SoftException('parentScopes list can not be empty')
        if len(parentScopes) == 1:
            raise SoftException('MultipleScope can not have an only one parent')
        super(MultipleScope, self).__init__(scopeType, parentScopes[0])
        i = 1
        while i < len(parentScopes):
            if parentScopes[i] is not None:
                parentScopes[i].addDependencedScope(self)
            else:
                raise SoftException('One of parents is None!')
            i += 1

        return


class GlobalScope(SimpleScope):

    def __init__(self, scopeType):
        super(GlobalScope, self).__init__(scopeType, None)
        return

    def getRecommendedScopeData(self, currentScope):
        scopeIsGlobal = False
        recommendedViewScope = self.getScopeType()
        if self.isInScope(SCOPE_TYPE.DYNAMIC):
            recommendedViewScope = currentScope.getScopeType()
        if self.isInScope(SCOPE_TYPE.GLOBAL):
            recommendedViewScope = SCOPE_TYPE.VIEW
            scopeIsGlobal = True
        return (recommendedViewScope, scopeIsGlobal)


GLOBAL_SCOPE = GlobalScope(SCOPE_TYPE.GLOBAL)
DYNAMIC_SCOPE = GlobalScope(SCOPE_TYPE.DYNAMIC)
VIEW_SCOPE = SimpleScope(SCOPE_TYPE.VIEW, GLOBAL_SCOPE)
WINDOW_SCOPE = SimpleScope(SCOPE_TYPE.WINDOW, GLOBAL_SCOPE)
TOP_WINDOW_SCOPE = SimpleScope(SCOPE_TYPE.TOP_WINDOW, GLOBAL_SCOPE)
DEFAULT_SCOPE = VIEW_SCOPE
LOBBY_SUB_SCOPE = SimpleScope(SCOPE_TYPE.LOBBY_SUB, DEFAULT_SCOPE)
LOBBY_TOP_SUB_SCOPE = SimpleScope(SCOPE_TYPE.LOBBY_TOP_SUB, DEFAULT_SCOPE)
WINDOW_VIEWED_MULTISCOPE = MultipleScope(SCOPE_TYPE.WINDOW_VIEWED_MULTISCOPE, (WINDOW_SCOPE, LOBBY_SUB_SCOPE, LOBBY_TOP_SUB_SCOPE))
VIEW_TYPES_TO_SCOPES = {WindowLayer.VIEW: VIEW_SCOPE,
 WindowLayer.WINDOW: WINDOW_SCOPE,
 WindowLayer.TOP_WINDOW: TOP_WINDOW_SCOPE,
 WindowLayer.SUB_VIEW: LOBBY_SUB_SCOPE,
 WindowLayer.TOP_SUB_VIEW: LOBBY_TOP_SUB_SCOPE}
