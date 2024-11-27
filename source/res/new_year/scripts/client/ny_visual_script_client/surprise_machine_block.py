# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/ny_visual_script_client/surprise_machine_block.py
from constants import IS_VS_EDITOR
from visual_script import ASPECT
from visual_script.block import Block, Meta
from visual_script.dependency import dependencyImporter
from visual_script.slot_types import SLOT_TYPE
dependency, newYearSkeletons, nyCurrencyn, nyCurrencyProvider = dependencyImporter('helpers.dependency', 'new_year.skeletons.new_year', 'new_year.gui.impl.gen.view_models.common.ny_currency_type_model', 'new_year.gui.shared.ny_currency_provider')

class NewYearExtMeta(Meta):

    @classmethod
    def blockColor(cls):
        pass

    @classmethod
    def blockCategory(cls):
        pass

    @classmethod
    def blockIcon(cls):
        pass


class GiftMachineButtonPress(Block, NewYearExtMeta):
    __nySurpriseMachineCtrl = dependency.descriptor(newYearSkeletons.INewYearSurpriseMachine) if not IS_VS_EDITOR else None

    def __init__(self, *args, **kwargs):
        super(GiftMachineButtonPress, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self._execute)
        self._out = self._makeEventOutputSlot('out')

    def _execute(self):
        self.__nySurpriseMachineCtrl.onMachineButtonPress()
        self._out.call()

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT, ASPECT.HANGAR]


class OnGiftMachineButtonPressStateChange(Block, NewYearExtMeta):
    __nySurpriseMachineCtrl = dependency.descriptor(newYearSkeletons.INewYearSurpriseMachine) if not IS_VS_EDITOR else None

    def __init__(self, *args, **kwargs):
        super(OnGiftMachineButtonPressStateChange, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self._exec)
        self._out = self._makeEventOutputSlot('out')
        self._canButtonPress = self._makeDataOutputSlot('canButtonPress', SLOT_TYPE.BOOL, None)
        return

    def onStartScript(self):
        self.__nySurpriseMachineCtrl.onUpdateApplyCoin += self.__onButtonStateChanged

    def onFinishScript(self):
        self.__nySurpriseMachineCtrl.onUpdateApplyCoin -= self.__onButtonStateChanged

    def _exec(self):
        self._canButtonPress.setValue(self.__nySurpriseMachineCtrl.canApplyCoin)
        self._out.call()

    def __onButtonStateChanged(self):
        self._exec()

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT, ASPECT.HANGAR]


class OnGiftMachineApplyCoinState(Block, NewYearExtMeta):

    def __init__(self, *args, **kwargs):
        super(OnGiftMachineApplyCoinState, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self._exec)
        self._out = self._makeEventOutputSlot('out')
        self._canApplyCoin = self._makeDataOutputSlot('canApplyCoin', SLOT_TYPE.BOOL, None)
        self.__currencyProvider = nyCurrencyProvider.NyCurrencyProvider() if not IS_VS_EDITOR else None
        return

    def onStartScript(self):
        self.__currencyProvider.initialize()
        self.__currencyProvider.onCurrencyUpdated += self.__onCurrencyUpdated

    def onFinishScript(self):
        self.__currencyProvider.onCurrencyUpdated -= self.__onCurrencyUpdated
        self.__currencyProvider.finalize()

    def _exec(self):
        canApplyCoin = self.__currencyProvider.getCurrencyCount(nyCurrencyn.NyCurrencyType.NYGIFTMACHINETOKEN) > 0
        self._canApplyCoin.setValue(canApplyCoin)
        self._out.call()

    def __onCurrencyUpdated(self, cyrrency, diff):
        if cyrrency == nyCurrencyn.NyCurrencyType.NYGIFTMACHINETOKEN:
            self._exec()

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT, ASPECT.HANGAR]


class GiftMachineButtonHovered(Block, NewYearExtMeta):
    __nySurpriseMachineCtrl = dependency.descriptor(newYearSkeletons.INewYearSurpriseMachine) if not IS_VS_EDITOR else None

    def __init__(self, *args, **kwargs):
        super(GiftMachineButtonHovered, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self._execute)
        self._out = self._makeEventOutputSlot('out')
        self._isHovered = self._makeDataInputSlot('isHovered', SLOT_TYPE.BOOL)

    def _execute(self):
        self.__nySurpriseMachineCtrl.onMachineButtonHovered(self._isHovered.getValue())
        self._out.call()

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT, ASPECT.HANGAR]
