# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/quests/quest_flag_manager.py
import typing
from CurrentVehicle import g_currentVehicle
from gui.Scaleform.genConsts.HANGAR_HEADER_QUESTS import HANGAR_HEADER_QUESTS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import icons
from helpers import dependency
from historical_battles.quests.vehicle_quest_info import VehicleQuestInfo
from historical_battles.skeletons.gui.game_event_controller import IGameEventController
from skeletons.gui.shared import IItemsCache

class QuestFlagManager(object):
    __slots__ = ('__itemsCache', '__gameEventController', '__activeIcon', '__disabledIcon', '_headerQuestFormatterVo', '_wrapQuestGroup')
    __itemsCache = dependency.descriptor(IItemsCache)
    __gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self, headerQuestFormatterVo, wrapQuestGroup):
        super(QuestFlagManager, self).__init__()
        self._headerQuestFormatterVo = headerQuestFormatterVo
        self._wrapQuestGroup = wrapQuestGroup
        self.__activeIcon = backport.image(R.images.historical_battles.gui.maps.icons.quests.headerFlagIcons.flag_icon())
        self.__disabledIcon = backport.image(R.images.historical_battles.gui.maps.icons.quests.headerFlagIcons.flag_icon_disabled())

    def __exportQuestData(self, quest):
        vehicle = g_currentVehicle.item
        vehicleQuestInfo = VehicleQuestInfo(vehicle)
        vehicleQuestInfo.init()
        if vehicleQuestInfo.isAnyAvailable() and not vehicleQuestInfo.isAllCompleted():
            self.__setAvailableFlagState(quest, vehicleQuestInfo.getUncompletedCount())
        elif vehicleQuestInfo.isEmptyConfig():
            self.__setMaintenanceFlagState(quest)
        elif vehicleQuestInfo.isAllCompleted():
            self.__setCompletedFlagState(quest)
        else:
            self.__setDisabledFlagState(quest)

    def __setAvailableFlagState(self, quest, questsCount):
        quest['enable'] = True
        quest['label'] = str(questsCount)
        quest['icon'] = self.__activeIcon

    def __setDisabledFlagState(self, quest):
        quest['enable'] = False
        quest['label'] = ''
        quest['icon'] = self.__disabledIcon

    def __setCompletedFlagState(self, quest):
        quest['enable'] = True
        quest['label'] = self.__getCompletedLabel()
        quest['icon'] = self.__activeIcon

    def __setMaintenanceFlagState(self, quest):
        quest['enable'] = True
        quest['label'] = icons.makeImageTag(backport.image(R.images.gui.maps.icons.library.alertIcon()))
        quest['icon'] = self.__activeIcon

    def __getCompletedLabel(self):
        if self.__gameEventController.isLastDay():
            label = icons.makeImageTag(backport.image(R.images.gui.maps.icons.library.outline.quests_all_done()))
        else:
            label = icons.makeImageTag(backport.image(R.images.gui.maps.icons.library.time_icon()))
        return label

    def getWrappedQuestGroup(self):
        if not self.__gameEventController.isEnabled():
            return []
        quest = self._headerQuestFormatterVo(enable=True, icon='', label='', questType=HANGAR_HEADER_QUESTS.QUEST_GROUP_HB_BATTLE, questID=HANGAR_HEADER_QUESTS.QUEST_GROUP_HB_BATTLE, isReward=False, tooltip=TOOLTIPS_CONSTANTS.HB_QUESTS_PREVIEW, flag=backport.image(R.images.gui.maps.icons.library.hangarFlag.flag_red()), flagDisabled=backport.image(R.images.gui.maps.icons.library.hangarFlag.flag_gray()), isTooltipSpecial=True)
        self.__exportQuestData(quest)
        return self._wrapQuestGroup(HANGAR_HEADER_QUESTS.QUEST_GROUP_HB_BATTLE, '', [quest])
