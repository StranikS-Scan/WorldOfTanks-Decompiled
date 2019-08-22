# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/battle_royale/battle_royale_intro.py
from account_helpers import AccountSettings
from account_helpers.AccountSettings import GUI_START_BEHAVIOR
from account_helpers.settings_core.settings_constants import GuiSettingsBehavior
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.view.lobby.battle_royale.battle_royale_sounds import BATTLE_ROYALE_PAGE_SOUND_SPACE
from gui.Scaleform.daapi.view.meta.BattleRoyaleIntroMeta import BattleRoyaleIntroMeta
from gui.Scaleform.genConsts.BATTLEROYALE_CONSTS import BATTLEROYALE_CONSTS
from gui.impl import backport
from gui.impl.gen import R
from gui.shared import event_dispatcher
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IBattleRoyaleController
BLOCKS_COUNT = 3

class BattleRoyaleIntro(LobbySubView, BattleRoyaleIntroMeta):
    __battleRoyaleController = dependency.descriptor(IBattleRoyaleController)
    __settingsCore = dependency.descriptor(ISettingsCore)
    _COMMON_SOUND_SPACE = BATTLE_ROYALE_PAGE_SOUND_SPACE

    def onAcceptClick(self):
        self.__setShowStateFlags()
        self.__showBattleRoyaleProgress()

    def onClose(self):
        self.__setShowStateFlags()
        self.__showBattleRoyaleProgress()

    def onDetailedClick(self):
        self.__setShowStateFlags()
        self.__battleRoyaleController.showBattleRoyalePage(ctx={'selectedItemID': BATTLEROYALE_CONSTS.BATTLE_ROYALE_INFO_ID})

    def onPlayVideoClick(self):
        event_dispatcher.showBattleRoyaleIntroVideo(self.alias)

    def _populate(self):
        super(BattleRoyaleIntro, self)._populate()
        headerData = {'title': backport.text(R.strings.battle_royale.event.name()),
         'leftSideText': backport.text(R.strings.battle_royale.intro.description()),
         'rightSideText': None,
         'tooltip': None}
        data = []
        for index in range(BLOCKS_COUNT):
            index += 1
            title = backport.text(R.strings.battle_royale.intro.blocks.dyn('block{}'.format(index)).title())
            if index == 2:
                descr = backport.text(R.strings.br_about_event.aboutEvent.feature_2.description())
            else:
                descr = backport.text(R.strings.battle_royale.intro.blocks.dyn('block{}'.format(index)).description())
            data.append({'title': title,
             'description': descr})

        self.as_setDataS(headerData, data)
        return

    def __setShowStateFlags(self):
        defaults = AccountSettings.getFilterDefault(GUI_START_BEHAVIOR)
        stateFlags = self.__settingsCore.serverSettings.getSection(GUI_START_BEHAVIOR, defaults)
        stateFlags[GuiSettingsBehavior.BATTLE_ROYALE_WELCOME_VIEW_SHOWED] = True
        self.__settingsCore.serverSettings.setSectionSettings(GUI_START_BEHAVIOR, stateFlags)

    def __showBattleRoyaleProgress(self):
        self.__battleRoyaleController.showBattleRoyalePage(ctx={'selectedItemID': BATTLEROYALE_CONSTS.BATTLE_ROYALE_PROGRESS_ID})
