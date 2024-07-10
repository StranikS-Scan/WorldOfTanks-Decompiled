# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/feature/util/fun_mixins.py
import logging
import typing
from adisp import adisp_async, adisp_process
from fun_random_common.fun_constants import UNKNOWN_EVENT_ID
from fun_random.gui.fun_gui_constants import SELECTOR_BATTLE_TYPES
from fun_random.gui.feature.util.fun_helpers import notifyCaller
from fun_random.gui.feature.util.fun_wrappers import hasActiveProgression, hasAnySubMode, hasSingleSubMode, hasSpecifiedSubMode
from fun_random.gui.shared.events import FunEventType, FunEventScope
from fun_random.gui.shared.event_dispatcher import showFunRandomInfoPage, showFunRandomProgressionWindow, showFunRandomModeSubSelectorWindow
from gui.impl import backport
from gui.shared.utils import SelectorBattleTypesUtils as selectorUtils
from helpers import dependency
from shared_utils import first
from skeletons.gui.game_control import IFunRandomController
if typing.TYPE_CHECKING:
    from fun_random.gui.feature.models.common import FunSubModesStatus
    from fun_random.gui.feature.models.progressions import FunProgression
    from fun_random.gui.feature.sub_modes.base_sub_mode import IFunSubMode
    from skeletons.gui.battle_session import IClientArenaVisitor
_logger = logging.getLogger(__name__)

class FunAssetPacksMixin(object):
    _funRandomCtrl = dependency.descriptor(IFunRandomController)

    @classmethod
    def getModeAssetsPointer(cls):
        return cls._funRandomCtrl.getAssetsPointer()

    @classmethod
    def getModeIconsResRoot(cls):
        return cls._funRandomCtrl.getIconsResRoot()

    @classmethod
    def getModeLocalsResRoot(cls):
        return cls._funRandomCtrl.getLocalsResRoot()

    @classmethod
    def getModeNameKwargs(cls):
        return {'modeName': cls.getModeUserName()}

    @classmethod
    def getModeUserName(cls):
        return backport.text(cls.getModeLocalsResRoot().userName())

    @classmethod
    def getModeDetailedUserName(cls, **kwargs):
        return backport.text(cls.getModeLocalsResRoot().detailedUserName(), modeName=cls.getModeUserName(), **kwargs)

    @classmethod
    def getPrebattleConditionIcon(cls):
        return backport.image(cls.getModeIconsResRoot().battle_type.c_32x32.fun_random())


class FunProgressionWatcher(object):
    _funRandomCtrl = dependency.descriptor(IFunRandomController)

    @classmethod
    @hasActiveProgression()
    def showActiveProgressionPage(cls):
        showFunRandomProgressionWindow()

    @classmethod
    def getActiveProgression(cls):
        return cls._funRandomCtrl.progressions.getActiveProgression()

    def startProgressionListening(self, updateMethod, tickMethod=None):
        self._funRandomCtrl.subscription.addListener(FunEventType.PROGRESSION_UPDATE, updateMethod)
        if tickMethod is not None:
            self._funRandomCtrl.subscription.addListener(FunEventType.PROGRESSION_TICK, tickMethod)
        return

    def stopProgressionListening(self, updateMethod, tickMethod=None):
        self._funRandomCtrl.subscription.removeListener(FunEventType.PROGRESSION_UPDATE, updateMethod)
        if tickMethod is not None:
            self._funRandomCtrl.subscription.removeListener(FunEventType.PROGRESSION_TICK, tickMethod)
        return


