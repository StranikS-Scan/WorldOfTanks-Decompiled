# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/exeptions.py
# Compiled at: 2011-07-29 13:15:51
import exceptions

class ChannelNotFound(exceptions.Exception):

    def __init__(self, cid, *args, **kwargs):
        super(ChannelNotFound, self).__init__(*args, **kwargs)
        self.cid = cid

    def __str__(self):
        return 'Not found a channel with id = %d, the first request from the server information on the channel with this id' % self.cid
