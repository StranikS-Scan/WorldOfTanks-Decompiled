# Embedded file name: scripts/client/gui/shared/SoundEffectsId.py
from debug_utils import LOG_DEBUG

class SoundEffectsId(object):
    SPEND_CREDITS_GOLD = 'spend_credits_and_gold'
    SPEND_CREDITS = 'spend_credits'
    SPEND_GOLD = 'spend_gold'
    EARN_CREDITS_GOLD = 'earn_credits_and_gold'
    EARN_CREDITS = 'earn_credits'
    EARN_GOLD = 'earn_gold'
    TRANSPORT_CONSTRAIN = 'transport_constrain'
    TRANSPORT_ENTER = 'transport_enter'
    TRANSPORT_EXIT = 'transport_exit'
    TRANSPORT_FIRST_STEP = 'transport_first_step'
    TRANSPORT_NEXT_STEP = 'transport_next_step'
    TRANSPORT_APPROVE = 'transport_approve'
    FORT_CREATE = 'fort_create'
    FORT_ENTERED_FOUNDATION_STATE = 'fort_entered_foundation_state'
    FORT_FIXED_IN_BUILDING = 'fort_fixed_in_building'
    FORT_UPGRADE_BUILDING = 'fort_upgrade_building'
    FORT_DEMOUNT_BUILDING = 'fort_demount_building'
    FORT_ORDER_INPROGRESS = 'fort_order_inprogress'
    FORT_ORDER_ISREADY = 'fort_order_isready'
    FORT_DIRECTION_CREATE = 'direction_create'
    FORT_DIRECTION_CLOSE = 'direction_close'
    ACTIVATE_REQUISITION = 'activate_requisition'
    ACTIVATE_EVACUATION = 'activate_evacuation'
    ACTIVATE_HEAVY_TRUCKS = 'activate_heavyTrucks'
    ACTIVATE_MILITARY_MANEUVERS = 'activate_militaryManeuvers'
    ACTIVATE_ADDITIONAL_BRIEFING = 'activate_additionalBriefing'
    ACTIVATE_TACTICAL_TRAINING = 'activate_tacticalTraining'
    ACTIVATE_BATTLE_PAYMENTS = 'activate_battlePayments'
    END_BUILDING_PROCESS_POSTFIX = '_endPrcBld'

    @classmethod
    def getEndBuildingProcess(cls, buildingID):
        result = buildingID + cls.END_BUILDING_PROCESS_POSTFIX
        return result
