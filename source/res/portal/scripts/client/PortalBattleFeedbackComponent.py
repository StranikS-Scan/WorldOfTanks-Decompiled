# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/PortalBattleFeedbackComponent.py
import BigWorld
import Event

class PortalBattleFeedbackComponent(BigWorld.DynamicScriptComponent):
    onVehicleHeal = Event.Event()

    @classmethod
    def unpackPortalActionApplied(cls, packedEffect):
        return (packedEffect >> 24 & 65535, packedEffect >> 12 & 4095, packedEffect & 255)
