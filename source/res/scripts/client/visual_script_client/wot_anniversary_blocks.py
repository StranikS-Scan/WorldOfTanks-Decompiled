# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/visual_script_client/wot_anniversary_blocks.py
from visual_script import ASPECT
from visual_script.block import Block, Meta
from visual_script.dependency import dependencyImporter
from visual_script.slot_types import SLOT_TYPE
wot_anniversary, dependency, wot_anniversary_helpers, CurrentVehicle = dependencyImporter('skeletons.gui.wot_anniversary', 'helpers.dependency', 'gui.impl.lobby.wot_anniversary.wot_anniversary_helpers', 'CurrentVehicle')

class WotAnniversaryMeta(Meta):

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


class IsPreviewVehicleOrStyleSelected(Block, WotAnniversaryMeta):

    def __init__(self, *args, **kwargs):
        super(IsPreviewVehicleOrStyleSelected, self).__init__(*args, **kwargs)
        self._isSelected = self._makeDataOutputSlot('isSelected', SLOT_TYPE.BOOL, self.__execute)
        self._onChanged = self._makeEventOutputSlot('out')

    def onStartScript(self):
        CurrentVehicle.g_currentPreviewVehicle.onSelected += self.__onPreviewVehicleSelected
        CurrentVehicle.g_currentPreviewVehicle.onChanged += self.__onPreviewVehicleSelected

    def onFinishScript(self):
        CurrentVehicle.g_currentPreviewVehicle.onSelected -= self.__onPreviewVehicleSelected
        CurrentVehicle.g_currentPreviewVehicle.onChanged -= self.__onPreviewVehicleSelected

    def __execute(self):
        self._isSelected.setValue(CurrentVehicle.g_currentPreviewVehicle.item is not None)
        return

    def __onPreviewVehicleSelected(self):
        self._onChanged.call()


class IsWotAnniversaryEnabled(Block, WotAnniversaryMeta):
    __wotAnniversaryController = dependency.descriptor(wot_anniversary.IWotAnniversaryController)

    def __init__(self, *args, **kwargs):
        super(IsWotAnniversaryEnabled, self).__init__(*args, **kwargs)
        self._isEnabled = self._makeDataOutputSlot('isEnabled', SLOT_TYPE.BOOL, self._execute)
        self._onChanged = self._makeEventOutputSlot('onChanged')

    def _execute(self):
        self._isEnabled.setValue(self.__wotAnniversaryController.isEnabled())

    def onStartScript(self):
        self.__wotAnniversaryController.onSettingsChanged += self._updateValues
        self.__wotAnniversaryController.onStartDateReached += self._updateValues
        self.__wotAnniversaryController.onEndDateReached += self._updateValues

    def onFinishScript(self):
        self.__wotAnniversaryController.onSettingsChanged -= self._updateValues
        self.__wotAnniversaryController.onStartDateReached -= self._updateValues
        self.__wotAnniversaryController.onEndDateReached -= self._updateValues

    def _updateValues(self):
        self._onChanged.call()


class OpenWotAnniversaryMainView(Block, WotAnniversaryMeta):

    def __init__(self, *args, **kwargs):
        super(OpenWotAnniversaryMainView, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self._execute)
        self._out = self._makeEventOutputSlot('out')

    def _execute(self):
        wot_anniversary_helpers.showWotAnniversaryMainView()
        self._out.call()
