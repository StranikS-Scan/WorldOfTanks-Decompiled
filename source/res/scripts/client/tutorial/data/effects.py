# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/tutorial/data/effects.py
from tutorial.data.has_id import HasTargetID

class EFFECT_TYPE(object):
    EFFECTS_GROUP, ACTIVATE, DEACTIVATE, GLOBAL_ACTIVATE, GLOBAL_DEACTIVATE, SHOW_HINT, CLOSE_HINT, SHOW_DIALOG, SHOW_WINDOW, CLOSE_WINDOW, SHOW_GREETING, REFUSE_TRAINING, NEXT_CHAPTER, RUN_TRIGGER, REQUEST_BONUS, REQUEST_ALL_BONUSES, SET_ITEM_PROPS, FINISH_TRAINING, INVOKE_GUI_CMD, SHOW_MESSAGE, SHOW_MARKER, REMOVE_MARKER, NEXT_TASK, INVOKE_PLAYER_CMD, TELEPORT, ENTER_MODE, ENTER_QUEUE, EXIT_QUEUE, ENABLE_CAMERA_ZOOM, DISABLE_CAMERA_ZOOM, PLAY_MUSIC, OPEN_INTERNAL_BROWSER, SET_GUI_ITEM_CRITERIA, SET_GUI_ITEM_VIEW_CRITERIA, SET_ACTION, REMOVE_ACTION, SET_VAR, SAVE_TUTORIAL_SETTING, SAVE_ACCOUNT_SETTING, CLEAR_SCENE, GO_SCENE, SHOW_UNLOCKED_CHAPTER, SELECT_VEHICLE_IN_HANGAR, LOAD_VIEW, CLOSE_VIEW, SHOW_AWARD_WINDOW, PLAY_ANIMATION, REQUEST_EXCLUSIVE_HINT, UPDATE_EXCLUSIVE_HINTS, SET_ALLOWED_TO_FIGHT, RESTORE_CHECKPOINT, SAVE_CHECKPOINT, PLAY_VIDEO, PLAY_SOUND, START_VSE_PLAN = range(0, 55)


EFFECT_TYPE_NAMES = dict(((v, k) for k, v in EFFECT_TYPE.__dict__.iteritems() if k.isupper()))

class HasTargetEffect(HasTargetID):

    def __init__(self, targetID, effectType, conditions=None):
        super(HasTargetEffect, self).__init__(targetID=targetID)
        self.__type = effectType
        self.__conditions = conditions

    def __repr__(self):
        return 'HasTargetEffect(type = {0!r:s}, targetID = {1:>s})'.format(EFFECT_TYPE_NAMES[self.getType()], self.getTargetID())

    def getType(self):
        return self.__type

    def getConditions(self):
        return self.__conditions

    def clear(self):
        if self.__conditions is not None:
            self.__conditions.clear()
        self.__conditions = None
        return


class SimpleEffect(HasTargetEffect):

    def __init__(self, effectType, conditions=None, **kwargs):
        super(SimpleEffect, self).__init__(None, effectType, conditions=conditions, **kwargs)
        return

    def __repr__(self):
        return 'SimpleEffect(type = {0!r:s})'.format(EFFECT_TYPE_NAMES[self.getType()])


class InvokeGuiCommand(HasTargetEffect):

    def __init__(self, targetID, argOverrides, conditions=None):
        super(InvokeGuiCommand, self).__init__(targetID, EFFECT_TYPE.INVOKE_GUI_CMD, conditions=conditions)
        self.__argOverrides = argOverrides or {}

    def getArgOverrides(self):
        return self.__argOverrides


class EffectsGroup(SimpleEffect):

    def __init__(self, effects, conditions=None):
        super(EffectsGroup, self).__init__(EFFECT_TYPE.EFFECTS_GROUP, conditions=conditions)
        self.__effects = effects

    def getEffects(self):
        return self.__effects[:]


class SetGuiItemProperties(HasTargetEffect):

    def __init__(self, targetID, props, conditions=None):
        super(SetGuiItemProperties, self).__init__(targetID, EFFECT_TYPE.SET_ITEM_PROPS, conditions=conditions)
        self.__props = props

    def getProps(self):
        return self.__props.copy()

    def clear(self):
        super(SetGuiItemProperties, self).clear()
        self.__props.clear()


class PlayAnimationEffect(HasTargetEffect):

    def __init__(self, targetID, animType, waitForFinish, conditions=None):
        super(PlayAnimationEffect, self).__init__(targetID, EFFECT_TYPE.PLAY_ANIMATION, conditions=conditions)
        self.__animType = animType
        self.__waitForFinish = waitForFinish

    def getAnimType(self):
        return self.__animType

    def needWaitForFinish(self):
        return self.__waitForFinish


class SetAllowedToFightEffect(SimpleEffect):

    def __init__(self, value, conditions=None):
        super(SetAllowedToFightEffect, self).__init__(EFFECT_TYPE.SET_ALLOWED_TO_FIGHT, conditions=conditions)
        self.__value = value

    def getValue(self):
        return self.__value


class PlaySoundEffect(HasTargetEffect):

    def __init__(self, soundID, soundEvent, conditions=None):
        super(PlaySoundEffect, self).__init__(soundID, EFFECT_TYPE.PLAY_SOUND, conditions=conditions)
        self.__soundEvent = soundEvent

    def getSoundEvent(self):
        return self.__soundEvent
