# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: open_bundle/scripts/client/open_bundle/gui/shared/event_dispatcher.py
from __future__ import absolute_import
from gui.impl.gen import R
from wg_async import wg_async, wg_await

def showOpenBundleMainView(bundleID):
    from open_bundle.gui.impl.lobby.states import OpenBundleState
    OpenBundleState.goTo(bundleID=bundleID)


def showIntro(bundleID):
    from open_bundle.gui.impl.lobby.intro_view import IntroWindow
    window = IntroWindow(bundleID)
    window.load()


@wg_async
def showOpenBundleConfirmDialog(bundleID, stepNumber, parent=None, callback=None):
    from gui.impl.dialogs import dialogs
    from open_bundle.gui.impl.lobby.confirmation_view import ConfirmationView
    result = yield wg_await(dialogs.showSingleDialogWithResultData(layoutID=R.views.open_bundle.mono.lobby.confirmation(), parent=parent, wrappedViewClass=ConfirmationView, bundleID=bundleID, stepNumber=stepNumber))
    if result.busy:
        callback((False, {}))
    else:
        isOK, data = result.result
        callback((isOK, data))


def showAttachmentsPreview(bundleID, attachmentsToken):
    from open_bundle.gui.impl.lobby.attachments_preview import AttachmentsPreviewWindow
    window = AttachmentsPreviewWindow(bundleID, attachmentsToken)
    window.load()
