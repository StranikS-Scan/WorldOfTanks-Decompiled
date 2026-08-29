# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/hangar/presenters/main_plugins_presenter.py
from __future__ import absolute_import
import logging
from gui.impl.gen.view_models.views.lobby.hangar.main_plugins_model import MainPluginsModel
from gui.impl.pub.view_component import ViewComponent
_logger = logging.getLogger(__name__)

class MainPluginsPresenter(ViewComponent[MainPluginsModel]):

    def __init__(self):
        super(MainPluginsPresenter, self).__init__(model=MainPluginsModel)

    @property
    def viewModel(self):
        return super(MainPluginsPresenter, self).getViewModel()
