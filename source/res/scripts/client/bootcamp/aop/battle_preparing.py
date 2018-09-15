# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bootcamp/aop/battle_preparing.py
""" AOP classes for altering some common logic according to Bootcamp's requirements.

    This module should contain aspects and pointcuts which
    must only be active in bootcamp battle preparation stage (StateBattlePreparing).
"""
from helpers import aop
from bootcamp.aop import common

def weave(weaver, stateBattlePreparing):
    """ Activates all pointcuts which must be always active in bootcamp battle preparation stage.
    :param weaver: AOP weaver to use for scoping
    :param stateBattlePreparing: instance of class bootcamp.states.StateBattlePreparing
    """
    weaver.weave(pointcut=_PointcutDelayStartFirstBattle(stateBattlePreparing))


class _PointcutDelayStartFirstBattle(aop.Pointcut):
    """ Redirects some PlayerAvatar methods to allow delaying their logic by StateBattlePreparing.
        Necessary to handle bootcamp login specifics like intro video before first battle.
    """

    def __init__(self, stateBattlePreparing):
        super(_PointcutDelayStartFirstBattle, self).__init__('Avatar', 'PlayerAvatar', '^(vehicle_onEnterWorld|onEnterWorld|onSpaceLoaded)$', aspects=(common.AspectRedirectMethod({'vehicle_onEnterWorld': stateBattlePreparing.onVehicleOnEnterWorld,
          'onEnterWorld': stateBattlePreparing.onAvatarOnEnterWorld,
          'onSpaceLoaded': stateBattlePreparing.onSpaceLoaded}),))
