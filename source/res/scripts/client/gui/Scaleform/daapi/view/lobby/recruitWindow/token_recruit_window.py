# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/recruitWindow/token_recruit_window.py
import nations
from adisp import async, process
from gui import SystemMessages
from gui.impl import backport
from gui.impl.gen.resources import R
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.recruitWindow.RecruitParamsComponent import packPredefinedTmanParams
from gui.Scaleform.daapi.view.meta.QuestRecruitWindowMeta import QuestRecruitWindowMeta
from gui.Scaleform.framework.entities.view_sound import CommonSoundSpaceSettings
from gui.Scaleform.genConsts.AWARDWINDOW_CONSTANTS import AWARDWINDOW_CONSTANTS
from gui.server_events.pm_constants import SOUNDS
from gui.shared.gui_items import Tankman
from gui.shared.gui_items.processors.tankman import TankmanTokenRecruit
from gui.shared.utils import decorators
from gui.sounds.filters import States, StatesGroup
from helpers import dependency
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from gui.server_events.recruit_helper import NonRecruitNotifierSingleton

class TokenRecruitWindow(QuestRecruitWindowMeta):
    eventsCache = dependency.descriptor(IEventsCache)
    itemsCache = dependency.descriptor(IItemsCache)
    __SOUND_SETTINGS = CommonSoundSpaceSettings(name='hangar', entranceStates={SOUNDS.STATE_PLACE: SOUNDS.STATE_PLACE_GARAGE,
     StatesGroup.HANGAR_FILTERED: States.HANGAR_FILTERED_OFF}, exitStates={}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent=SOUNDS.WOMAN_AWARD_WINDOW, exitEvent='')
    _COMMON_SOUND_SPACE = __SOUND_SETTINGS

    def __init__(self, ctx=None):
        super(TokenRecruitWindow, self).__init__()
        self.__currentSelectedNationID = None
        self.__tokenName = ctx['tokenName']
        self.__tokenData = ctx['tokenData']
        return

    def onWindowClose(self):
        self.destroy()

    @decorators.process('updating')
    def onApply(self, data):
        yield self.__recruitTankman(int(data.nation), int(data.vehicle), data.tankmanRole, self.__tokenName, self.__tokenData)
        self.onWindowClose()

    def _onRegisterFlashComponent(self, viewPy, alias):
        super(TokenRecruitWindow, self)._onRegisterFlashComponent(viewPy, alias)
        if alias == VIEW_ALIAS.RECRUIT_PARAMS:
            viewPy.setPredefinedTankman(packPredefinedTmanParams(roles=self.__tokenData.getRoles(), nationsParam=self.__tokenData.getNations()))
            viewPy.onDataChange += self.__paramsChangeHandler
            viewPy.init()

    def _onUnregisterFlashComponent(self, viewPy, alias):
        super(TokenRecruitWindow, self)._onUnregisterFlashComponent(viewPy, alias)
        if alias == VIEW_ALIAS.RECRUIT_PARAMS:
            viewPy.onDataChange -= self.__paramsChangeHandler

    def __paramsChangeHandler(self, selectedNationID, selectedVehClass, selectedVehicle, selectedTmanRole):
        selectedNationID = int(selectedNationID)
        nationName = nations.NAMES[selectedNationID]
        if self.__currentSelectedNationID != selectedNationID:
            faceIcon = self.__tokenData.getBigIcon()
            bgImage = self.__getBgImage(self.__tokenData.getSourceID())
            self.as_setInitDataS({'windowTitle': backport.text(R.strings.dialogs.recruitWindow.title()),
             'applyButtonLabel': backport.text(R.strings.dialogs.recruitWindow.submit()),
             'cancelButtonLabel': backport.text(R.strings.dialogs.recruitWindow.cancel()),
             'name': self.__tokenData.getFullUserNameByNation(selectedNationID),
             'nation': nationName,
             'rank': Tankman.getRankUserName(selectedNationID, self.__tokenData.getRankID()),
             'backAnimationData': None if bgImage else self.__getBackAnimationData(faceIcon),
             'bgImage': bgImage,
             'tankmanIcon': faceIcon})
        self.__currentSelectedNationID = selectedNationID
        return

    @staticmethod
    def __getBackAnimationData(faceIcon):
        return {'image': faceIcon,
         'animationPath': AWARDWINDOW_CONSTANTS.EXPLOSION_BACK_ANIMATION_PATH,
         'animationLinkage': AWARDWINDOW_CONSTANTS.EXPLOSION_BACK_ANIMATION_LINKAGE}

    @staticmethod
    def __getBgImage(eventName):
        bgID = None
        if eventName is not None:
            bgID = R.images.gui.maps.icons.tankmen.windows.dyn(attr='{}_recruitWindowBg'.format(eventName))
        return backport.image(bgID()) if bgID is not None and bgID.exists() else ''

    @async
    @process
    def __recruitTankman(self, nationID, vehTypeID, role, tokenName, tokenData, callback):
        recruiter = TankmanTokenRecruit(nationID=int(nationID), vehTypeID=int(vehTypeID), role=role, tokenName=tokenName, tokenData=tokenData)
        _, msg, msgType, _ = yield recruiter.request()
        if msg:
            SystemMessages.pushMessage(msg, type=msgType)
        callback(None)
        NonRecruitNotifierSingleton().getInstance().notifyNonRecruitCount()
        return
