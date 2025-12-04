# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/gen/view_models/views/lobby/new_year/views/city/ny_city_view_model.py
from frameworks.wulf import Array
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.components.ny_popover_decoration_slot_model import NyPopoverDecorationSlotModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.city.atmosphere_animation_model import AtmosphereAnimationModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.city.group_slots_model import GroupSlotsModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.city.ny_city_marker_model import NyCityMarkerModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.city.object_view_model import ObjectViewModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.city.objects_overview_model import ObjectsOverviewModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.environment_switcher import EnvironmentSwitcher
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.lootboxes.loot_box_entry_point_model import LootBoxEntryPointModel

class NyCityViewModel(ViewModel):
    __slots__ = ('onLevelUp', 'onHoverSlot', 'onHoverOutSlot', 'onClickSlot', 'onHoverMarker', 'onHoverOutMarker', 'onApplyDecorationSelection', 'onIsNewStateChanged', 'onLevelUpAnimationEnd')
    OBJECTS_OVERVIEW = 0
    OBJECT_VIEW = 1

    def __init__(self, properties=19, commands=9):
        super(NyCityViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def environmentSwitcher(self):
        return self._getViewModel(0)

    @staticmethod
    def getEnvironmentSwitcherType():
        return EnvironmentSwitcher

    @property
    def objectsOverview(self):
        return self._getViewModel(1)

    @staticmethod
    def getObjectsOverviewType():
        return ObjectsOverviewModel

    @property
    def objectView(self):
        return self._getViewModel(2)

    @staticmethod
    def getObjectViewType():
        return ObjectViewModel

    @property
    def groupSlots(self):
        return self._getViewModel(3)

    @staticmethod
    def getGroupSlotsType():
        return GroupSlotsModel

    @property
    def lootBox(self):
        return self._getViewModel(4)

    @staticmethod
    def getLootBoxType():
        return LootBoxEntryPointModel

    @property
    def atmosphereAnimation(self):
        return self._getViewModel(5)

    @staticmethod
    def getAtmosphereAnimationType():
        return AtmosphereAnimationModel

    @property
    def firMarker(self):
        return self._getViewModel(6)

    @staticmethod
    def getFirMarkerType():
        return NyCityMarkerModel

    @property
    def teremMarker(self):
        return self._getViewModel(7)

    @staticmethod
    def getTeremMarkerType():
        return NyCityMarkerModel

    @property
    def installationsMarker(self):
        return self._getViewModel(8)

    @staticmethod
    def getInstallationsMarkerType():
        return NyCityMarkerModel

    @property
    def fairMarker(self):
        return self._getViewModel(9)

    @staticmethod
    def getFairMarkerType():
        return NyCityMarkerModel

    @property
    def snowslideMarker(self):
        return self._getViewModel(10)

    @staticmethod
    def getSnowslideMarkerType():
        return NyCityMarkerModel

    @property
    def fireworksMarker(self):
        return self._getViewModel(11)

    @staticmethod
    def getFireworksMarkerType():
        return NyCityMarkerModel

    def getShowEnvSwitcherTip(self):
        return self._getBool(12)

    def setShowEnvSwitcherTip(self, value):
        self._setBool(12, value)

    def getIsGuiLootBoxesVisible(self):
        return self._getBool(13)

    def setIsGuiLootBoxesVisible(self, value):
        self._setBool(13, value)

    def getCurrentSubModel(self):
        return self._getNumber(14)

    def setCurrentSubModel(self, value):
        self._setNumber(14, value)

    def getCityLvl(self):
        return self._getNumber(15)

    def setCityLvl(self, value):
        self._setNumber(15, value)

    def getIsFirstEntrance(self):
        return self._getBool(16)

    def setIsFirstEntrance(self, value):
        self._setBool(16, value)

    def getDecorationsTitle(self):
        return self._getResource(17)

    def setDecorationsTitle(self, value):
        self._setResource(17, value)

    def getDecorationsSlots(self):
        return self._getArray(18)

    def setDecorationsSlots(self, value):
        self._setArray(18, value)

    @staticmethod
    def getDecorationsSlotsType():
        return NyPopoverDecorationSlotModel

    def _initialize(self):
        super(NyCityViewModel, self)._initialize()
        self._addViewModelProperty('environmentSwitcher', EnvironmentSwitcher())
        self._addViewModelProperty('objectsOverview', ObjectsOverviewModel())
        self._addViewModelProperty('objectView', ObjectViewModel())
        self._addViewModelProperty('groupSlots', UserListModel())
        self._addViewModelProperty('lootBox', LootBoxEntryPointModel())
        self._addViewModelProperty('atmosphereAnimation', AtmosphereAnimationModel())
        self._addViewModelProperty('firMarker', NyCityMarkerModel())
        self._addViewModelProperty('teremMarker', NyCityMarkerModel())
        self._addViewModelProperty('installationsMarker', NyCityMarkerModel())
        self._addViewModelProperty('fairMarker', NyCityMarkerModel())
        self._addViewModelProperty('snowslideMarker', NyCityMarkerModel())
        self._addViewModelProperty('fireworksMarker', NyCityMarkerModel())
        self._addBoolProperty('showEnvSwitcherTip', False)
        self._addBoolProperty('isGuiLootBoxesVisible', False)
        self._addNumberProperty('currentSubModel', 0)
        self._addNumberProperty('cityLvl', 0)
        self._addBoolProperty('isFirstEntrance', False)
        self._addResourceProperty('decorationsTitle', R.invalid())
        self._addArrayProperty('decorationsSlots', Array())
        self.onLevelUp = self._addCommand('onLevelUp')
        self.onHoverSlot = self._addCommand('onHoverSlot')
        self.onHoverOutSlot = self._addCommand('onHoverOutSlot')
        self.onClickSlot = self._addCommand('onClickSlot')
        self.onHoverMarker = self._addCommand('onHoverMarker')
        self.onHoverOutMarker = self._addCommand('onHoverOutMarker')
        self.onApplyDecorationSelection = self._addCommand('onApplyDecorationSelection')
        self.onIsNewStateChanged = self._addCommand('onIsNewStateChanged')
        self.onLevelUpAnimationEnd = self._addCommand('onLevelUpAnimationEnd')
