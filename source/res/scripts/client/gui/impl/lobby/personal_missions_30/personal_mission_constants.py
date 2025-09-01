# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/personal_missions_30/personal_mission_constants.py
from enum import Enum
from typing import TYPE_CHECKING
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.personal_missions_30.common.enums import MissionCategory
from gui.impl.gen.view_models.views.lobby.personal_missions_30.main_view_reward_model import RewardsType
from gui.impl.gen.view_models.views.lobby.personal_missions_30.rewards_view_model import RewardsViewType
from shared_utils import CONST_CONTAINER
from sound_gui_manager import CommonSoundSpaceSettings
if TYPE_CHECKING:
    from typing import Optional, Set
PM3_CAMPAIGN_ID = 3
MAX_DETAIL_ID = 15
CAMERA_IMMEDIATE_TRANSITION_DURATION = 0.0
MAX_DAILY_QUESTS_PM_POINTS = 25
MAX_NEWBIE_DAILY_QUESTS_PM_POINTS = 15
MISSIONS_ROLES_TO_CATEGORIES = {'Assault': MissionCategory.ASSAULT,
 'Sniper': MissionCategory.SNIPER,
 'Support': MissionCategory.SUPPORT}
REWARDS_VIEW_TYPES = {'vehicleDetail': RewardsViewType.VEHICLE_PART,
 'operationWithHonor': RewardsViewType.OPERATION_WITH_HONORS,
 'campaignWithHonor': RewardsViewType.CAMPAIGN_WITH_HONORS,
 'operation': RewardsViewType.OPERATION}
REWARD_CLASSES = {RewardsType.MAIN: 'operation',
 RewardsType.CAMPAIGN: 'campaign',
 RewardsType.OPERATION: 'honor'}

class IntroKeys(Enum):
    MAIN_INTRO_VIEW = 'INTRO'
    OPERATION_INTRO_VIEW = 'INTRO_OP_%s'


class OperationIDs(int, Enum):
    OPERATION_FIRST = 8
    OPERATION_SECOND = 9
    OPERATION_THIRD = 10


class CameraNameTemplates(str, Enum):
    STAGE = 'operation_{}_stage_{}'
    TOP = 'operation_{}_camera_top_{}'
    FREE = 'operation_{}_camera_free'


class TopCameras(int, Enum):
    FIRST = 1
    SECOND = 2


class StageAdditions(str, Enum):
    CAPE = 'cape'
    SUPPORT = 'support'


class AssemblingType(str, Enum):
    FADE = 'fade'
    VIDEO = 'video'


class SoundsSpaceKeys(CONST_CONTAINER):
    CAMPAIGN_SELECTOR_SPACE = 'pm_campaign_selector'
    CAMPAIGNS_1_2_SPACE = 'pm_campaigns_1_2'
    CAMPAIGN_3_SPACE = 'pm_campaign_3'


class SoundsStateKeys(CONST_CONTAINER):
    HANGAR_PROGRESSION_STATE = 'STATE_hangar_personal_missions_progression'
    HANGAR_PROGRESSION_ON_STATE = 'STATE_hangar_personal_missions_progression_on'
    HANGAR_PROGRESSION_OFF_STATE = 'STATE_hangar_personal_missions_progression_off'
    HANGAR_PLACE_STATE = 'STATE_hangar_place'
    HANGAR_PLACE_PERSONAL_MISSIONS_STATE = 'STATE_hangar_place_personalMissions'
    PERSONAL_MISSIONS_STATE = 'STATE_hangar_personalMissions'
    CAMPAIGN_SELECTOR_STATE = 'STATE_hangar_personalMissions_00'
    CAMPAIGNS_1_2_STATE = 'STATE_hangar_personalMissions_01'
    CAMPAIGN_3_STATE = 'STATE_hangar_personalMissions_03'


