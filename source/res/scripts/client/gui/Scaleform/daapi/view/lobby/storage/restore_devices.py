# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/storage/restore_devices.py
from gui.Scaleform.daapi.view.meta.StorageRestoreDevicesViewMeta import StorageRestoreDevicesViewMeta
from gui.Scaleform.locale.STORAGE import STORAGE
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.event_dispatcher import showStorage
from gui.Scaleform.genConsts.STORAGE_CONSTANTS import STORAGE_CONSTANTS

class StorageRestoreDevicesView(StorageRestoreDevicesViewMeta):

    def __init__(self, ctx=None):
        super(StorageRestoreDevicesView, self).__init__(ctx)
        context = ctx or {}
        self._backBtnLabel = context.get('backBtnLabel')

    def _populate(self):
        super(StorageRestoreDevicesView, self)._populate()
        self.as_setDataS({'bgSource': backport.image(R.images.gui.maps.icons.storage.background()),
         'titleLabel': STORAGE.DEVICES_RESTORE_TITLE,
         'backBtn': STORAGE.DEVICES_RESTORE_GOBACK,
         'backBtnLabel': self._backBtnLabel or STORAGE.DEVICES_RESTORE_GOBACKTOSECTIONS})

    def onBackClick(self):
        self.destroy()
        showStorage(defaultSection=STORAGE_CONSTANTS.STORAGE, tabId=STORAGE_CONSTANTS.INVENTORY_TAB_EQUIPMENT)
