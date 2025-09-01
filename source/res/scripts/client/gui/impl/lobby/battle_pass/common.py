# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/common.py
from account_helpers import AccountSettings
from account_helpers.AccountSettings import EXTRA_CHAPTERS_VIDEO_SHOWN, LAST_BATTLE_PASS_EXTRA_CHAPTER_SEEN, UMG_BATTLE_PASS_EXTRA_CHAPTER_SEEN
from account_helpers.settings_core.settings_constants import BattlePassStorageKeys
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.impl.gen import R
from gui.shared.event_dispatcher import showBrowserOverlayView
from helpers import dependency
from shared_utils import first
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IBattlePassController

@dependency.replace_none_kwargs(battlePass=IBattlePassController)
def getActualBattlePassIDs(layoutID=R.invalid(), chapterID=0, battlePass=None):
    if layoutID:
        return (layoutID, chapterID if battlePass.isChapterExists(chapterID) else battlePass.getCurrentChapterID())
    isPostProgressionActive = battlePass.isPostProgressionActive()
    needToRemindExtraChapter = battlePass.hasExtra() and not isUmgExtraChapterSeen()
    if isPostProgressionActive and needToRemindExtraChapter:
        setUmgExtraChapterSeen()
    if not isIntroVideoShown() or not isExtraVideoShown() or not isIntroShown():
        return (R.aliases.battle_pass.Intro(), chapterID)
    if isPostProgressionActive:
        if needToRemindExtraChapter:
            return (R.aliases.battle_pass.ChapterChoice(), chapterID)
        return (R.aliases.battle_pass.PostProgression(), chapterID)
    if battlePass.isHoliday() and battlePass.isCompleted():
        return (R.aliases.battle_pass.HolidayFinal(), chapterID)
    if battlePass.isChapterExists(chapterID):
        return (R.aliases.battle_pass.Progression(), chapterID)
    return (R.aliases.battle_pass.Progression(), battlePass.getCurrentChapterID()) if battlePass.hasActiveChapter() else (R.aliases.battle_pass.ChapterChoice(), chapterID)


def showOverlayVideo(url, callbackOnClose=None):
    showBrowserOverlayView(url, VIEW_ALIAS.BATTLE_PASS_VIDEO_BROWSER, callbackOnClose=callbackOnClose)


@dependency.replace_none_kwargs(settingsCore=ISettingsCore)
def isIntroVideoShown(settingsCore=None):
    return settingsCore.serverSettings.getBPStorage().get(BattlePassStorageKeys.INTRO_VIDEO_SHOWN)


@dependency.replace_none_kwargs(settingsCore=ISettingsCore)
def setIntroVideoShown(settingsCore=None):
    settingsCore.serverSettings.saveInBPStorage({BattlePassStorageKeys.INTRO_VIDEO_SHOWN: True})


@dependency.replace_none_kwargs(battlePass=IBattlePassController)
def isExtraVideoShown(battlePass=None):
    return not battlePass.hasExtra() or first(battlePass.getExtraChapterIDs()) in AccountSettings.getSettings(EXTRA_CHAPTERS_VIDEO_SHOWN)


@dependency.replace_none_kwargs(battlePass=IBattlePassController)
def setExtraVideoShown(battlePass=None):
    settings = AccountSettings.getSettings(EXTRA_CHAPTERS_VIDEO_SHOWN)
    for extraChapterID in battlePass.getExtraChapterIDs():
        settings.add(extraChapterID)

    AccountSettings.setSettings(EXTRA_CHAPTERS_VIDEO_SHOWN, settings)


@dependency.replace_none_kwargs(settingsCore=ISettingsCore)
def isIntroShown(settingsCore=None):
    return settingsCore.serverSettings.getBPStorage().get(BattlePassStorageKeys.INTRO_SHOWN)


@dependency.replace_none_kwargs(settingsCore=ISettingsCore)
def setIntroShown(settingsCore=None):
    settingsCore.serverSettings.saveInBPStorage({BattlePassStorageKeys.INTRO_SHOWN: True})


def isExtraChapterSeen():
    return AccountSettings.getSettings(LAST_BATTLE_PASS_EXTRA_CHAPTER_SEEN) == getExtraChapterID()


def setExtraChapterSeen():
    AccountSettings.setSettings(LAST_BATTLE_PASS_EXTRA_CHAPTER_SEEN, getExtraChapterID())


def isUmgExtraChapterSeen():
    return AccountSettings.getSettings(UMG_BATTLE_PASS_EXTRA_CHAPTER_SEEN) == getExtraChapterID()


def setUmgExtraChapterSeen():
    AccountSettings.setSettings(UMG_BATTLE_PASS_EXTRA_CHAPTER_SEEN, getExtraChapterID())


@dependency.replace_none_kwargs(battlePass=IBattlePassController)
def getExtraChapterID(battlePass=None):
    return first(battlePass.getExtraChapterIDs(), 0)
