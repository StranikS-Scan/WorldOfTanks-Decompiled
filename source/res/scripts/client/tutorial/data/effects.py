# Embedded file name: scripts/client/tutorial/data/effects.py
from tutorial.data.has_id import HasTargetID

class EFFECT_TYPE(object):
    ACTIVATE, DEACTIVATE, GLOBAL_ACTIVATE, GLOBAL_DEACTIVATE, SHOW_HINT, CLOSE_HINT, SHOW_DIALOG, SHOW_WINDOW, CLOSE_WINDOW, SHOW_GREETING, REFUSE_TRAINING, NEXT_CHAPTER, RUN_TRIGGER, REQUEST_BONUS, REQUEST_ALL_BONUSES, SET_ITEM_PROPS, FINISH_TRAINING, INVOKE_GUI_CMD, SHOW_MESSAGE, SHOW_MARKER, REMOVE_MARKER, NEXT_TASK, INVOKE_PLAYER_CMD, TELEPORT, ENTER_QUEUE, EXIT_QUEUE, ENABLE_CAMERA_ZOOM, DISABLE_CAMERA_ZOOM, PLAY_MUSIC, OPEN_INTERNAL_BROWSER, SET_GUI_ITEM_CRITERIA, SET_ACTION, REMOVE_ACTION, SET_VAR, SAVE_TUTORIAL_SETTING, SAVE_ACCOUNT_SETTING, CLEAR_SCENE, GO_SCENE, SHOW_UNLOCKED_CHAPTER, SHOW_AWARD_WINDOW = range(0, 40)


EFFECT_TYPE_NAMES = dict(((v, k) for k, v in EFFECT_TYPE.__dict__.iteritems() if k.isupper()))

class HasTargetEffect(HasTargetID):

    def __init__(self, targetID, effectType, conditions = None):
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

    def __init__(self, effectType, conditions = None, **kwargs):
        super(SimpleEffect, self).__init__(None, effectType, conditions=conditions, **kwargs)
        return

    def __repr__(self):
        return 'SimpleEffect(type = {0!r:s})'.format(EFFECT_TYPE_NAMES[self.getType()])


class SetGuiItemProperty(HasTargetEffect):

    def __init__(self, targetID, props, conditions = None, revert = False):
        super(SetGuiItemProperty, self).__init__(targetID, EFFECT_TYPE.SET_ITEM_PROPS, conditions=conditions)
        self.__props = props
        self.__revert = revert

    def getProps(self):
        return self.__props.copy()

    def isRevert(self):
        return self.__revert

    def clear(self):
        super(SetGuiItemProperty, self).clear()
        self.__props.clear()
