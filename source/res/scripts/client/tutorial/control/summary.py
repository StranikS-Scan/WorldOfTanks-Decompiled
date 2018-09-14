# Embedded file name: scripts/client/tutorial/control/summary.py
from tutorial.control.functional import FunctionalVarSet
from tutorial.logger import LOG_ERROR, LOG_DEBUG

class _Flag(object):

    def __init__(self, name, active, store = True):
        super(_Flag, self).__init__()
        self.name = name
        self.active = active
        self.store = store

    def __repr__(self):
        return '{0:>s}: {1!r:s}'.format(self.name, self.active)

    def isActive(self):
        return self.active

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False


class FlagSummary(object):

    def __init__(self, flagNames, initial = None):
        super(FlagSummary, self).__init__()
        if flagNames is None:
            flagNames = []
        if initial is None:
            initial = {}
        self.__flags = {}
        initialGetter = initial.get
        for name in flagNames:
            self.__flags[name] = _Flag(name, initialGetter(name, False))

        return

    def __repr__(self):
        return 'FlagSummary({0:s}): {1!r:s}'.format(hex(id(self)), self.__flags.values())

    def deactivateFlag(self, flagName):
        LOG_DEBUG('Deactivate flag', flagName)
        if flagName in self.__flags:
            self.__flags[flagName].deactivate()
        else:
            self.__flags[flagName] = _Flag(flagName, False, store=False)

    def activateFlag(self, flagName):
        LOG_DEBUG('Activate flag: ', flagName)
        if flagName in self.__flags:
            self.__flags[flagName].activate()
        else:
            self.__flags[flagName] = _Flag(flagName, True, store=False)

    def isActiveFlag(self, flagName):
        activeFlag = False
        if flagName in self.__flags:
            activeFlag = self.__flags[flagName].isActive()
        return activeFlag

    def addFlag(self, flagName):
        if flagName not in self.__flags:
            self.__flags[flagName] = _Flag(flagName, False)

    def getDict(self):
        filtered = filter(lambda flag: flag.store, self.__flags.itervalues())
        return dict(map(lambda flag: (flag.name, flag.active), filtered))


class VarSummary(object):

    def __init__(self, varSets, runtime = None):
        super(VarSummary, self).__init__()
        if varSets:
            self.__varSets = dict(map(lambda varSet: (varSet.getID(), FunctionalVarSet(varSet)), varSets))
        else:
            self.__varSets = {}
        self.__runtime = runtime or {}

    def get(self, varID, default = None):
        if varID in self.__varSets:
            result = self.__varSets[varID].getFirstActual()
        else:
            result = self.__runtime.get(varID, default)
        return result

    def set(self, varID, value):
        if varID in self.__varSets:
            LOG_ERROR('Var {0:>s} in not mutable.'.format(varID))
        else:
            LOG_DEBUG('Set var {0:>s}'.format(varID), value)
            self.__runtime[varID] = value
