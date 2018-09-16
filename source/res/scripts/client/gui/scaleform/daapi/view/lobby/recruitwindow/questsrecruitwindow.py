# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/recruitWindow/QuestsRecruitWindow.py
import nations
from gui import SystemMessages
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.meta.QuestRecruitWindowMeta import QuestRecruitWindowMeta
from gui.Scaleform.genConsts.AWARDWINDOW_CONSTANTS import AWARDWINDOW_CONSTANTS
from gui.Scaleform.locale.DIALOGS import DIALOGS
from gui.server_events.pm_constants import SOUNDS, PERSONAL_MISSIONS_SILENT_SOUND_SPACE
from gui.shared.gui_items import Tankman
from gui.shared.gui_items.processors.quests import PersonalMissionsGetTankwomanReward
from gui.shared.utils import decorators
from helpers import dependency
from helpers.i18n import makeString as _ms
from items import tankmen
from skeletons.gui.server_events import IEventsCache

class QuestsRecruitWindow(QuestRecruitWindowMeta):
    eventsCache = dependency.descriptor(IEventsCache)
    _COMMON_SOUND_SPACE = PERSONAL_MISSIONS_SILENT_SOUND_SPACE

    def __init__(self, ctx=None):
        super(QuestsRecruitWindow, self).__init__()
        self.__currentSelectedNationID = None
        self.__questID = ctx['questID']
        self.__isPremium = ctx['isPremium']
        self.__fnGroup = ctx['fnGroup']
        self.__lnGroup = ctx['lnGroup']
        self.__iGroupID = ctx['iGroupID']
        self.__freeXpValue = ctx.get('freeXP', 0)
        return

    def onWindowClose(self):
        self.destroy()

    @decorators.process('updating')
    def onApply(self, data):
        mission = self.eventsCache.personalMissions.getQuests().get(self.__questID)
        result = yield PersonalMissionsGetTankwomanReward(mission, int(data.nation), int(data.vehicle), data.tankmanRole).request()
        if result.userMsg:
            SystemMessages.pushMessage(result.userMsg, type=result.sysMsgType)
        if result.success:
            self.destroy()

    def _onRegisterFlashComponent(self, viewPy, alias):
        super(QuestsRecruitWindow, self)._onRegisterFlashComponent(viewPy, alias)
        if alias == VIEW_ALIAS.RECRUIT_PARAMS:
            viewPy.onDataChange += self.__paramsChangeHandler
            viewPy.init()

    def _onUnregisterFlashComponent(self, viewPy, alias):
        super(QuestsRecruitWindow, self)._onUnregisterFlashComponent(viewPy, alias)
        if alias == VIEW_ALIAS.RECRUIT_PARAMS:
            viewPy.onDataChange -= self.__paramsChangeHandler

    def _populate(self):
        super(QuestsRecruitWindow, self)._populate()
        self.soundManager.playInstantSound(SOUNDS.WOMAN_AWARD_WINDOW)

    def __paramsChangeHandler(self, selectedNationID, selectedVehClass, selectedVehicle, selectedTmanRole):
        selectedNationID = int(selectedNationID)
        nationName = nations.NAMES[selectedNationID]
        if self.__currentSelectedNationID != selectedNationID:
            firstNameID, lastNameID, iconID = self.eventsCache.personalMissions.getNextTankwomanIDs(selectedNationID, self.__isPremium, int(self.__fnGroup), int(self.__lnGroup), int(self.__iGroupID))
            rankID = Tankman.calculateRankID(tankmen.MAX_SKILL_LEVEL, self.__freeXpValue)
            faceIcon = Tankman.getBigIconPath(selectedNationID, iconID)
            self.as_setInitDataS({'windowTitle': _ms(DIALOGS.RECRUITWINDOW_TITLE),
             'applyButtonLabel': _ms(DIALOGS.RECRUITWINDOW_SUBMIT),
             'cancelButtonLabel': _ms(DIALOGS.RECRUITWINDOW_CANCEL),
             'name': Tankman.getFullUserName(selectedNationID, firstNameID, lastNameID),
             'nation': nationName,
             'rank': Tankman.getRankUserName(selectedNationID, rankID),
             'backAnimationData': self.__getBackAnimationData(faceIcon)})
        self.__currentSelectedNationID = selectedNationID

    def __getBackAnimationData(self, faceIcon):
        return {'image': faceIcon,
         'animationPath': AWARDWINDOW_CONSTANTS.EXPLOSION_BACK_ANIMATION_PATH,
         'animationLinkage': AWARDWINDOW_CONSTANTS.EXPLOSION_BACK_ANIMATION_LINKAGE}
