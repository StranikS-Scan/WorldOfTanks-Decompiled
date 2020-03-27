# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/SoundEffectsId.py
from shared_utils import CONST_CONTAINER

class SoundEffectsId(CONST_CONTAINER):
    SPEND_DEFAULT_SOUND = 'wwspend_default_currency'
    SPEND_CREDITS_GOLD = 'wwspend_credits_and_gold'
    SPEND_CREDITS = 'wwspend_credits'
    SPEND_GOLD = 'wwspend_gold'
    SPEND_CRYSTAL = 'wwspend_crystal'
    SPEND_EVENT_COIN = 'wwspend_event_coin'
    EARN_DEFAULT_SOUND = 'wwearn_default_currency'
    EARN_CREDITS_GOLD = 'wwearn_credits_and_gold'
    EARN_CREDITS = 'wwearn_credits'
    EARN_GOLD = 'wwearn_gold'
    EARN_CRYSTAL = 'wwearn_crystal'
    EARN_EVENT_COIN = 'wwearn_event_coin'
    TRANSPORT_ENTER = 'wwtransport_enter'
    TRANSPORT_EXIT = 'wwtransport_exit'
    TRANSPORT_FIRST_STEP = 'wwtransport_first_step'
    TRANSPORT_NEXT_STEP = 'wwtransport_next_step'
    TRANSPORT_APPROVE = 'wwtransport_approve'
    ACTIVATE_REQUISITION = 'wwactivate_requisition'
    ACTIVATE_EVACUATION = 'wwactivate_evacuation'
    ACTIVATE_HEAVY_TRUCKS = 'wwactivate_heavyTrucks'
    ACTIVATE_MILITARY_MANEUVERS = 'wwactivate_militaryManeuvers'
    ACTIVATE_ADDITIONAL_BRIEFING = 'wwactivate_additionalBriefing'
    ACTIVATE_TACTICAL_TRAINING = 'wwactivate_tacticalTraining'
    ACTIVATE_BATTLE_PAYMENTS = 'wwactivate_battlePayments'
    ACTIVATE_SPECIALMISSION = 'wwactivate_specialMission'
    END_BUILDING_PROCESS_POSTFIX = '_endPrcBld'
    ACTIVATE_DEFENCE_PERIOD = 'wwactivate_defencePeriod'
    DEACTIVATE_DEFENCE_PERIOD = 'wwdeactivate_defencePeriod'
    ENEMY_DIRECTION_SELECTED = 'wwenemyDirection_selected'
    ENEMY_DIRECTION_HOVER = 'wwenemyDirection_hover'
    MY_DIRECTION_SELECTED = 'wwmyDirection_selected'
    FORT_CLAN_WAR_DECLARED = 'wwfortClanWar_declared'
    BATTLE_ROOM_TIMER_ALERT = 'wwbattleRoom_timerAlert'
    _FORT_CLAN_WAR_RESULT_PREFIX = 'wwfortClanWarResult_'
    CS_ANIMATION_LEAGUE_UP = 'wwcs_animation_league_up'
    CS_ANIMATION_LEAGUE_DOWN = 'wwcs_animation_league_down'
    CS_ANIMATION_DIVISION_UP = 'wwcs_animation_division_up'
    CS_ANIMATION_DIVISION_UP_ALT = 'wwcs_animation_division_up_alt'
    CS_ANIMATION_DIVISION_DOWN = 'wwcs_animation_division_down'
    DYN_SQUAD_STARTING_DYNAMIC_PLATOON = 'wwdyn_squad_starting_dynamic_platoon'
    SELECT_RADIAL_BUTTON = 'wwselect_radial_button'
    RUDY_DOG = 'wwrody_dog'

    @classmethod
    def getEndBuildingProcess(cls, buildingID):
        result = 'ww%s%s' % (buildingID, cls.END_BUILDING_PROCESS_POSTFIX)
        return result

    @classmethod
    def getFortClanWarResult(cls, battleResult):
        result = '%s%s' % (cls._FORT_CLAN_WAR_RESULT_PREFIX, battleResult)
        return result
