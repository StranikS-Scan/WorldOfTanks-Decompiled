# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/personal_missions/task_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class TaskType(Enum):
    VALUEPROGRESS = 'valueProgress'
    BINARYPROGRESS = 'binaryProgress'
    COUNTERPROGRESS = 'counterProgress'
    BIATHLONPROGRESS = 'biathlonProgress'


class HeaderType(Enum):
    LIMITED = 'limited'
    BIATHLON = 'biathlon'
    SERIES = 'series'
    COUNTER = 'counter'


class iconType(Enum):
    ASSIST = 'assist'
    ASSISTRADIO = 'assist_radio'
    ASSISTTRACK = 'assist_track'
    ASSISTSTUN = 'assist_stun'
    ASSISTSTUNTIME = 'assist_stun_time'
    ASSISTSTUNMULTI = 'assist_stun_multi'
    AWARD = 'award'
    BASECAPTURE = 'base_capture'
    BASEDEF = 'base_def'
    CREDITS = 'credits'
    DAMAGE = 'damage'
    DAMAGEBLOCK = 'damage_block'
    DISCOVER = 'discover'
    EXPERIENCE = 'experience'
    FIRE = 'fire'
    GETDAMAGE = 'get_damage'
    GETHIT = 'get_hit'
    HIT = 'hit'
    HURT1SHOT = 'hurt_1shot'
    HURTVEHICLES = 'hurt_vehicles'
    KILL1SHOT = 'kill_1shot'
    KILLVEHICLES = 'kill_vehicles'
    MASTER = 'master'
    METERS = 'meters'
    MODULECRIT = 'module_crit'
    PREPARATION = 'preparation'
    SAVEHP = 'save_hp'
    SECALIVE = 'sec_alive'
    SURVIVE = 'survive'
    TIMESGETDAMAGE = 'times_get_damage'
    TOP = 'top'
    WIN = 'win'
    FOLDER = 'folder'
    BARRELMARK = 'barrel_mark'
    RAM = 'ram'
    MAINREPEAT = 'main_repeat'
    IMPROVE = 'improve'
    RANKUP = 'rank_up'
    PRESTIGEPOINTS = 'prestige_points'


class TaskModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(TaskModel, self).__init__(properties=properties, commands=commands)

    def getTaskType(self):
        return TaskType(self._getString(0))

    def setTaskType(self, value):
        self._setString(0, value.value)

    def getIcon(self):
        return iconType(self._getString(1))

    def setIcon(self, value):
        self._setString(1, value.value)

    def getHeaderType(self):
        return HeaderType(self._getString(2))

    def setHeaderType(self, value):
        self._setString(2, value.value)

    def getIsMain(self):
        return self._getBool(3)

    def setIsMain(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(TaskModel, self)._initialize()
        self._addStringProperty('taskType')
        self._addStringProperty('icon')
        self._addStringProperty('headerType')
        self._addBoolProperty('isMain', False)
