# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/battle_loading.py
from functools import partial
import BattleReplay
from account_helpers.settings_core import settings_constants
from account_helpers.settings_core.options import BattleLoadingTipSetting
from helpers import dependency
from helpers import tips
from gui.battle_control.arena_info.interfaces import IArenaVehiclesController
from gui.battle_control.arena_info.settings import SMALL_MAP_IMAGE_SF_PATH
from gui.shared.formatters import text_styles
from gui.Scaleform.daapi.view.meta.BaseBattleLoadingMeta import BaseBattleLoadingMeta
from ReplayEvents import g_replayEvents
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.lobby_context import ILobbyContext
_bBattleReplayLoadingShowed = False

def _setBattleLoading(value):
    global _bBattleReplayLoadingShowed
    _bBattleReplayLoadingShowed = value and BattleReplay.isPlaying()


def _isBattleLoadingShowed():
    if BattleReplay.isPlaying():
        if _setBattleLoading not in g_replayEvents.onReplayTerminated:
            g_replayEvents.onReplayTerminated += partial(_setBattleLoading, False)
        return _bBattleReplayLoadingShowed
    return False


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
        if not _isBattleLoadingShowed():
            if self.lobbyContext.getBattlesCount() is not None:
                battlesCount = self._getBattlesCount()
            criteria = tips.getTipsCriteria(self._arenaVisitor)
            criteria.setContext(ctx={'battlesCount': battlesCount,
             'vehicleType': arenaDP.getVehicleInfo().vehicleType})
            translation = self.gui.resourceManager.getTranslatedText
            tip = criteria.find()
            self.as_setTipTitleS(self._formatTipTitle(translation(tip.status)))
            self.as_setTipS(self._formatTipBody(translation(tip.body)))
            self.as_setVisualTipInfoS(self._makeVisualTipVO(arenaDP, tip))
            _setBattleLoading(True)
        return

    def _formatTipTitle(self, tipTitleText):
        return text_styles.highTitle(tipTitleText)

    def _formatTipBody(self, tipBody):
        return text_styles.playerOnline(tipBody)

    def _addArenaTypeData(self):
        self.as_setMapIconS(SMALL_MAP_IMAGE_SF_PATH % self._arenaVisitor.type.getGeometryName())

    def _getSettingsID(self, loadingInfo):
        return self.settingsCore.options.getSetting(loadingInfo).getSettingID(isVisualOnly=self._arenaVisitor.gui.isSandboxBattle() or self._arenaVisitor.gui.isEventBattle())

    def _makeVisualTipVO(self, arenaDP, tip=None):
        loadingInfo = settings_constants.GAME.BATTLE_LOADING_RANKED_INFO if self._arenaVisitor.gui.isRankedBattle() else settings_constants.GAME.BATTLE_LOADING_INFO
        if tip is not None and tip.isValid():
            settingID = self._getSettingsID(loadingInfo)
        else:
            settingID = BattleLoadingTipSetting.OPTIONS.TEXT
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
