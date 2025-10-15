# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/notify_center/notify_center_helpers.py
from debug_utils import LOG_ERROR
from gui.shared.view_helpers.UsersInfoHelper import UsersInfoHelper

def parseSize(sizeStr):
    if sizeStr:
        try:
            size = tuple(map(int, sizeStr.split('x')))
            if len(size) != 2:
                return
        except ValueError:
            LOG_ERROR('Failed to parse size: %s' % sizeStr)
            size = None

    else:
        size = None
    return size


def spa2Nickname(value):
    helper = UsersInfoHelper()
    contact = helper.getContact(value)
    name = '<font color="#DFDFDF">{}</font>'.format(contact.getName())
    clanAbbrev = '<font color="#8C8C7E">[{}]</font>'.format(contact.getClanAbbrev()) if contact.getClanAbbrev() else ''
    return '{}{}'.format(name, clanAbbrev)
