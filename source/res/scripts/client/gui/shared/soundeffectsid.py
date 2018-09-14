# Embedded file name: scripts/client/gui/shared/SoundEffectsId.py
from debug_utils import LOG_DEBUG
import FMOD

class SoundEffectsId(object):
    if FMOD.enabled:
        SPEND_CREDITS_GOLD = 'spend_credits_and_gold'
        SPEND_CREDITS = 'spend_credits'
        SPEND_GOLD = 'spend_gold'
        EARN_CREDITS_GOLD = 'earn_credits_and_gold'
        EARN_CREDITS = 'earn_credits'
        EARN_GOLD = 'earn_gold'
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
        ACTIVATE_SPECIALMISSION = 'activate_specialMission'
        END_BUILDING_PROCESS_POSTFIX = '_endPrcBld'
        ACTIVATE_DEFENCE_PERIOD = 'activate_defencePeriod'
        DEACTIVATE_DEFENCE_PERIOD = 'deactivate_defencePeriod'
        ENEMY_DIRECTION_SELECTED = 'enemyDirection_selected'
        ENEMY_DIRECTION_HOVER = 'enemyDirection_hover'
        MY_DIRECTION_SELECTED = 'myDirection_selected'
        FORT_CLAN_WAR_DECLARED = 'fortClanWar_declared'
        BATTLE_ROOM_TIMER_ALERT = 'battleRoom_timerAlert'
        FORT_CLAN_WAR_RESULT_WIN = 'fortClanWarResult_win'
        FORT_CLAN_WAR_RESULT_LOSE = 'fortClanWarResult_lose'
        FORT_CLAN_WAR_RESULT_DRAW = 'fortClanWarResult_draw'
        CS_ANIMATION_LEAGUE_UP = 'cs_animation_league_up'
        CS_ANIMATION_LEAGUE_DOWN = 'cs_animation_league_down'
        CS_ANIMATION_DIVISION_UP = 'cs_animation_division_up'
        CS_ANIMATION_DIVISION_UP_ALT = 'cs_animation_division_up_alt'
        CS_ANIMATION_DIVISION_DOWN = 'cs_animation_division_down'
        DYN_SQUAD_STARTING_DYNAMIC_PLATOON = 'dyn_squad_starting_dynamic_platoon'
        RUDY_DOG = 'rody_dog'

    @classmethod
    def getEndBuildingProcess(cls, buildingID):
        if FMOD.enabled:
            result = buildingID + cls.END_BUILDING_PROCESS_POSTFIX
        return result
