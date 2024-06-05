# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/dog_tags/customization_confirm_dialog.py
import logging
import BigWorld
import typing
from frameworks.wulf import ViewSettings
from constants import DOG_TAGS_CONFIG
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.dog_tags.customization_confirm_dialog_model import CustomizationConfirmDialogModel
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogBaseView
from gui.impl.lobby.dog_tags.dog_tag_composer import DogTagComposerLobby
from gui.impl.pub.dialog_window import DialogButtons
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.web import IWebController
if typing.TYPE_CHECKING:
    from account_helpers.dog_tags import DogTags as DogTagsAccountHelper
_logger = logging.getLogger(__name__)

class CustomizationConfirmDialog(FullScreenDialogBaseView):
    __slots__ = ('__dogTagsHelper', '__composer', '__backgroundId', '__engravingId', '__additionalData', '__isLocked')
    _webCtrl = dependency.descriptor(IWebController)
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, backgroundId, engravingId):
        settings = ViewSettings(R.views.lobby.dog_tags.CustomizationConfirmDialog())
        settings.model = CustomizationConfirmDialogModel()
        self.__dogTagsHelper = BigWorld.player().dogTags
        self.__composer = DogTagComposerLobby(self.__dogTagsHelper)
        self.__backgroundId = backgroundId
        self.__engravingId = engravingId
        self.__additionalData = {}
        self.__isLocked = None
        super(CustomizationConfirmDialog, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return super(CustomizationConfirmDialog, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(CustomizationConfirmDialog, self)._onLoading()
        unlockedComps = self.__dogTagsHelper.getUnlockedComps()
        self.__isLocked = self.__backgroundId not in unlockedComps or self.__engravingId not in unlockedComps
        dogTag = self.__dogTagsHelper.getDisplayableDTForComponents([self.__backgroundId, self.__engravingId], self._webCtrl.getAccountProfile())
        with self.viewModel.transaction() as tx:
            if dogTag:
                self.__composer.fillModel(tx.equippedDogTag, dogTag, isUnlocked=not self.__isLocked)
        self.__addListeners()

    def __onClose(self):
        self._setResult(DialogButtons.CANCEL)

    def __onConfirm(self):
        if not self.__isLocked:
            self.__additionalData['saveChanges'] = True
            self._setResult(DialogButtons.SUBMIT)
        else:
            self._setResult(DialogButtons.CANCEL)

    def __onDiscard(self):
        self.__additionalData['saveChanges'] = False
        self._setResult(DialogButtons.SUBMIT)

    def _getAdditionalData(self):
        return self.__additionalData

    def __addListeners(self):
        self.viewModel.onConfirm += self.__onConfirm
        self.viewModel.onClose += self.__onClose
        self.viewModel.onDiscard += self.__onDiscard
        self.lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChange

    def __removeListeners(self):
        self.viewModel.onConfirm -= self.__onConfirm
        self.viewModel.onClose -= self.__onClose
        self.viewModel.onDiscard -= self.__onDiscard
        self.lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChange

    def _finalize(self):
        self.__removeListeners()
        super(CustomizationConfirmDialog, self)._finalize()

    def __onServerSettingsChange(self, diff):
        if DOG_TAGS_CONFIG in diff:
            if not self.lobbyContext.getServerSettings().isDogTagCustomizationScreenEnabled():
                self.destroyWindow()
