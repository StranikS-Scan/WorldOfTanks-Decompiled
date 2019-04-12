# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/battle_loading.py
import BattleReplay
from account_helpers.settings_core import settings_constants
from account_helpers.settings_core.options import BattleLoadingTipSetting
from helpers import dependency
from helpers import tips
from gui.battle_control.arena_info.interfaces import IArenaVehiclesController
from gui.battle_control.arena_info.settings import SMALL_MAP_IMAGE_SF_PATH
from gui.shared.formatters import text_styles
from gui.Scaleform.daapi.view.meta.BaseBattleLoadingMeta import BaseBattleLoadingMeta
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.lobby_context import ILobbyContext
__bBattleLoadingShowed = False

def isBattleLoadingShowed():
    global __bBattleLoadingShowed
    return __bBattleLoadingShowed if BattleReplay.isPlaying() else False


def _setBattleLoading(value):
    global __bBattleLoadingShowed
    __bBattleLoadingShowed = value


DEFAULT_BATTLES_COUNT = 100

class BattleLoading(BaseBattleLoadingMeta, IArenaVehiclesController):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    settingsCore = dependency.descriptor(ISettingsCore)
    lobbyContext = dependency.descriptor(ILobbyContext)
    gui = dependency.descriptor(IGuiLoader)

    def __init__(self, _=None):
        super(BattleLoading, self).__init__()
        self._battleCtx = None
        self._arenaVisitor = None
        self._isArenaTypeDataInited = False
        return

    def startControl(self, battleCtx, arenaVisitor):
        self._battleCtx = battleCtx
        self._arenaVisitor = arenaVisitor

    def stopControl(self):
        self._battleCtx = None
        self._arenaVisitor = None
        return

    def updateSpaceLoadProgress(self, progress):
        self.as_setProgressS(progress)

    def invalidateArenaInfo(self):
        self._setTipsInfo()

    def _populate(self):
        super(BattleLoading, self)._populate()
        self.sessionProvider.addArenaCtrl(self)
        if self._arenaVisitor is None:
            return
        else:
            self._addArenaTypeData()
            return

    def _dispose(self):
        self.sessionProvider.removeArenaCtrl(self)
        super(BattleLoading, self)._disposeWithReloading()

    def _getBattlesCount(self):
        return self.lobbyContext.getBattlesCount()

    def _setTipsInfo(self):
        arenaDP = self._battleCtx.getArenaDP()
        battlesCount = DEFAULT_BATTLES_COUNT
        if not isBattleLoadingShowed():
            if self.lobbyContext.getBattlesCount() is not None:
                battlesCount = self._getBattlesCount()
            classTag, vLvl, nation = arenaDP.getVehicleInfo().getTypeInfo()
            criteria = tips.getTipsCriteria(self._arenaVisitor)
            criteria.setBattleCount(battlesCount)
            criteria.setClassTag(classTag)
            criteria.setLevel(vLvl)
            criteria.setNation(nation)
            translation = self.gui.resourceManager.getTranslatedText
            tip = criteria.find()
            self.as_setTipTitleS(text_styles.highTitle(translation(tip.status)))
            self.as_setTipS(text_styles.playerOnline(translation(tip.body)))
            self.as_setVisualTipInfoS(self.__makeVisualTipVO(arenaDP, tip))
            _setBattleLoading(True)
        return

    def _addArenaTypeData(self):
        self.as_setMapIconS(SMALL_MAP_IMAGE_SF_PATH % self._arenaVisitor.type.getGeometryName())

    def __makeVisualTipVO(self, arenaDP, tip=None):
        loadingInfo = settings_constants.GAME.BATTLE_LOADING_RANKED_INFO if self._arenaVisitor.gui.isRankedBattle() else settings_constants.GAME.BATTLE_LOADING_INFO
        setting = self.settingsCore.options.getSetting(loadingInfo)
        settingID = setting.getSettingID(isVisualOnly=self._arenaVisitor.gui.isSandboxBattle() or self._arenaVisitor.gui.isEventBattle())
        tipIconPath = self.gui.resourceManager.getImagePath(tip.icon)
        vo = {'settingID': settingID,
         'tipIcon': tipIconPath if settingID == BattleLoadingTipSetting.OPTIONS.VISUAL else None,
         'arenaTypeID': self._arenaVisitor.type.getID(),
         'minimapTeam': arenaDP.getNumberOfTeam(),
         'showMinimap': settingID == BattleLoadingTipSetting.OPTIONS.MINIMAP,
         'showTipsBackground': settingID == BattleLoadingTipSetting.OPTIONS.MINIMAP}
        viewSettings = self._getViewSettingByID(settingID)
        vo.update(viewSettings)
        return vo

    def _getViewSettingByID(self, settingID):
        result = {}
        if settingID == BattleLoadingTipSetting.OPTIONS.TEXT:
            result.update({'leftTeamTitleLeft': -410,
             'rightTeamTitleLeft': 204,
             'tipTitleTop': 536,
             'tipBodyTop': 562,
             'showTableBackground': True,
             'showTipsBackground': False})
        else:
            result.update({'leftTeamTitleLeft': -475,
             'rightTeamTitleLeft': 270,
             'tipTitleTop': 366,
             'tipBodyTop': 397,
             'showTableBackground': False,
             'showTipsBackground': True})
        return result
