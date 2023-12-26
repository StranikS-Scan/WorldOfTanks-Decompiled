# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/glade/ny_glade_view_model.py
from enum import Enum
from gui.impl.gen.view_models.views.lobby.lootboxes.reward_kit_entry_point_model import RewardKitEntryPointModel
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_toy_slots_bar_model import NyToySlotsBarModel
from gui.impl.gen.view_models.views.lobby.new_year.views.base.ny_scene_rotatable_view import NySceneRotatableView
from gui.impl.gen.view_models.views.lobby.new_year.views.glade.customization_levelup_model import CustomizationLevelupModel
from gui.impl.gen.view_models.views.lobby.new_year.views.glade.ny_intro_model import NyIntroModel
from gui.impl.gen.view_models.views.lobby.new_year.views.glade.ny_max_level_rewards_model import NyMaxLevelRewardsModel
from gui.impl.gen.view_models.views.lobby.new_year.views.glade.ny_resource_collector_model import NyResourceCollectorModel

class ContentState(Enum):
    RESOURCES = 'Resources'
    TOYSLOTS = 'ToySlots'
    ALLTOWN = 'AllTown'
    MAXLEVELREWARD = 'MaxLevelReward'


class InfoState(Enum):
    TUTORIAL = 'Tutorial'
    DEFAULTHANGAR = 'DefaultHangar'
    MAXLEVEL = 'MaxLevel'
    DEFAULT = 'Default'


class AnimationLevelUpStates(Enum):
    IDLE = 'idle'
    PENDING = 'Pending'
    CUSTOMIZATION = 'customization'
    WIDGET = 'widget'
    MAXLEVEL = 'maxLevel'


class NyGladeViewModel(NySceneRotatableView):
    __slots__ = ('onNextTutorialState', 'onSetTutorialState', 'onMaxLevelMessageClosed', 'onUpdateContentModel')

    def __init__(self, properties=16, commands=6):
        super(NyGladeViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def resourceCollector(self):
        return self._getViewModel(1)

    @staticmethod
    def getResourceCollectorType():
        return NyResourceCollectorModel

    @property
    def toySlotsBar(self):
        return self._getViewModel(2)

    @staticmethod
    def getToySlotsBarType():
        return NyToySlotsBarModel

    @property
    def rewardKit(self):
        return self._getViewModel(3)

    @staticmethod
    def getRewardKitType():
        return RewardKitEntryPointModel

    @property
    def intro(self):
        return self._getViewModel(4)

    @staticmethod
    def getIntroType():
        return NyIntroModel

    @property
    def customizationLevelUp(self):
        return self._getViewModel(5)

    @staticmethod
    def getCustomizationLevelUpType():
        return CustomizationLevelupModel

    @property
    def maxLevelReward(self):
        return self._getViewModel(6)

    @staticmethod
    def getMaxLevelRewardType():
        return NyMaxLevelRewardsModel

    def getIsIntroOpened(self):
        return self._getBool(7)

    def setIsIntroOpened(self, value):
        self._setBool(7, value)

    def getTabName(self):
        return self._getString(8)

    def setTabName(self, value):
        self._setString(8, value)

    def getIsTabSwitching(self):
        return self._getBool(9)

    def setIsTabSwitching(self, value):
        self._setBool(9, value)

    def getIsShowLevelUp(self):
        return self._getBool(10)

    def setIsShowLevelUp(self, value):
        self._setBool(10, value)

    def getIsMaxLevelMessageClosed(self):
        return self._getBool(11)

    def setIsMaxLevelMessageClosed(self, value):
        self._setBool(11, value)

    def getShowCustomizationObjectTooltip(self):
        return self._getBool(12)

    def setShowCustomizationObjectTooltip(self, value):
        self._setBool(12, value)

    def getIsConverterOpened(self):
        return self._getBool(13)

    def setIsConverterOpened(self, value):
        self._setBool(13, value)

    def getAnimationLevelUpState(self):
        return AnimationLevelUpStates(self._getString(14))

    def setAnimationLevelUpState(self, value):
        self._setString(14, value.value)

    def getHasChangedViewAnimation(self):
        return self._getBool(15)

    def setHasChangedViewAnimation(self, value):
        self._setBool(15, value)

    def _initialize(self):
        super(NyGladeViewModel, self)._initialize()
        self._addViewModelProperty('resourceCollector', NyResourceCollectorModel())
        self._addViewModelProperty('toySlotsBar', NyToySlotsBarModel())
        self._addViewModelProperty('rewardKit', RewardKitEntryPointModel())
        self._addViewModelProperty('intro', NyIntroModel())
        self._addViewModelProperty('customizationLevelUp', CustomizationLevelupModel())
        self._addViewModelProperty('maxLevelReward', NyMaxLevelRewardsModel())
        self._addBoolProperty('isIntroOpened', False)
        self._addStringProperty('tabName', '')
        self._addBoolProperty('isTabSwitching', False)
        self._addBoolProperty('isShowLevelUp', True)
        self._addBoolProperty('isMaxLevelMessageClosed', False)
        self._addBoolProperty('showCustomizationObjectTooltip', False)
        self._addBoolProperty('isConverterOpened', False)
        self._addStringProperty('animationLevelUpState')
        self._addBoolProperty('hasChangedViewAnimation', False)
        self.onNextTutorialState = self._addCommand('onNextTutorialState')
        self.onSetTutorialState = self._addCommand('onSetTutorialState')
        self.onMaxLevelMessageClosed = self._addCommand('onMaxLevelMessageClosed')
        self.onUpdateContentModel = self._addCommand('onUpdateContentModel')
