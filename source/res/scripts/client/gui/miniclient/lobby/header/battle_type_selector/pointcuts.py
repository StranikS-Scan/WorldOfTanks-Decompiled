# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/miniclient/lobby/header/battle_type_selector/pointcuts.py
from helpers import aop
import aspects

class _BattleItemSelector(aop.Pointcut):

    def __init__(self, battleTypeBuilderMethod, aspects_):
        aop.Pointcut.__init__(self, 'gui.Scaleform.daapi.view.lobby.header', 'battle_selector_items', battleTypeBuilderMethod, aspects=aspects_)


class RankedBattle(_BattleItemSelector):

    def __init__(self):
        _BattleItemSelector.__init__(self, '_addRankedBattleType', (aspects.RankedBattle,))


class CommandBattle(_BattleItemSelector):

    def __init__(self):
        _BattleItemSelector.__init__(self, '_addCommandBattleType', (aspects.CommandBattle,))


class TrainingBattle(_BattleItemSelector):

    def __init__(self):
        _BattleItemSelector.__init__(self, '_addTrainingBattleType', (aspects.TrainingBattle,))


class SpecialBattle(_BattleItemSelector):

    def __init__(self):
        _BattleItemSelector.__init__(self, '_addSpecialBattleType', (aspects.SpecialBattle,))


class FalloutBattle(_BattleItemSelector):

    def __init__(self):
        _BattleItemSelector.__init__(self, '_addFalloutBattleType', (aspects.FalloutBattle,))


class StrongholdBattle(_BattleItemSelector):

    def __init__(self):
        _BattleItemSelector.__init__(self, '_addStrongholdsBattleType', (aspects.StrongholdBattle,))


class OnBattleTypeSelectorPopulate(aop.Pointcut):

    def __init__(self):
        aop.Pointcut.__init__(self, 'gui.Scaleform.daapi.view.lobby.header.BattleTypeSelectPopover', 'BattleTypeSelectPopover', '_populate', aspects=(aspects.OnBattleTypeSelectorPopulate,))
