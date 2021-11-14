# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/account_completion/contact_support_overlay_view.py
from adisp import process
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.account_completion.contact_support_model import ContactSupportModel
from gui.impl.lobby.account_completion.common.base_overlay_view import BaseOverlayView
from gui.impl.lobby.account_completion.utils.common import openMenu, SUPPORT_URL
from helpers import dependency
from skeletons.gui.game_control import IExternalLinksController

class ContactSupportOverlayView(BaseOverlayView):
    __slots__ = ('_isCloseVisible',)
    _links = dependency.instance(IExternalLinksController)
    _LAYOUT_DYN_ACCESSOR = R.views.lobby.account_completion.ContactSupportView
    _VIEW_MODEL_CLASS = ContactSupportModel

    def __init__(self):
        super(ContactSupportOverlayView, self).__init__()
        self._isCloseVisible = True

    @property
    def viewModel(self):
        return super(ContactSupportOverlayView, self).getViewModel()

    def activate(self, message, isCloseVisible=True, *args, **kwargs):
        super(ContactSupportOverlayView, self).activate(*args, **kwargs)
        self.viewModel.onContactClicked += self._contactClickedHandler
        with self.viewModel.transaction() as model:
            model.setMessage(message)
            model.setIsCloseVisible(isCloseVisible)
        self._isCloseVisible = isCloseVisible

    def deactivate(self):
        super(ContactSupportOverlayView, self).deactivate()
        self.viewModel.onContactClicked -= self._contactClickedHandler

    def _escapePressHandler(self):
        if not self._isCloseVisible:
            openMenu()

    @process
    def _contactClickedHandler(self):
        parsedUrl = yield self._links.getURL(SUPPORT_URL)
        self._links.open(parsedUrl)
