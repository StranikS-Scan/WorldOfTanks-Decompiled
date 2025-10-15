# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/common/portal_helpers.py
import typing
if typing.TYPE_CHECKING:
    from Math import Vector3

def clampImpulse(impulse, mass, velocity, velocityLimit):
    newVelocity = velocity + impulse / mass
    length = newVelocity.length
    if length <= velocityLimit:
        return impulse
    factor = velocityLimit / length
    return (newVelocity * factor - velocity) * mass
