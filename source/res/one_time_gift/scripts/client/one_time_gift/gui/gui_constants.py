# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: one_time_gift/scripts/client/one_time_gift/gui/gui_constants.py
from constants_utils import ConstInjector
from messenger import m_constants
from shared_utils import CONST_CONTAINER

class SCH_CLIENT_MSG_TYPE(m_constants.SCH_CLIENT_MSG_TYPE, ConstInjector):
    OTG_VEHICLES_RECEIVED = 350
    OTG_ADDITIONAL_REWARDS_RECEIVED = 351
    OTG_COLLECTOR_REWARDS_RECEIVED = 352


class TOOLTIP_CONSTANTS(CONST_CONTAINER):
    ONE_TIME_GIFT_VEHICLE_TOOLTIP = 'oneTimeGiftVehicleTooltip'


ONE_TIME_GIFT_TOOLTIP_SET = (TOOLTIP_CONSTANTS.ONE_TIME_GIFT_VEHICLE_TOOLTIP,)
OTG_LOCK_SOURCE_NAME = 'one_time_gift_logic'
OTG_MISSION_TOKEN_PREFIX = 'one_time_gift_mission:'
OTG_MISSION_TOKEN_BONUS_NAME = 'oneTimeGiftMission'
OTG_EQUIPMENT_SET_BONUS_NAME = 'oneTimeGiftEquipmentSet'
