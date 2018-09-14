# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/dialogs/bootcamp_dialogs.py
from gui.Scaleform.daapi.view.meta.BootcampDialogMeta import BootcampDialogMeta

class ExecutionChooserDialog(BootcampDialogMeta):

    def __init__(self, meta, handler):
        super(ExecutionChooserDialog, self).__init__(meta.getMessage(), meta.getTitle(), meta.getButtonLabels(), meta.getCallbackWrapper(handler))
        self.__imagePath = meta.getImagePath()
        self.__label = meta.getLabel()
        self.__showAwardIcon = meta.getShowAwardIcon()
        self.__awardingText = meta.getAwardingText()

    def _populate(self):
        super(ExecutionChooserDialog, self)._populate()
        self.as_setDataS(self.__imagePath, self.__label, self.__showAwardIcon, self.__awardingText)
