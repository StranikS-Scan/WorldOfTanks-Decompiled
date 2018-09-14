# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/battle_loading.py
import BattleReplay
import BigWorld
from account_helpers.settings_core import settings_constants
from account_helpers.settings_core.options import BattleLoadingTipSetting
from helpers import dependency
from helpers import tips
from gui.LobbyContext import g_lobbyContext
from gui.battle_control.arena_info.interfaces import IArenaVehiclesController
from gui.battle_control.arena_info.settings import SMALL_MAP_IMAGE_SF_PATH
from gui.shared.formatters import text_styles
from gui.Scaleform.daapi.view.meta.BaseBattleLoadingMeta import BaseBattleLoadingMeta
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.battle_session import IBattleSessionProvider
__bBattleLoadingShowed = False

def isBattleLoadingShowed():
    """is battle loading screen has been showed
    """
    global __bBattleLoadingShowed
    if BattleReplay.isPlaying():
        return __bBattleLoadingShowed
    else:
        return False


def _setBattleLoading(value):
    global __bBattleLoadingShowed
    __bBattleLoadingShowed = value


DEFAULT_BATTLES_COUNT = 100

class BattleLoading(BaseBattleLoadingMeta, IArenaVehiclesController):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    settingsCore = dependency.descriptor(ISettingsCore)

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
        arenaDP = self._battleCtx.getArenaDP()
        self._setTipsInfo()
        self.__addPlayerData(arenaDP)

    def arenaLoadCompleted(self):
        if not BattleReplay.isPlaying():
            BigWorld.wg_enableGUIBackground(False, True)
        else:
            BigWorld.wg_enableGUIBackground(False, False)

    def isFalloutMode(self):
        return False

    def _populate(self):
        super(BattleLoading, self)._populate()
        self.sessionProvider.addArenaCtrl(self)
        if self._arenaVisitor is None:
            return
        else:
            BigWorld.wg_updateColorGrading()
            BigWorld.wg_enableGUIBackground(True, False)
            self._addArenaTypeData()
            return

    def _dispose(self):
        self.sessionProvider.removeArenaCtrl(self)
        if not BattleReplay.isPlaying():
            BigWorld.wg_enableGUIBackground(False, True)
        super(BattleLoading, self)._disposeWithReloading()

    def _setTipsInfo(self):
        arenaDP = self._battleCtx.getArenaDP()
        battlesCount = DEFAULT_BATTLES_COUNT
        if not isBattleLoadingShowed():
            if g_lobbyContext.getBattlesCount() is not None:
                battlesCount = g_lobbyContext.getBattlesCount()
            classTag, vLvl, nation = arenaDP.getVehicleInfo().getTypeInfo()
            criteria = tips.getTipsCriteria(self._arenaVisitor)
            criteria.setBattleCount(battlesCount)
            criteria.setClassTag(classTag)
            criteria.setLevel(vLvl)
            criteria.setNation(nation)
            tip = criteria.find()
            self.as_setTipTitleS(text_styles.highTitle(tip.status))
            self.as_setTipS(text_styles.playerOnline(tip.body))
            self.as_setVisualTipInfoS(self.__makeVisualTipVO(arenaDP, tip))
            _setBattleLoading(True)
        return

    def _addArenaTypeData(self):
        self.as_setMapIconS(SMALL_MAP_IMAGE_SF_PATH % self._arenaVisitor.type.getGeometryName())
        BigWorld.wg_setGUIBackground(self._battleCtx.getArenaScreenIcon())

    def __addPlayerData(self, arenaDP):
        vInfoVO = arenaDP.getVehicleInfo()
        self.as_setPlayerDataS(vInfoVO.vehicleID, vInfoVO.getSquadID())

    def __makeVisualTipVO(self, arenaDP, tip=None):
        setting = self.settingsCore.options.getSetting(settings_constants.GAME.BATTLE_LOADING_INFO)
        settingID = setting.getSettingID(isVisualOnly=self._arenaVisitor.gui.isSandboxBattle() or self._arenaVisitor.gui.isEventBattle(), isFallout=self.isFalloutMode())
        vo = {'settingID': settingID,
         'tipIcon': tip.icon if settingID == BattleLoadingTipSetting.OPTIONS.VISUAL else None,
         'arenaTypeID': self._arenaVisitor.type.getID(),
         'minimapTeam': arenaDP.getNumberOfTeam(),
         'showMinimap': settingID == BattleLoadingTipSetting.OPTIONS.MINIMAP,
         'showTipsBackground': settingID == BattleLoadingTipSetting.OPTIONS.MINIMAP}
        viewSettings = self.__getViewSettingByID(settingID)
        vo.update(viewSettings)
        return vo

    def __getViewSettingByID(self, settingID):
        """ Get settings for view by type
        :return:
        """
        result = {}
        if settingID == BattleLoadingTipSetting.OPTIONS.TEXT:
            result.update({'leftTeamTitleLeft': -412,
             'rightTeamTitleLeft': 204,
             'tipTitleTop': 536,
             'tipBodyTop': 562,
             'showTableBackground': True,
             'showTipsBackground': False})
        else:
            result.update({'leftTeamTitleLeft': -472,
             'rightTeamTitleLeft': 268,
             'tipTitleTop': 366,
             'tipBodyTop': 397,
             'showTableBackground': False,
             'showTipsBackground': True})
        return result
