# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_events/gun_events.py
from __future__ import absolute_import
import typing
import CGF
import Vehicular

def postVehicularSingleShotEvent(spaceID, entityID, slotName, gunID):
    CGF.postEvent(spaceID, Vehicular.SingleShotEvent(entityID=entityID, slotName=slotName, gunID=gunID))


def postVehicularMultiShotEvent(spaceID, entityID, slotName, gunIDs):
    CGF.postEvent(spaceID, Vehicular.MultiShotEvent(entityID=entityID, slotName=slotName, gunIDs=gunIDs))


def postVehicularContinuousBurstEvent(spaceID, entityID, slotName, active):
    CGF.postEvent(spaceID, Vehicular.ContinuousBurstEvent(entityID=entityID, slotName=slotName, active=active))


def postVehicularFireRateChangedEvent(spaceID, entityID, slotName, shotsPerSec):
    CGF.postEvent(spaceID, Vehicular.FireRateChangedEvent(entityID=entityID, slotName=slotName, shotsPerSec=shotsPerSec))


def postVehicularTemperatureChangedEvent(spaceID, entityID, slotName, currentTemperature, maxTemperature):
    CGF.postEvent(spaceID, Vehicular.TemperatureChangedEvent(entityID=entityID, slotName=slotName, currentTemperature=currentTemperature, maxTemperature=maxTemperature))
