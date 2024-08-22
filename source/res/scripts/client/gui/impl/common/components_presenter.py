# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/common/components_presenter.py
import typing
from gui.impl.common.base_sub_model_view import BaseSubModelView
from gui.impl.pub import ViewImpl
if typing.TYPE_CHECKING:
    from frameworks.wulf import View, ViewEvent, Window

class ComponentsPresenterView(ViewImpl):

    def __init__(self, settings):
        self.__componentPresenters = []
        super(ComponentsPresenterView, self).__init__(settings)

    def _onLoading(self, *args, **kwargs):
        super(ComponentsPresenterView, self)._onLoading(args, kwargs)
        self.__componentPresenters.extend(self._registerSubModels())
        for presenter in self.__componentPresenters:
            presenter.initialize()

    def _finalize(self):
        for presenter in self.__componentPresenters:
            presenter.finalize()

        self.__componentPresenters = None
        super(ComponentsPresenterView, self)._finalize()
        return

    def createToolTipContent(self, event, contentID):
        for presenter in self.__componentPresenters:
            content = presenter.createToolTipContent(event, contentID)
            if content is not None:
                return content

        return super(ComponentsPresenterView, self).createToolTipContent(event, contentID)

    def createToolTip(self, event):
        for presenter in self.__componentPresenters:
            content = presenter.createToolTip(event)
            if content is not None:
                return content

        return super(ComponentsPresenterView, self).createToolTip(event)

    def createPopOverContent(self, event):
        for presenter in self.__componentPresenters:
            content = presenter.createPopOverContent(event)
            if content is not None:
                return content

        return

    def _registerSubModels(self):
        raise NotImplementedError


class BaseSubModelViewWithToolTips(BaseSubModelView):

    def createToolTipContent(self, event, contentID):
        return None

    def createPopOverContent(self, event):
        return None

    def createToolTip(self, event):
        return None
