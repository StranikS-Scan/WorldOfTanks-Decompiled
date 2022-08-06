# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/asynchat.py
import asyncore
import errno
import socket
from collections import deque
from sys import py3kwarning
from warnings import filterwarnings, catch_warnings
_BLOCKING_IO_ERRORS = (errno.EAGAIN,
 errno.EALREADY,
 errno.EINPROGRESS,
 errno.EWOULDBLOCK)

class async_chat(asyncore.dispatcher):
    ac_in_buffer_size = 4096
    ac_out_buffer_size = 4096

    def __init__(self, sock=None, map=None):
        self.ac_in_buffer = ''
        self.incoming = []
        self.producer_fifo = deque()
        asyncore.dispatcher.__init__(self, sock, map)

    def collect_incoming_data(self, data):
        raise NotImplementedError('must be implemented in subclass')

    def _collect_incoming_data(self, data):
        self.incoming.append(data)

    def _get_data(self):
        d = ''.join(self.incoming)
        del self.incoming[:]
        return d

    def found_terminator(self):
        raise NotImplementedError('must be implemented in subclass')

    def set_terminator(self, term):
        self.terminator = term

    def get_terminator(self):
        return self.terminator

    def handle_read(self):
        try:
            data = self.recv(self.ac_in_buffer_size)
        except socket.error as why:
            if why.args[0] in _BLOCKING_IO_ERRORS:
                return
            self.handle_error()
            return

        self.ac_in_buffer = self.ac_in_buffer + data
        while self.ac_in_buffer:
            lb = len(self.ac_in_buffer)
            terminator = self.get_terminator()
            if not terminator:
                self.collect_incoming_data(self.ac_in_buffer)
                self.ac_in_buffer = ''
            if isinstance(terminator, (int, long)):
                n = terminator
                if lb < n:
                    self.collect_incoming_data(self.ac_in_buffer)
                    self.ac_in_buffer = ''
                    self.terminator = self.terminator - lb
                else:
                    self.collect_incoming_data(self.ac_in_buffer[:n])
                    self.ac_in_buffer = self.ac_in_buffer[n:]
                    self.terminator = 0
                    self.found_terminator()
            terminator_len = len(terminator)
            index = self.ac_in_buffer.find(terminator)
            if index != -1:
                if index > 0:
                    self.collect_incoming_data(self.ac_in_buffer[:index])
                self.ac_in_buffer = self.ac_in_buffer[index + terminator_len:]
                self.found_terminator()
            index = find_prefix_at_end(self.ac_in_buffer, terminator)
            if index:
                if index != lb:
                    self.collect_incoming_data(self.ac_in_buffer[:-index])
                    self.ac_in_buffer = self.ac_in_buffer[-index:]
                break
            self.collect_incoming_data(self.ac_in_buffer)
            self.ac_in_buffer = ''

    def handle_write(self):
        self.initiate_send()

    def handle_close(self):
        self.close()

    def push(self, data):
        sabs = self.ac_out_buffer_size
        if len(data) > sabs:
            for i in xrange(0, len(data), sabs):
                self.producer_fifo.append(data[i:i + sabs])

        else:
            self.producer_fifo.append(data)
        self.initiate_send()

    def push_with_producer(self, producer):
        self.producer_fifo.append(producer)
        self.initiate_send()

    def readable(self):
        pass

    def writable(self):
        return self.producer_fifo or not self.connected

    def close_when_done(self):
        self.producer_fifo.append(None)
        return

    def initiate_send(self):
        while self.producer_fifo and self.connected:
            first = self.producer_fifo[0]
            if not first:
                del self.producer_fifo[0]
                if first is None:
                    self.handle_close()
                    return
            obs = self.ac_out_buffer_size
            try:
                with catch_warnings():
                    if py3kwarning:
                        filterwarnings('ignore', '.*buffer', DeprecationWarning)
                    data = buffer(first, 0, obs)
            except TypeError:
                data = first.more()
                if data:
                    self.producer_fifo.appendleft(data)
                del self.producer_fifo[0]
                continue

            try:
                num_sent = self.send(data)
            except socket.error:
                self.handle_error()
                return

            if num_sent:
                if num_sent < len(data) or obs < len(first):
                    self.producer_fifo[0] = first[num_sent:]
                else:
                    del self.producer_fifo[0]
            return

        return

    def discard_buffers(self):
        self.ac_in_buffer = ''
        del self.incoming[:]
        self.producer_fifo.clear()


class simple_producer:

    def __init__(self, data, buffer_size=512):
        self.data = data
        self.buffer_size = buffer_size

    def more(self):
        if len(self.data) > self.buffer_size:
            result = self.data[:self.buffer_size]
            self.data = self.data[self.buffer_size:]
            return result
        else:
            result = self.data
            self.data = ''
            return result


class fifo:

    def __init__(self, list=None):
        if not list:
            self.list = deque()
        else:
            self.list = deque(list)

    def __len__(self):
        return len(self.list)

    def is_empty(self):
        return not self.list

    def first(self):
        return self.list[0]

    def push(self, data):
        self.list.append(data)

    def pop(self):
        if self.list:
            return (1, self.list.popleft())
        else:
            return (0, None)
            return None


def find_prefix_at_end(haystack, needle):
    l = len(needle) - 1
    while l and not haystack.endswith(needle[:l]):
        l -= 1

    return l
