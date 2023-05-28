# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/achievements/dialogs/achievement_edit_confirm.py
import typing
from BWUtil import AsyncReturn
from PlayerEvents import g_playerEvents
from constants import Configs
from frameworks.wulf import ViewSettings
from gui.impl.dialogs.dialogs import showSingleDialogWithResultData
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.achievements.dialogs.edit_confirm_model import EditConfirmModel, DialogType
from gui.impl.lobby.achievements.profile_utils import isLayoutEnabled, isSummaryEnabled
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogView
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from helpers import dependency, server_settings
from skeletons.gui.lobby_context import ILobbyContext
from wg_async import wg_async, wg_await
if typing.TYPE_CHECKING:
    from typing import Dict
    from frameworks.wulf import Window

class EditConfirm(FullScreenDialogView):
    __slots__ = ('__dialogType', '__additionalData')
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, dialogType):
        settings = ViewSettings(R.views.lobby.achievements.dialogs.EditConfirm(), model=EditConfirmModel())
        self.__dialogType = dialogType
        self.__additionalData = {}
        super(EditConfirm, self).__init__(settings)

    @property
    def viewModel(self):
        return super(EditConfirm, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(EditConfirm, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as model:
            model.setDialogType(self.__dialogType)

    def _addListeners(self):
        pass

    def _getEvents(self):
        return ((self.viewModel.onAccept, self._onAccept),
         (self.viewModel.onCancel, self.__onCancelAction),
         (self.viewModel.onClose, self._onExitClicked),
         (g_playerEvents.onAccountBecomeNonPlayer, self.destroyWindow),
         (self.__lobbyContext.getServerSettings().onServerSettingsChange, self.__onServerSettingsChanged))

    def _removeListeners(self):
        pass

    def _setBaseParams(self, model):
        pass

    def _getAdditionalData(self):
        return self.__additionalData

    def __onCancelAction(self):
        self.__additionalData['isUserCancelAction'] = True
        self._onCancel()

    @server_settings.serverSettingsChangeListener(Configs.ACHIEVEMENTS20_CONFIG.value)
    def __onServerSettingsChanged(self, diff):
        if not isLayoutEnabled() or not isSummaryEnabled():
            self.__showErrorState()

    @replaceNoneKwargsModel
    def __showErrorState(self, model=None):
        self.__dialogType = DialogType.ERROR
        model.setDialogType(self.__dialogType)


@wg_async
def showDialog(dialogType, parent):
    result = yield wg_await(showSingleDialogWithResultData(layoutID=R.views.lobby.achievements.dialogs.EditConfirm(), dialogType=dialogType, parent=parent, wrappedViewClass=EditConfirm))
    raise AsyncReturn(result)
