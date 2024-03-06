# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client_common/hints/battle/schemas/newbie.py
import typing
from dict2model import fields, validate
from helpers import dependency
from hints_common.battle.schemas.base import HMCContextType, HMCPropsType
from hints.battle.newbie import getLogger
from hints.battle.schemas.base import ClientHintHistoryModel, ClientHintHistorySchema, ClientHintModel, ClientHintSchema, CHMTextType, CHMVisualType, CHMSoundType, CHMLifecycleType
from skeletons.gui.battle_hints.newbie_battle_hints_controller import INewbieBattleHintsController
_logger = getLogger('Model')
_DEFAULT_DISPLAY_COUNT = 5

class NewbieClientHintHistoryModel(ClientHintHistoryModel):
    __slots__ = ('displayCount',)

    def __init__(self, modifyPriority, cooldown, displayCount):
        super(NewbieClientHintHistoryModel, self).__init__(modifyPriority, cooldown)
        self.displayCount = displayCount

    def _reprArgs(self):
        return '{}, displayCount={}'.format(super(NewbieClientHintHistoryModel, self)._reprArgs(), self.displayCount)


class NewbieClientHintHistorySchema(ClientHintHistorySchema[NewbieClientHintHistoryModel]):
    __slots__ = ()

    def __init__(self):
        super(NewbieClientHintHistorySchema, self).__init__(checkUnknown=True, modelClass=NewbieClientHintHistoryModel)
        self._fields['displayCount'] = fields.Integer(required=False, default=_DEFAULT_DISPLAY_COUNT, deserializedValidators=validate.Range(minValue=1))


class NewbieClientHintModel(ClientHintModel[HMCPropsType, HMCContextType, CHMTextType, CHMVisualType, CHMSoundType, CHMLifecycleType, NewbieClientHintHistoryModel]):
    __slots__ = ()
    _newbieHintsCtrl = dependency.descriptor(INewbieBattleHintsController)

    def validate(self, *args, **kwargs):
        if not self._newbieHintsCtrl.isEnabled():
            _logger.debug('Hint <%s> action disabled by server.', self.uniqueName)
            return False
        return super(NewbieClientHintModel, self).validate(*args, **kwargs)

    def canBeShown(self):
        if not self._newbieHintsCtrl.isEnabled() or not self._newbieHintsCtrl.isUserSettingEnabled():
            _logger.debug('Can not show <%s>. Disabled by server or user.', self.uniqueName)
            return False
        else:
            if self.history is not None:
                displayCount = self._newbieHintsCtrl.getDisplayCount(self.uniqueName)
                if displayCount is None:
                    _logger.debug('Can not show <%s>. History completed or disabled.', self.uniqueName)
                    return False
                if displayCount >= self.history.displayCount:
                    _logger.debug('Can not show <%s>. Hint reached display limit.', self.uniqueName)
                    return False
            return super(NewbieClientHintModel, self).canBeShown()


hintSchema = ClientHintSchema[NewbieClientHintModel](historySchema=NewbieClientHintHistorySchema(), modelClass=NewbieClientHintModel)
