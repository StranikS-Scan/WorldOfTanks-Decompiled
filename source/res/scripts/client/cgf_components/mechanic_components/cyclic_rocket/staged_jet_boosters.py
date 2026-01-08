# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/mechanic_components/cyclic_rocket/staged_jet_boosters.py
import CGF
from cgf_script.managers_registrator import autoregister, onAddedQuery, onRemovedQuery
from StagedJetBoostersController import StagedJetBoostersController

@autoregister(presentInAllWorlds=True, domain=CGF.DomainOption.DomainClient)
class StagedJetBoostersComponentManager(CGF.ComponentManager):

    @onAddedQuery(StagedJetBoostersController)
    def onAdded(self, ctrl):
        ctrl.attachInput()

    @onRemovedQuery(StagedJetBoostersController)
    def onRemoved(self, ctrl):
        if ctrl.isValid and not ctrl.isComponentDestroyed():
            ctrl.detachInput()
