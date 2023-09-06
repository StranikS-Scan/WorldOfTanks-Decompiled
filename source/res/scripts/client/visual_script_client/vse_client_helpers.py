# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/visual_script_client/vse_client_helpers.py
import BigWorld

def runPlan(entity, planName, params, key='', contextName=''):
    player = BigWorld.player()
    if player is not None:
        arena = player.arena
        if arena is not None:
            context = None
            if contextName:
                if entity and hasattr(entity, 'getVseContextInstance'):
                    context = entity.getVseContextInstance(contextName)
                else:
                    context = arena.getVseContextInstance(contextName)
            arena.runVsePlan(planName, params, key, context)
    return


def stopPlan(planName, key=''):
    player = BigWorld.player()
    if player is not None:
        arena = player.arena
        if arena is not None:
            arena.stopVsePlan(planName, key)
    return
