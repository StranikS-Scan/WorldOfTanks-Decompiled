# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/pub/ny_info_dialog_window.py
from gui.impl.lobby.dialogs.contents.common_balance_content import CommonBalanceContent
from gui.impl.pub.simple_dialog_window import SimpleDialogWindow

class NYInfoDialogWindow(SimpleDialogWindow):

    def __init__(self, *args, **kwargs):
        if kwargs.get('balanceContent') is not None:
            kwargs['balanceContent'] = CommonBalanceContent()
        super(NYInfoDialogWindow, self).__init__(*args, **kwargs)
        return
