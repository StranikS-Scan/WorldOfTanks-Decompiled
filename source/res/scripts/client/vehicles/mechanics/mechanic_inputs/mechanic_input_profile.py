# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/mechanics/mechanic_inputs/mechanic_input_profile.py
from __future__ import absolute_import
import logging
import weakref
import Input
from Input import TriggerEvent
from vehicle_systems.stricted_loading import makeCallbackWeak
_logger = logging.getLogger(__name__)

class PlayerVehicleInputPredicate(object):

    def __init__(self, entity):
        super(PlayerVehicleInputPredicate, self).__init__()
        self._entityRef = weakref.ref(entity)

    def __call__(self):
        vehicle = self._entityRef()
        return vehicle is not None and vehicle.isPlayerVehicle and vehicle.isAlive()


class MechanicInputProfile(object):

    def __init__(self, vehicle, profileName, actionName, callback, predicateFactory=PlayerVehicleInputPredicate, activateOnAttach=True):
        self.__vehicleRef = weakref.ref(vehicle)
        self.__profileName = profileName
        self.__actionName = actionName
        self.__callback = makeCallbackWeak(callback)
        self.__predicateFactory = predicateFactory
        self.__activateOnAttach = activateOnAttach

    def attach(self):
        if self.__activateOnAttach:
            self.activate()

    def activate(self):
        if self.__callback is None:
            return
        else:
            inputSystem = Input.inputSystem()
            if not inputSystem.hasProfile(self.__profileName):
                _logger.error('[INPUT] InputProfile %s is not loaded', self.__profileName)
                return
            action = inputSystem.findAction(self.__profileName, self.__actionName)
            if action is None:
                _logger.error("[INPUT] Can't find InputAction %s/%s", self.__profileName, self.__actionName)
                return
            vehicle = self.__vehicleRef()
            if vehicle is not None:
                action.setPredicate(self.__predicateFactory(vehicle))
            action.bindEventReaction(TriggerEvent.Triggered, self.__callback)
            inputSystem.activateProfile(self.__profileName)
            return

    def deactivate(self):
        inputSystem = Input.inputSystem()
        if inputSystem.hasProfile(self.__profileName):
            inputSystem.deactivateProfile(self.__profileName, unbindAllReactions=True)

    def destroy(self):
        self.__callback = None
        self.__vehicleRef = None
        return
