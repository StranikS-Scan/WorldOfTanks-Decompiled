# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/common/player_satisfaction_rating/randomize_feedback.py
from constants import PlayerSatisfactionRating
from gui.impl import backport
from gui.impl.gen import R
from player_satisfaction_schema import playerSatisfactionSchema
_FEEDBACK_BY_RATING_VARIANT = {PlayerSatisfactionRating.WORSE: [R.strings.player_satisfaction.battle.widget.onDislikeTextOptionOne(),
                                  R.strings.player_satisfaction.battle.widget.onDislikeTextOptionTwo(),
                                  R.strings.player_satisfaction.battle.widget.onDislikeTextOptionThree(),
                                  R.strings.player_satisfaction.battle.widget.onDislikeTextOptionFour(),
                                  R.strings.player_satisfaction.battle.widget.onDislikeTextOptionFive()],
 PlayerSatisfactionRating.BETTER: [R.strings.player_satisfaction.battle.widget.onLikeTextOptionOne(),
                                   R.strings.player_satisfaction.battle.widget.onLikeTextOptionTwo(),
                                   R.strings.player_satisfaction.battle.widget.onLikeTextOptionThree(),
                                   R.strings.player_satisfaction.battle.widget.onLikeTextOptionFour(),
                                   R.strings.player_satisfaction.battle.widget.onLikeTextOptionFive()],
 PlayerSatisfactionRating.USUAL: [R.strings.player_satisfaction.battle.widget.onNeutralText()],
 PlayerSatisfactionRating.NONE: [R.strings.player_satisfaction.battle.widget.baseText()]}
_DEFAULT_FEEDBACK_BY_RATING_VARIANT = {PlayerSatisfactionRating.WORSE: R.strings.player_satisfaction.battle.widget.onDislikeTextOptionThree(),
 PlayerSatisfactionRating.BETTER: R.strings.player_satisfaction.battle.widget.onLikeTextOptionFour(),
 PlayerSatisfactionRating.USUAL: R.strings.player_satisfaction.battle.widget.onNeutralText(),
 PlayerSatisfactionRating.NONE: R.strings.player_satisfaction.battle.widget.baseText()}
SELECTION_ORDER = (PlayerSatisfactionRating.NONE,
 PlayerSatisfactionRating.WORSE,
 PlayerSatisfactionRating.USUAL,
 PlayerSatisfactionRating.BETTER)

def getFeedbackResID(ratingVariant, arenaUniqueID):
    config = playerSatisfactionSchema.getModel()
    if not config.randomizedFeedbackText:
        return _DEFAULT_FEEDBACK_BY_RATING_VARIANT.get(ratingVariant, R.invalid())
    options = _FEEDBACK_BY_RATING_VARIANT.get(ratingVariant, (R.invalid(),))
    numOptions = len(options)
    return options[0] if numOptions == 1 else options[arenaUniqueID % numOptions]


def getFeedbackMsgID(ratingVariant, arenaUniqueID):
    return backport.msgid(getFeedbackResID(ratingVariant, arenaUniqueID))
