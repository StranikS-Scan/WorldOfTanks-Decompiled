# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch_progression/scripts/client/grinch_progression/gui/shared/gui_items/processors/processors.py
import BigWorld
from account_helpers.settings_core.settings_constants import OnceOnlyHints
from gui import SystemMessages
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.gui_items.processors import Processor, makeError
from gui.shared.notifications import NotificationPriorityLevel
from messenger.formatters.service_channel import QuestAchievesFormatter
from gui.shared.event_dispatcher import showCustomizationRarityAwardScreen
from gui.shared.event_dispatcher import pushNYAttached3DRewardsMessage
from grinch_progression.gui.shared.event_dispatcher import showGPStyleRewardNotification
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.customization import ICustomizationService
from gui.shared.gui_items import getItemTypeID
from items.components.c11n_constants import Rarity
NOTIFICATION_RARITY_RANGE = [Rarity.RARE]

class OpenStepForChapter(Processor):
    c11n = dependency.descriptor(ICustomizationService)
    __settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, chapterID, stepID):
        super(OpenStepForChapter, self).__init__()
        self._chapterID = chapterID
        self._stepID = stepID

    def _request(self, callback):
        BigWorld.player().GrinchProgressionAccountComponent.openStep(self._chapterID, self._stepID, lambda code, errStr, ext: self._response(code, callback, errStr=errStr, ctx=ext))

    def _errorHandler(self, code, errStr='', ctx=None):
        SystemMessages.pushMessage(text=backport.text(R.strings.grinch_progression.notification.reward.error()), priority=NotificationPriorityLevel.MEDIUM, type=SystemMessages.SM_TYPE.Error)
        return makeError(errStr, SystemMessages.SM_TYPE.Error)

    def _successHandler(self, code, ctx=None):
        _ctx = {k:v for k, v in ctx.iteritems() if k not in ('version', 'tokens')} if ctx is not None else {}
        for customization in _ctx.get('customizations', []):
            custType = customization.get('custType')
            if custType == 'attachment':
                attachment = self.c11n.getItemByID(getItemTypeID(custType), customization.get('id'))
                if attachment.rarity in NOTIFICATION_RARITY_RANGE:
                    pushNYAttached3DRewardsMessage({'bonuses': {'customizations': [customization]}})
                elif attachment.rarity in Rarity.UI_EFFECT:
                    isFirstEntry = not self.__settingsCore.serverSettings.getOnceOnlyHintsSetting(OnceOnlyHints.NEW_C11N_SECTION_HINT)
                    showCustomizationRarityAwardScreen(attachment, isFirstEntry)
            if custType == 'style':
                style = self.c11n.getItemByID(getItemTypeID(custType), customization.get('id'))
                if not style.is3D:
                    showGPStyleRewardNotification({'bonuses': {'customizations': [customization]}})

        fmt = QuestAchievesFormatter.formatQuestAchieves(_ctx, False, processCompensations=False)
        if fmt is not None:
            header = backport.text(R.strings.grinch_progression.notification.board.rewardClaim.header())
            SystemMessages.pushMessage(fmt, type=SystemMessages.SM_TYPE.InformationHeader, priority=NotificationPriorityLevel.LOW, messageData={'header': header})
        return super(OpenStepForChapter, self)._successHandler(code, ctx)