class SoundsKeys(CONST_CONTAINER):
    PLAY_ANIMATION_EVENT = 'pm_operation_%s_stage_%s'
    SWITCH_CAMERA_EVENT = 'hangar_pm_whoosh'
    CAMPAIGN_SELECTOR_ENTER = 'pm_lobby_enter'
    CAMPAIGN_SELECTOR_EXIT = 'pm_lobby_exit'
    CAMPAIGNS_1_2_AMBIENT = 'pm_ambient'
    CAMPAIGNS_1_2_MUSIC = 'pm_music'
    CAMPAIGNS_1_2_EXIT = 'pm_exit'
    CAMPAIGN_3_ENTER = 'pm_03_enter'
    CAMPAIGN_3_EXIT = 'pm_03_exit'
    TO_ASSEMBLING = 'pm_03_tank_enter'
    FROM_ASSEMBLING = 'pm_03_tank_exit'
    VEHICLE_CLICK = 'tank_selection'


PERSONAL_MISSIONS_CAMPAIGN_SELECTOR_SPACE = CommonSoundSpaceSettings(name=SoundsSpaceKeys.CAMPAIGN_SELECTOR_SPACE, entranceStates={SoundsStateKeys.HANGAR_PLACE_STATE: SoundsStateKeys.HANGAR_PLACE_PERSONAL_MISSIONS_STATE,
 SoundsStateKeys.PERSONAL_MISSIONS_STATE: SoundsStateKeys.CAMPAIGN_SELECTOR_STATE}, exitStates={}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent=SoundsKeys.CAMPAIGN_SELECTOR_ENTER, exitEvent=SoundsKeys.CAMPAIGN_SELECTOR_EXIT, parentSpace='')
PERSONAL_MISSIONS_CAMPAIGNS_1_2_SPACE = CommonSoundSpaceSettings(name=SoundsSpaceKeys.CAMPAIGNS_1_2_SPACE, entranceStates={SoundsStateKeys.HANGAR_PLACE_STATE: SoundsStateKeys.HANGAR_PLACE_PERSONAL_MISSIONS_STATE,
 SoundsStateKeys.PERSONAL_MISSIONS_STATE: SoundsStateKeys.CAMPAIGNS_1_2_STATE}, exitStates={SoundsStateKeys.PERSONAL_MISSIONS_STATE: SoundsStateKeys.CAMPAIGN_SELECTOR_STATE}, persistentSounds=(SoundsKeys.CAMPAIGNS_1_2_AMBIENT, SoundsKeys.CAMPAIGNS_1_2_MUSIC), stoppableSounds=(), priorities=(), autoStart=True, enterEvent='', exitEvent=SoundsKeys.CAMPAIGNS_1_2_EXIT, parentSpace='')
PERSONAL_MISSIONS_CAMPAIGN_3_SPACE = CommonSoundSpaceSettings(name=SoundsSpaceKeys.CAMPAIGN_3_SPACE, entranceStates={SoundsStateKeys.HANGAR_PLACE_STATE: SoundsStateKeys.HANGAR_PLACE_PERSONAL_MISSIONS_STATE,
 SoundsStateKeys.PERSONAL_MISSIONS_STATE: SoundsStateKeys.CAMPAIGN_3_STATE}, exitStates={SoundsStateKeys.PERSONAL_MISSIONS_STATE: SoundsStateKeys.CAMPAIGN_SELECTOR_STATE}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent=SoundsKeys.CAMPAIGN_3_ENTER, exitEvent=SoundsKeys.CAMPAIGN_3_EXIT, parentSpace='')

class StageInfo(object):
    __slots__ = ('operationId', 'stageId', 'stages', 'additions', '__assemblingType')

    def __init__(self, operationId, stageId, stages=None, additions=None):
        self.operationId = operationId
        self.stageId = stageId
        self.stages = stages or set()
        self.additions = additions or set()
        self.__assemblingType = None
        return

    @property
    def assemblingType(self):
        if not self.__assemblingType:
            self.__assemblingType = self.__getAssemblingType()
        return self.__assemblingType

    def __getAssemblingType(self):
        if self.stageId == 0:
            return None
        else:
            return AssemblingType.VIDEO if self.__getVideoPath().exists() else AssemblingType.FADE

    def __getVideoPath(self):
        rootPath = R.videos.personal_missions_30
        return rootPath.rewards_screen.dyn('operation_{}_intro'.format(self.operationId)) if self.stageId == MAX_DETAIL_ID else rootPath.assembling_screen.dyn('operation_{}_stage_{}'.format(self.operationId, self.stageId))


