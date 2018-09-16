# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bootcamp/aop/battle_preparing.py
from helpers import aop
from bootcamp.aop import common

def weave(weaver, stateBattlePreparing):
    weaver.weave(pointcut=_PointcutDelayStartFirstBattle(stateBattlePreparing))


class _PointcutDelayStartFirstBattle(aop.Pointcut):

    def __init__(self, stateBattlePreparing):
        super(_PointcutDelayStartFirstBattle, self).__init__('Avatar', 'PlayerAvatar', '^(vehicle_onEnterWorld|onEnterWorld|onSpaceLoaded)$', aspects=(common.AspectRedirectMethod({'vehicle_onEnterWorld': stateBattlePreparing.onVehicleOnEnterWorld,
          'onEnterWorld': stateBattlePreparing.onAvatarOnEnterWorld,
          'onSpaceLoaded': stateBattlePreparing.onSpaceLoaded}),))
