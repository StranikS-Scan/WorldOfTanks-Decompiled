# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/activate_chapter_confirm_dialog.py
from frameworks.wulf import ViewFlags, ViewSettings
from gui.battle_pass.sounds import ACTIVATE_CHAPTER_SOUND_SPACE
from gui.impl.dialogs.dialog_template import DialogTemplateView
from gui.impl.dialogs.dialog_template_button import CancelButton, ConfirmButton
from gui.impl.gen import R
from gui.impl.gen.view_models.views.dialogs.default_dialog_place_holders import DefaultDialogPlaceHolders
from gui.impl.gen.view_models.views.lobby.battle_pass.chapter_confirm_view_model import ChapterConfirmViewModel
from gui.impl.pub import ViewImpl
from gui.shared.event_dispatcher import showHangar
from helpers import dependency
from skeletons.gui.game_control import IBattlePassController
_CONFIRM_RES = R.strings.battle_pass.chapterChoice.confirmation
_CHAPTER_RES = R.strings.battle_pass.chapter

class ChapterConfirm(ViewImpl):
    __slots__ = ('__prevChapterID', '__nextChapterID')
    __battlePass = dependency.descriptor(IBattlePassController)
    _COMMON_SOUND_SPACE = ACTIVATE_CHAPTER_SOUND_SPACE

    def __init__(self, prevChapterID, nextChapterID):
        settings = ViewSettings(R.views.lobby.battle_pass.dialogs.ChapterConfirm())
        settings.flags = ViewFlags.VIEW
        settings.model = ChapterConfirmViewModel()
        super(ChapterConfirm, self).__init__(settings)
        self.__prevChapterID = prevChapterID
        self.__nextChapterID = nextChapterID

    @property
    def viewModel(self):
        return super(ChapterConfirm, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(ChapterConfirm, self)._onLoading()
        with self.viewModel.transaction() as model:
            model.setPrevChapter(self.__prevChapterID)
            model.setNextChapter(self.__nextChapterID)


class ActivateChapterConfirmDialog(DialogTemplateView):
    __battlePassController = dependency.descriptor(IBattlePassController)

    def __init__(self, chapterID=None):
        super(ActivateChapterConfirmDialog, self).__init__()
        self.__nextChapterID = chapterID

    def _onLoading(self, *args, **kwargs):
        prevChapterID = self.__battlePassController.getCurrentChapterID()
        self.setSubView(DefaultDialogPlaceHolders.CONTENT, ChapterConfirm(prevChapterID, self.__nextChapterID))
        self.addButton(ConfirmButton(_CONFIRM_RES.button.submit() if prevChapterID == 0 else _CONFIRM_RES.button.switch()))
        self.addButton(CancelButton(_CONFIRM_RES.button.cancel()))
        super(ActivateChapterConfirmDialog, self)._onLoading(*args, **kwargs)

    def _getAdditionalData(self):
        return {}

    def _getEvents(self):
        return ((self.__battlePassController.onSeasonStateChanged, self.__onSeasonStateChanged),)

    def __onSeasonStateChanged(self):
        if not self.__battlePassController.isActive():
            showHangar()
            self._closeClickHandler()