_STAGES_CONFIG_DATA = {OperationIDs.OPERATION_FIRST: {0: (set(range(0, 1)), {StageAdditions.SUPPORT}),
                                1: (set(range(0, 2)), {StageAdditions.SUPPORT}),
                                2: (set(range(0, 3)), {StageAdditions.SUPPORT}),
                                3: (set(range(0, 4)), {StageAdditions.SUPPORT}),
                                4: (set(range(0, 5)), {StageAdditions.SUPPORT}),
                                5: (set(range(0, 6)), {StageAdditions.SUPPORT}),
                                6: (set(range(0, 7)), {StageAdditions.SUPPORT}),
                                7: (set(range(7, 8)), {StageAdditions.SUPPORT}),
                                8: (set(range(7, 9)), {StageAdditions.SUPPORT}),
                                9: (set(range(7, 10)), {StageAdditions.SUPPORT}),
                                10: (set(range(7, 11)), {StageAdditions.SUPPORT}),
                                11: (set(range(7, 12)), {StageAdditions.SUPPORT}),
                                12: (set(range(7, 13)), {StageAdditions.SUPPORT}),
                                13: (set(range(7, 14)), {StageAdditions.SUPPORT}),
                                14: (set(range(7, 15)), {StageAdditions.SUPPORT}),
                                15: (set(range(7, 16)), set())},
 OperationIDs.OPERATION_SECOND: {0: (set(range(0, 1)), {StageAdditions.CAPE, StageAdditions.SUPPORT}),
                                 1: (set(range(0, 2)), {StageAdditions.SUPPORT}),
                                 2: (set(range(0, 3)), {StageAdditions.SUPPORT}),
                                 3: (set(range(0, 4)), {StageAdditions.SUPPORT}),
                                 4: (set(range(0, 5)), {StageAdditions.SUPPORT}),
                                 5: (set(range(0, 6)), {StageAdditions.SUPPORT}),
                                 6: (set(range(0, 7)), {StageAdditions.SUPPORT}),
                                 7: (set(range(0, 8)), {StageAdditions.SUPPORT}),
                                 8: (set(range(0, 9)), {StageAdditions.SUPPORT}),
                                 9: (set(range(0, 10)), {StageAdditions.SUPPORT}),
                                 10: (set(range(10, 11)), {StageAdditions.SUPPORT}),
                                 11: (set(range(10, 12)), {StageAdditions.SUPPORT}),
                                 12: (set(range(10, 13)), {StageAdditions.SUPPORT}),
                                 13: (set(range(10, 14)), {StageAdditions.SUPPORT}),
                                 14: (set(range(10, 15)), {StageAdditions.SUPPORT}),
                                 15: (set(range(10, 16)), set())},
 OperationIDs.OPERATION_THIRD: {0: (set(range(0, 1)), {StageAdditions.CAPE, StageAdditions.SUPPORT}),
                                1: (set(range(0, 2)), {StageAdditions.SUPPORT}),
                                2: (set(range(0, 3)), {StageAdditions.SUPPORT}),
                                3: (set(range(0, 4)), {StageAdditions.SUPPORT}),
                                4: (set(range(0, 5)), {StageAdditions.SUPPORT}),
                                5: (set(range(0, 6)), {StageAdditions.SUPPORT}),
                                6: (set(range(0, 7)), {StageAdditions.SUPPORT}),
                                7: (set(range(0, 8)), {StageAdditions.SUPPORT}),
                                8: (set(range(0, 9)), {StageAdditions.SUPPORT}),
                                9: (set(range(0, 10)), {StageAdditions.SUPPORT}),
                                10: (set(range(0, 11)), {StageAdditions.SUPPORT}),
                                11: (set(range(11, 12)), {StageAdditions.SUPPORT}),
                                12: (set(range(11, 13)), {StageAdditions.SUPPORT}),
                                13: (set(range(11, 14)), {StageAdditions.SUPPORT}),
                                14: (set(range(11, 15)), {StageAdditions.SUPPORT}),
                                15: (set(range(11, 16)), set())}}
STAGES_CONFIG = {operationId:{stageNumber:StageInfo(operationId, stageNumber, stages=stageData[0], additions=stageData[1]) for stageNumber, stageData in operationStages.items()} for operationId, operationStages in _STAGES_CONFIG_DATA.items()}
