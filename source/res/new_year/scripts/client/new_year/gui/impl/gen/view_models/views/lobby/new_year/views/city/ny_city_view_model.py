# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/gen/view_models/views/lobby/new_year/views/city/ny_city_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.city.atmosphere_animation_model import AtmosphereAnimationModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.city.group_slots_model import GroupSlotsModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.city.ny_city_marker_model import NyCityMarkerModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.city.object_view_model import ObjectViewModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.city.objects_overview_model import ObjectsOverviewModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.lootboxes.loot_box_entry_point_model import LootBoxEntryPointModel

class NyCityViewModel(ViewModel):
    __slots__ = ('onLevelUp', 'onHoverSlot', 'onHoverOutSlot', 'onHoverMarker', 'onHoverOutMarker', 'onMouseOver3dScene', 'onMoveSpace')
    OBJECTS_OVERVIEW = 0
    OBJECT_VIEW = 1

    def __init__(self, properties=13, commands=7):
        super(NyCityViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def objectsOverview(self):
        return self._getViewModel(0)

    @staticmethod
    def getObjectsOverviewType():
        return ObjectsOverviewModel

    @property
    def objectView(self):
        return self._getViewModel(1)

    @staticmethod
    def getObjectViewType():
        return ObjectViewModel

    @property
    def groupSlots(self):
        return self._getViewModel(2)

    @staticmethod
    def getGroupSlotsType():
        return GroupSlotsModel

    @property
    def lootBox(self):
        return self._getViewModel(3)

    @staticmethod
    def getLootBoxType():
        return LootBoxEntryPointModel

    @property
    def atmosphereAnimation(self):
        return self._getViewModel(4)

    @staticmethod
    def getAtmosphereAnimationType():
        return AtmosphereAnimationModel

    @property
    def firMarker(self):
        return self._getViewModel(5)

    @staticmethod
    def getFirMarkerType():
        return NyCityMarkerModel

    @property
    def lightsMarker(self):
        return self._getViewModel(6)

    @staticmethod
    def getLightsMarkerType():
        return NyCityMarkerModel

    @property
    def installationsMarker(self):
        return self._getViewModel(7)

    @staticmethod
    def getInstallationsMarkerType():
        return NyCityMarkerModel

    @property
    def fairMarker(self):
        return self._getViewModel(8)

    @staticmethod
    def getFairMarkerType():
        return NyCityMarkerModel

    @property
    def skatingMarker(self):
        return self._getViewModel(9)

    @staticmethod
    def getSkatingMarkerType():
        return NyCityMarkerModel

    @property
    def attractionsMarker(self):
        return self._getViewModel(10)

    @staticmethod
    def getAttractionsMarkerType():
        return NyCityMarkerModel

    def getIsGuiLootBoxesVisible(self):
        return self._getBool(11)

    def setIsGuiLootBoxesVisible(self, value):
        self._setBool(11, value)

    def getCurrentSubModel(self):
        return self._getNumber(12)

    def setCurrentSubModel(self, value):
        self._setNumber(12, value)

    def _initialize(self):
        super(NyCityViewModel, self)._initialize()
        self._addViewModelProperty('objectsOverview', ObjectsOverviewModel())
        self._addViewModelProperty('objectView', ObjectViewModel())
        self._addViewModelProperty('groupSlots', UserListModel())
        self._addViewModelProperty('lootBox', LootBoxEntryPointModel())
        self._addViewModelProperty('atmosphereAnimation', AtmosphereAnimationModel())
        self._addViewModelProperty('firMarker', NyCityMarkerModel())
        self._addViewModelProperty('lightsMarker', NyCityMarkerModel())
        self._addViewModelProperty('installationsMarker', NyCityMarkerModel())
        self._addViewModelProperty('fairMarker', NyCityMarkerModel())
        self._addViewModelProperty('skatingMarker', NyCityMarkerModel())
        self._addViewModelProperty('attractionsMarker', NyCityMarkerModel())
        self._addBoolProperty('isGuiLootBoxesVisible', False)
        self._addNumberProperty('currentSubModel', 0)
        self.onLevelUp = self._addCommand('onLevelUp')
        self.onHoverSlot = self._addCommand('onHoverSlot')
        self.onHoverOutSlot = self._addCommand('onHoverOutSlot')
        self.onHoverMarker = self._addCommand('onHoverMarker')
        self.onHoverOutMarker = self._addCommand('onHoverOutMarker')
        self.onMouseOver3dScene = self._addCommand('onMouseOver3dScene')
        self.onMoveSpace = self._addCommand('onMoveSpace')
