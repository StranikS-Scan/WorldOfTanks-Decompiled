# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch_progression/scripts/client/grinch_progression/visual_script_client/grinch_progression_blocks.py
from visual_script import ASPECT
from visual_script.block import Meta, Block
from visual_script.dependency import dependencyImporter
from visual_script.slot_types import SLOT_TYPE
dependency, grinch_skeletons_battle_controller, grinch_skeletons_progression_controller, newYearSkeletons, periodic_battles_models = dependencyImporter('helpers.dependency', 'grinch.skeletons.battle_controller', 'grinch_progression.skeletons.game_controller', 'skeletons.new_year', 'gui.periodic_battles.models')

class GrinchProgressionMeta(Meta):

    @classmethod
    def blockColor(cls):
        pass

    @classmethod
    def blockCategory(cls):
        pass

    @classmethod
    def blockIcon(cls):
        pass

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT, ASPECT.HANGAR]


class SelectGrinchBattle(Block, GrinchProgressionMeta):
    __grinchCtrl = dependency.descriptor(grinch_skeletons_battle_controller.IGrinchController)

    def __init__(self, *args, **kwargs):
        super(SelectGrinchBattle, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self._execute)
        self._out = self._makeEventOutputSlot('out')

    def _execute(self):
        self.__grinchCtrl.selectMode()
        self._out.call()


class GetGrinchState(Block, GrinchProgressionMeta):
    __grinchCtrl = dependency.descriptor(grinch_skeletons_battle_controller.IGrinchController)
    __nyController = dependency.descriptor(newYearSkeletons.INewYearController)

    def __init__(self, *args, **kwargs):
        super(GetGrinchState, self).__init__(*args, **kwargs)
        self._isAvailable = self._makeDataOutputSlot('isAvailable', SLOT_TYPE.BOOL, self._execute)

    def _execute(self):
        isBeforeSeason = self.__grinchCtrl.getPeriodInfo().periodType == periodic_battles_models.PeriodType.BEFORE_SEASON
        isGrinchDisabled = not self.__grinchCtrl.isEnabled()
        isSuspended = self.__nyController.isSuspended()
        self._isAvailable.setValue(not (isBeforeSeason or isGrinchDisabled or isSuspended))


class OnGrinchStateChanged(Block, GrinchProgressionMeta):
    __grinchCtrl = dependency.descriptor(grinch_skeletons_battle_controller.IGrinchController)
    __nyController = dependency.descriptor(newYearSkeletons.INewYearController)
    __grinchPrgrnCtrl = dependency.descriptor(grinch_skeletons_progression_controller.IGrinchProgressionController)

    def __init__(self, *args, **kwargs):
        super(OnGrinchStateChanged, self).__init__(*args, **kwargs)
        self._out = self._makeEventOutputSlot('out')
        self._isAvailable = self._makeDataOutputSlot('isAvailable', SLOT_TYPE.BOOL, None)
        return

    def onStartScript(self):
        self.__grinchCtrl.onPrimeTimeStatusUpdated += self.update
        self.__grinchCtrl.onConfigChanged += self.update
        self.__grinchPrgrnCtrl.onDataUpdated += self.update
        self.__nyController.onStateChanged += self.update

    def onFinishScript(self):
        self.__grinchCtrl.onPrimeTimeStatusUpdated -= self.update
        self.__grinchCtrl.onConfigChanged -= self.update
        self.__grinchPrgrnCtrl.onDataUpdated -= self.update
        self.__nyController.onStateChanged -= self.update

    def update(self, *_):
        isBeforeSeason = self.__grinchCtrl.getPeriodInfo().periodType == periodic_battles_models.PeriodType.BEFORE_SEASON
        isGrinchDisabled = not self.__grinchCtrl.isEnabled()
        isSuspended = self.__nyController.isSuspended()
        self._isAvailable.setValue(not (isBeforeSeason or isGrinchDisabled or isSuspended))
        self._out.call()
