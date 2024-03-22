# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/vse_hud_settings_ctrl/settings/chat.py


class ChatModel(object):
    __slots__ = ('hide',)

    def __init__(self, hide):
        super(ChatModel, self).__init__()
        self.hide = hide

    def __repr__(self):
        return '<ChatModel>: hide=%s' % self.hide
