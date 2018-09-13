# Embedded file name: scripts/client/tutorial/control/triggers.py
from tutorial.control import TutorialProxyHolder
from tutorial.data import IHasID
from tutorial.logger import LOG_ERROR

class _Trigger(TutorialProxyHolder, IHasID):

    def __init__(self, triggerID):
        super(_Trigger, self).__init__()
        self.__triggerID = triggerID
        self.__onEffects = []
        self.__offEffects = []
        self.__excludeTriggerIDs = []
        self.isRunning = False
        self.isSubscribed = False

    def getID(self):
        return self.__triggerID

    def setID(self, entityID):
        self.__triggerID = entityID

    def addOnEffect(self, effect):
        self.__onEffects.append(effect)

    def addOffEffect(self, effect):
        self.__offEffects.append(effect)

    def addExcludeTriggerID(self, triggerID):
        self.__excludeTriggerIDs.append(triggerID)

    def run(self):
        self.isRunning = True
        self.toggle(isOn=self.isOn())

    def clear(self):
        self.isRunning = False

    def isOn(self, *args):
        return True

    def toggle(self, isOn = True, benefit = True, **kwargs):
        effects = self.__offEffects
        if isOn:
            effects = self.__onEffects
            getter = self._tutorial._data.getTrigger
            for triggerID in self.__excludeTriggerIDs:
                trigger = getter(triggerID)
                if trigger is not None:
                    trigger.clear()
                else:
                    LOG_ERROR('Trigger not found', triggerID)

        if len(effects):
            self._tutorial.storeEffectsInQueue(effects, benefit=benefit)
        self.isRunning = False
        return

    def _setFlagValue(self, flagID, value):
        if flagID is None:
            return
        else:
            flags = self._tutorial.getFlags()
            isActive = flags.isActiveFlag(flagID)
            if value:
                if not isActive:
                    flags.activateFlag(flagID)
                    self._tutorial.invalidateFlags()
            elif isActive:
                flags.deactivateFlag(flagID)
                self._tutorial.invalidateFlags()
            return


class _TriggerWithValidateVar(_Trigger):

    def __init__(self, triggerID, validateVarID, setVarID = None):
        super(_TriggerWithValidateVar, self).__init__(triggerID)
        self._validateVarID = validateVarID
        self._setVarID = setVarID

    def vars(self):
        return self._tutorial.getVars()

    def getVar(self):
        return self._tutorial.getVars().get(self._validateVarID)

    def getIterVar(self):
        var = self._tutorial.getVars().get(self._validateVarID)
        if hasattr(var, '__iter__'):
            var = set(var)
        else:
            var = set([var])
        return var

    def setVar(self, value):
        if self._setVarID is not None:
            self._tutorial.getVars().set(self._setVarID, value)
        return
