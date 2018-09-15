# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/recruitWindow/GiftRecruitWindow.py
import nations
from gui import SystemMessages
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.meta.QuestRecruitWindowMeta import QuestRecruitWindowMeta
from gui.Scaleform.genConsts.AWARDWINDOW_CONSTANTS import AWARDWINDOW_CONSTANTS
from gui.Scaleform.locale.DIALOGS import DIALOGS
from gui.server_events.pm_constants import SOUNDS, PERSONAL_MISSIONS_SILENT_SOUND_SPACE
from gui.shared.gui_items import Tankman
from gui.shared.utils import decorators
from helpers import dependency
from helpers.i18n import makeString as _ms
from items import tankmen
from shared_utils import first
from skeletons.gui.server_events import IEventsCache
from gui.shared.gui_items.processors.quests import GiftGetReward
from items import makeIntCompactDescrByID

class GiftRecruitWindow(QuestRecruitWindowMeta):
    eventsCache = dependency.descriptor(IEventsCache)
    _COMMON_SOUND_SPACE = PERSONAL_MISSIONS_SILENT_SOUND_SPACE

    def __init__(self, ctx=None):
        super(GiftRecruitWindow, self).__init__()
        self.__currentSelectedNationID = None
        return

    def onWindowClose(self):
        self.destroy()

    @decorators.process('updating')
    def onApply(self, data):
        intCD = makeIntCompactDescrByID('vehicle', int(data.nation), int(data.vehicle))
        result = yield GiftGetReward(intCD, data.tankmanRole).request()
        if result.userMsg:
            SystemMessages.pushMessage(result.userMsg, type=result.sysMsgType)
        if result.success:
            self.destroy()

    def _onRegisterFlashComponent(self, viewPy, alias):
        super(GiftRecruitWindow, self)._onRegisterFlashComponent(viewPy, alias)
        if alias == VIEW_ALIAS.RECRUIT_PARAMS:
            viewPy.onDataChange += self.__paramsChangeHandler
            viewPy.init()

    def _onUnregisterFlashComponent(self, viewPy, alias):
        super(GiftRecruitWindow, self)._onUnregisterFlashComponent(viewPy, alias)
        if alias == VIEW_ALIAS.RECRUIT_PARAMS:
            viewPy.onDataChange -= self.__paramsChangeHandler

    def _populate(self):
        super(GiftRecruitWindow, self)._populate()
        self.soundManager.playSound(SOUNDS.WOMAN_AWARD_WINDOW, owner=id(self))

    def __paramsChangeHandler(self, selectedNationID, selectedVehClass, selectedVehicle, selectedTmanRole):
        selectedNationID = int(selectedNationID)
        nationName = nations.NAMES[selectedNationID]
        if self.__currentSelectedNationID != selectedNationID:
            fg = next(iter([ fg for fg in tankmen.getNationGroups(selectedNationID, True) if fg.isFemales ]))
            firstNameID = first(fg.firstNames)
            lastNameID = first(fg.lastNames)
            iconID = first(fg.icons)
            rankID = Tankman.calculateRankID(tankmen.MAX_SKILL_LEVEL, 0)
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
