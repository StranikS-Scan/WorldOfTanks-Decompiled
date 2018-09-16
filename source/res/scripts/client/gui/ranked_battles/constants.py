# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/ranked_battles/constants.py


class RANK_TYPES(object):
    ACCOUNT = 'account'
    VEHICLE = 'vehicle'


class SOUND(object):
    RANK_FLICKER = 'gui_rb_rank_flicker'
    STEP_EARNED = 'gui_rb_rank_arrow_up'
    STEP_LOST = 'gui_rb_rank_arrow_down'
    RANK_1_EARNED = 'gui_rb_rank_1'
    RANK_2_EARNED = 'gui_rb_rank_2'
    RANK_3_EARNED = 'gui_rb_rank_3'
    RANK_4_EARNED = 'gui_rb_rank_4'
    RANK_5_EARNED = 'gui_rb_rank_5'
    VEH_RANK_EARNED = 'gui_rb_rank_max'
    RANK_LOST = 'gui_rb_rank_down'
    RANK_EARNED_POST_BATTLE = 'gui_rb_rank_up_postmortem'
    RANK_LOST_POST_BATTLE = 'gui_rb_rank_down_postmortem'
    STEP_EARNED_POST_BATTLE = 'gui_rb_rank_arrow_up_final'
    STEP_LOST_POST_BATTLE = 'gui_rb_rank_arrow_down_final'
    STEP_NOT_CHANGED_POST_BATTLE = 'gui_rb_rank_arrow_up_nothing'
    SEASON_RESULT_ANIMATION_START = 'gui_rb_rank_result'
    SEASON_RESULT_WOOD_BOX_1 = 'gui_rb_rank_wood_box_1'
    SEASON_RESULT_WOOD_BOX_2 = 'gui_rb_rank_wood_box_2'
    SEASON_RESULT_WOOD_BOX_3 = 'gui_rb_rank_wood_box_3'
    SEASON_RESULT_WOOD_BOX_4 = 'gui_rb_rank_wood_box_4'
    SEASON_RESULT_WOOD_BOX_5 = 'gui_rb_rank_wood_box_max'
    SEASON_RESULT_METAL_BOX_1 = 'gui_rb_rank_metal_box_1'
    SEASON_RESULT_METAL_BOX_2 = 'gui_rb_rank_metal_box_2'
    SEASON_RESULT_METAL_BOX_3 = 'gui_rb_rank_metal_box_3'
    SEASON_RESULT_AWARD_ANIMATION = 'gui_rb_rank_reward'
    SEASON_RESULT_BUTTON_ANIMATION = 'gui_rb_rank_exactly'
    ANIMATION_WINDOW_CLOSED = 'gui_rb_rank_Exit_input_animation'
    SHIELD_DAMAGED = 'gui_rb_rank_shield_damage_small'
    SHIELD_LOST = 'gui_rb_rank_shield_break_small'
    SHIELD_HEALED = 'gui_rb_rank_shield_restore_small'
    SHIELD_RECEIVED = 'gui_rb_rank_shield_receive_small'
    POST_BATTLE_SHIELD_DAMAGED = 'gui_rb_rank_shield_damage'
    POST_BATTLE_SHIELD_LOST = 'gui_rb_rank_shield_break'
    POST_BATTLE_SHIELD_HEALED = 'gui_rb_rank_shield_restore'
    POST_BATTLE_SHIELD_RECEIVED = 'gui_rb_rank_shield_receive'

    @staticmethod
    def getRankEarnedEvent(rankID):
        if rankID > 5:
            rankID = 5
        return 'gui_rb_rank_{}'.format(rankID)

    @staticmethod
    def getBoxAnimationEvent(boxType, number):
        if number >= 5:
            number = 'max'
        return 'gui_rb_rank_{}_box_{}'.format(boxType, number)

    @staticmethod
    def getRankAwardAnimationEvent(rankID):
        if rankID > 5:
            rankID = 5
        return 'gui_rb_rank_{}_postmortem'.format(rankID)


RANKED_QUEST_ID_PREFIX = 'ranked'

class PRIME_TIME_STATUS(object):
    DISABLED = 0
    NOT_SET = 1
    FROZEN = 2
    NO_SEASON = 3
    NOT_AVAILABLE = 4
    AVAILABLE = 5
