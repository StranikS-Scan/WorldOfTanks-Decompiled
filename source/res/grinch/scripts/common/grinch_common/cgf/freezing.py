# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/common/grinch_common/cgf/freezing.py
import CGF
import Triggers
from cgf_script.component_meta_class import registerComponent, ComponentProperty, CGFMetaTypes
from debug_utils import LOG_ERROR
from grinch_common.grinch_freezer import IAttacked, _AttackersData

@registerComponent
class GrinchFreezingTriggerComponent(object):
    category = 'Grinch'
    domain = CGF.DomainOption.DomainAll
    trigger = ComponentProperty(type=CGFMetaTypes.LINK, editorName='AreaTrigger', value=Triggers.AreaTriggerComponent)

    def __init__(self):
        self.enterReactionId = None
        self.exitReactionId = None
        return


@registerComponent
class GrinchFreezingConfigComponent(object):
    category = 'Grinch'
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainServer
    debuffDuration = ComponentProperty(type=CGFMetaTypes.FLOAT, editorName='debuffDuration', value=10.0)
    freezingTime = ComponentProperty(type=CGFMetaTypes.FLOAT, editorName='freezingTime', value=1.0)
    freezeDamage = ComponentProperty(type=CGFMetaTypes.FLOAT, editorName='freezeDamage', value=100.0)
    ownerVehId = ComponentProperty(type=CGFMetaTypes.INT, editorName='ownerVehId', value=0)
    team = ComponentProperty(type=CGFMetaTypes.INT, editorName='team', value=0)
    factorNames = ComponentProperty(type=CGFMetaTypes.STRING_LIST, editorName='factorNames', value=[])
    factorOperations = ComponentProperty(type=CGFMetaTypes.STRING_LIST, editorName='factorOperations', value=[])
    factorValues = ComponentProperty(type=CGFMetaTypes.FLOAT_LIST, editorName='factorValues', value=[])

    def getFactorFullData(self):
        if len(self.factorNames) == len(self.factorOperations) == len(self.factorValues):
            result = []
            for i, fName in enumerate(self.factorNames):
                result.append((fName, self.factorOperations[i], self.factorValues[i]))

            return tuple(result)
        LOG_ERROR('Factors data arrays must have the same length! Please check input data!')
        return tuple()


@registerComponent
class AwaitingFreezingComponent(IAttacked):
    category = 'Grinch'
    domain = CGF.DomainOption.DomainServer

    def __init__(self, creationTime, attackerId, data):
        self.__creationTime = creationTime
        self.__isValid = True
        self.__attackersData = _AttackersData(attackerId, data)

    def getCreationTime(self):
        return self.__creationTime

    def getCurrentAttacker(self):
        return self.__attackersData.getCurrentAttacker()

    def addAttacker(self, attackerId, data):
        self.__attackersData.addAttacker(attackerId, data)

    def removeAttacker(self, attackerId):
        self.__attackersData.removeAttacker(attackerId)

    def iterAttackersData(self):
        for d in self.__attackersData.iterAttackersData():
            yield d

    def getAttackersData(self):
        return tuple(self.iterAttackersData())

    def extractAttackers(self):
        return self.__attackersData

    def hasAttackers(self):
        return self.__attackersData.hasAttackers()

    def isValid(self):
        return self.__isValid

    def cleanup(self):
        self.__attackersData = None
        self.__isValid = False
        return
