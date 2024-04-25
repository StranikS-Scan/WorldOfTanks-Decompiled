# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/HBBattleFeedbackComponent.py
import BigWorld
import Event

class HBBattleFeedbackComponent(BigWorld.DynamicScriptComponent):
    onVehicleHeal = Event.Event()

    @classmethod
    def unpackHBActionApplied(cls, packedEffect):
        return (packedEffect >> 24 & 65535, packedEffect >> 12 & 4095, packedEffect & 255)
