# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bootcamp/aop/in_battle.py
""" AOP classes for altering some common logic according to Bootcamp's requirements.

    This module should contain aspects and pointcuts which
    must only be active while in bootcamp battles (StateInBattle).
"""
from helpers import aop
from bootcamp.aop import common

def weave(weaver, stateInBattle):
    """ Activates all pointcuts which must be always active in bootcamp battles.
    :param weaver: AOP weaver to use for scoping
    :param stateInBattle: instance of class bootcamp.states.StateInBattle
    """
    weaver.weave(pointcut=_PointcutToggleFullStats, avoid=True)
    weaver.weave(pointcut=_PointcutAvatarReceiveBattleResults(stateInBattle))
    weaver.weave(pointcut=_PointcutComputePiercingPowerAtDist)
    weaver.weave(pointcut=_PointcutComputePiercingPowerRandomization)
    weaver.weave(pointcut=_PointcutKeepArenaSoundsPlayingOnResultScreen)


class _PointcutToggleFullStats(aop.Pointcut):
    """ Blocks toggling display of full stats in battle (TAB hotkey). """

    def __init__(self):
        super(_PointcutToggleFullStats, self).__init__('gui.battle_control', 'event_dispatcher', 'toggleFullStats')


class _PointcutAvatarReceiveBattleResults(aop.Pointcut):
    """ Tweaks battle results handling logic for Bootcamp battles. """

    def __init__(self, stateInBattle):
        super(_PointcutAvatarReceiveBattleResults, self).__init__('Avatar', 'PlayerAvatar', 'receiveBattleResults', aspects=(common.AspectRedirectMethod(stateInBattle.onAvatarReceiveBattleResults),))


class _PointcutComputePiercingPowerAtDist(aop.Pointcut):
    """ Tweaks piercing indicator behavior when targeting enemy vehicle:
        if piercing power is overridden (server-side) for current bootcamp battle,
        then client-side calculations of piercing power based on the distance are skipped.
    """

    def __init__(self):
        super(_PointcutComputePiercingPowerAtDist, self).__init__('AvatarInputHandler', 'gun_marker_ctrl', '_computePiercingPowerAtDistImpl', aspects=(_AspectComputePiercingPowerAtDist,))


class _PointcutComputePiercingPowerRandomization(aop.Pointcut):
    """ Tweaks piercing indicator behavior when targeting enemy vehicle:
        if piercing power is overridden (server-side) for current bootcamp battle,
        then client-side randomization of piercing power is skipped.
    """

    def __init__(self):
        super(_PointcutComputePiercingPowerRandomization, self).__init__('AvatarInputHandler', 'gun_marker_ctrl', '_computePiercingPowerRandomizationImpl', aspects=(_AspectComputePiercingPowerRandomization,))


class _PointcutKeepArenaSoundsPlayingOnResultScreen(aop.Pointcut):
    """ Disables SoundGroups.enableArenaSounds(False) call from Avatar.onBecomeNonPlayer,
        which sets volume of certain sound categories to 0.
        This is necessary to make sure that some longer sfx will finish properly
        after being delayed by bootcamp logic (see WOTD-89629).
        It will also keep proper volume of all sounds on result screen.
    """

    def __init__(self):
        super(_PointcutKeepArenaSoundsPlayingOnResultScreen, self).__init__('SoundGroups', 'SoundGroups', 'enableArenaSounds', aspects=(_AspectKeepArenaSoundsPlayingOnResultScreen,))


class _AspectComputePiercingPowerAtDist(aop.Aspect):
    """ Aspect for _PointcutComputePiercingPowerAtDist implementation. """

    def atCall(self, cd):
        from bootcamp.Bootcamp import g_bootcamp
        bootcampPP = g_bootcamp.getPredefinedPiercingPower()
        if bootcampPP:
            cd.avoid()
            piercingPower = bootcampPP['data'][0][1]
            return piercingPower


class _AspectComputePiercingPowerRandomization(aop.Aspect):
    """ Aspect for _PointcutComputePiercingPowerRandomization implementation. """

    def atCall(self, cd):
        from bootcamp.Bootcamp import g_bootcamp
        if g_bootcamp.getPredefinedPiercingPower():
            cd.avoid()
            return (100.0, 100.0)


class _AspectKeepArenaSoundsPlayingOnResultScreen(aop.Aspect):
    """ Aspect for _PointcutKeepArenaSoundsPlayingOnResultScreen implementation. """

    def atCall(self, cd):
        enable = cd.findArg(0, 'enable')
        if not enable:
            cd.avoid()