class FunSubModesWatcher(object):
    _funRandomCtrl = dependency.descriptor(IFunRandomController)

    @classmethod
    def getBattleSubMode(cls, arenaVisitor=None):
        return cls._funRandomCtrl.subModesHolder.getBattleSubMode(arenaVisitor)

    @classmethod
    def getDesiredSubMode(cls):
        return cls._funRandomCtrl.subModesHolder.getDesiredSubMode()

    @classmethod
    def getSubMode(cls, subModeID):
        return cls._funRandomCtrl.subModesHolder.getSubMode(subModeID)

    @classmethod
    def getSubModes(cls, subModesIDs=None, isOrdered=False):
        return cls._funRandomCtrl.subModesHolder.getSubModes(subModesIDs=subModesIDs, isOrdered=isOrdered)

    @classmethod
    def getSubModesStatus(cls, subModesIDs=None):
        return cls._funRandomCtrl.subModesInfo.getSubModesStatus(subModesIDs)

    def startSubSelectionListening(self, method):
        self._funRandomCtrl.subscription.addListener(FunEventType.SUB_SELECTION, method)

    def startSubSettingsListening(self, method, desiredOnly=False):
        scope = FunEventScope.DESIRABLE if desiredOnly else FunEventScope.DEFAULT
        self._funRandomCtrl.subscription.addListener(FunEventType.SUB_SETTINGS, method, scope)

    def startSubStatusListening(self, updateMethod, desiredOnly=False, tickMethod=None):
        scope = FunEventScope.DESIRABLE if desiredOnly else FunEventScope.DEFAULT
        self._funRandomCtrl.subscription.addListener(FunEventType.SUB_STATUS_UPDATE, updateMethod, scope)
        if tickMethod is not None:
            self._funRandomCtrl.subscription.addListener(FunEventType.SUB_STATUS_TICK, tickMethod, scope)
        return

    def stopSubSelectionListening(self, method):
        self._funRandomCtrl.subscription.removeListener(FunEventType.SUB_SELECTION, method)

    def stopSubSettingsListening(self, method, desiredOnly=False):
        scope = FunEventScope.DESIRABLE if desiredOnly else FunEventScope.DEFAULT
        self._funRandomCtrl.subscription.removeListener(FunEventType.SUB_SETTINGS, method, scope)

    def stopSubStatusListening(self, updateMethod, desiredOnly=False, tickMethod=False):
        scope = FunEventScope.DESIRABLE if desiredOnly else FunEventScope.DEFAULT
        self._funRandomCtrl.subscription.removeListener(FunEventType.SUB_STATUS_UPDATE, updateMethod, scope)
        if tickMethod is not None:
            self._funRandomCtrl.subscription.removeListener(FunEventType.SUB_STATUS_TICK, tickMethod, scope)
        return

    @adisp_async
    @adisp_process
    def selectFunRandomBattle(self, subModeID=UNKNOWN_EVENT_ID, callback=None):
        selectorUtils.setBattleTypeAsKnown(SELECTOR_BATTLE_TYPES.FUN_RANDOM)
        allSubModesIDs = self._funRandomCtrl.subModesHolder.getSubModesIDs()
        if not allSubModesIDs:
            _logger.error('Trying to get into fun random without any sub mode configured')
            notifyCaller(callback, False)
            return
        if subModeID != UNKNOWN_EVENT_ID and subModeID not in allSubModesIDs:
            _logger.error('Trying to get into not configured fun random sub mode %s', subModeID)
            notifyCaller(callback, False)
            return
        if subModeID == UNKNOWN_EVENT_ID and len(allSubModesIDs) > 1:
            showFunRandomModeSubSelectorWindow()
            notifyCaller(callback, False)
            return
        subModeID = subModeID or first(allSubModesIDs)
        if not self.getSubMode(subModeID).isAvailable():
            self.showSubModeInfoPage(subModeID)
            notifyCaller(callback, False)
            return
        result = yield self._funRandomCtrl.selectFunRandomBattle(subModeID)
        notifyCaller(callback, result)

    @hasAnySubMode()
    def showCommonInfoPage(self):
        selectorUtils.setBattleTypeAsKnown(SELECTOR_BATTLE_TYPES.FUN_RANDOM)
        showFunRandomInfoPage(self._funRandomCtrl.getSettings().infoPageUrl)

    @hasSpecifiedSubMode()
    def showSubModeInfoPage(self, subModeID):
        selectorUtils.setBattleTypeAsKnown(SELECTOR_BATTLE_TYPES.FUN_RANDOM)
        showFunRandomInfoPage(self.getSubMode(subModeID).getSettings().client.infoPageUrl)

    @hasSingleSubMode(abortAction='showCommonInfoPage')
    def showSubModesInfoPage(self):
        selectorUtils.setBattleTypeAsKnown(SELECTOR_BATTLE_TYPES.FUN_RANDOM)
        showFunRandomInfoPage(first(self.getSubModes()).getSettings().client.infoPageUrl)


class FunSubModeHolder(FunSubModesWatcher):

    def __init__(self):
        super(FunSubModeHolder, self).__init__()
        self.__subMode = None
        return

    def getHoldingSubMode(self):
        return self.__subMode

    def catchSubMode(self, subModeID):
        self.__subMode = self.getSubMode(subModeID)

    def releaseSubMode(self):
        self.__subMode = None
        return
