# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/activate_chapter_confirm_dialog.py
from __future__ import absolute_import
from frameworks.wulf import ViewSettings
from gui.battle_pass.sounds import ACTIVATE_CHAPTER_SOUND_SPACE
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_pass.chapter_confirm_view_model import ChapterConfirmViewModel
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogBaseView
from gui.impl.pub.dialog_window import DialogButtons
from helpers import dependency
from skeletons.gui.game_control import IBattlePassController
from skeletons.gui.shared import IItemsCache
_CONFIRM_RES = R.strings.battle_pass.chapterChoice.confirmation
_CHAPTER_RES = R.strings.battle_pass.chapter

class ChapterConfirm(FullScreenDialogBaseView):
    __slots__ = ('__chapterID',)
    __itemsCache = dependency.descriptor(IItemsCache)
    __battlePass = dependency.descriptor(IBattlePassController)
    _COMMON_SOUND_SPACE = ACTIVATE_CHAPTER_SOUND_SPACE

    def __init__(self, chapterID=None, *args, **kwargs):
        settings = ViewSettings(layoutID=R.views.mono.battle_pass.dialogs.chapter_confirm(), model=ChapterConfirmViewModel())
        settings.args = args
        settings.kwargs = kwargs
        self.__chapterID = chapterID
        super(ChapterConfirm, self).__init__(settings)

    @property
    def viewModel(self):
        return super(ChapterConfirm, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(ChapterConfirm, self)._onLoading(self, *args, **kwargs)
        with self.viewModel.transaction() as model:
            model.setPrevChapter(self.__battlePass.getCurrentChapterID())
            model.setNextChapter(self.__chapterID)
            model.setIsSwitchFromPostProgressionToExtraChapter(self.__battlePass.isPostProgressionActive() and self.__battlePass.isExtraChapter(self.__chapterID))

    def _getEvents(self):
        events = super(ChapterConfirm, self)._getEvents()
        return events + ((self.viewModel.onAccept, self._onAccept), (self.viewModel.onCancel, self._onCancel), (self.__battlePass.onSeasonStateChanged, self.__onSeasonStateChanged))

    def _onAccept(self):
        self._setResult(DialogButtons.SUBMIT)

    def _onCancel(self):
        self._setResult(DialogButtons.CANCEL)

    def __onSeasonStateChanged(self):
        if not self.__battlePass.isActive():
            self.destroyWindow()
