# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/game_objects/festivalrace_objects/race_sound_zone.py
import Triggers
import Math
from constants import IS_CLIENT

def buildCommon(gameObject):
    gameObject.createComponent(Triggers.SquareAreaComponent, Math.Vector3(0, -2, -13), Math.Vector3(48, 10, 13))


def buildClient(gameObject):
    trigger = gameObject.createComponent(Triggers.AreaTriggerComponent)
    if not IS_CLIENT:
        import GameplayDebug
        gameObject.createComponent(GameplayDebug.TextComponent, 'Race Sound Zone', Math.Vector3(0.0, 0.0, 0.0), 4278190335L)
        return
    from game_objects.festivalrace_objects import race_sound_zone

    def zoneEnter(who, where):
        race_sound_zone.onVehicleEnterZone(who, where)

    def zoneExit(who, where):
        race_sound_zone.onVehicleExitZone(who, where)

    trigger.addEnterReaction(zoneEnter)
    trigger.addExitReaction(zoneExit)


def buildServer(gameObject):
    pass


def buildEditor(gameObject):
    pass
