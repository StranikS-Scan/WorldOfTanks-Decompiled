# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/dialogs/default_dialog_place_holders.py
from frameworks.wulf import ViewModel

class DefaultDialogPlaceHolders(ViewModel):
    __slots__ = ()
    TOP_RIGHT = 'topRight'
    ICON = 'icon'
    TITLE = 'title'
    CONTENT = 'content'
    FOOTER = 'footer'

    def __init__(self, properties=0, commands=0):
        super(DefaultDialogPlaceHolders, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(DefaultDialogPlaceHolders, self)._initialize()
