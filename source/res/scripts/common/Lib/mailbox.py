# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/mailbox.py
import sys
import os
import time
import calendar
import socket
import errno
import copy
import email
import email.message
import email.generator
import StringIO
try:
    if sys.platform == 'os2emx':
        raise ImportError
    import fcntl
except ImportError:
    fcntl = None

import warnings
with warnings.catch_warnings():
    if sys.py3kwarning:
        warnings.filterwarnings('ignore', '.*rfc822 has been removed', DeprecationWarning)
    import rfc822
__all__ = ['Mailbox',
 'Maildir',
 'mbox',
 'MH',
 'Babyl',
 'MMDF',
 'Message',
 'MaildirMessage',
 'mboxMessage',
 'MHMessage',
 'BabylMessage',
 'MMDFMessage',
 'UnixMailbox',
 'PortableUnixMailbox',
 'MmdfMailbox',
 'MHMailbox',
 'BabylMailbox']

class Mailbox():

    def __init__(self, path, factory=None, create=True):
        self._path = os.path.abspath(os.path.expanduser(path))
        self._factory = factory

    def add(self, message):
        raise NotImplementedError('Method must be implemented by subclass')

    def remove(self, key):
        raise NotImplementedError('Method must be implemented by subclass')

    def __delitem__(self, key):
        self.remove(key)

    def discard(self, key):
        try:
            self.remove(key)
        except KeyError:
            pass

    def __setitem__(self, key, message):
        raise NotImplementedError('Method must be implemented by subclass')

    def get(self, key, default=None):
        try:
            return self.__getitem__(key)
        except KeyError:
            return default

    def __getitem__(self, key):
        if not self._factory:
            return self.get_message(key)
        else:
            return self._factory(self.get_file(key))

    def get_message(self, key):
        raise NotImplementedError('Method must be implemented by subclass')

    def get_string(self, key):
        raise NotImplementedError('Method must be implemented by subclass')

    def get_file(self, key):
        raise NotImplementedError('Method must be implemented by subclass')

    def iterkeys(self):
        raise NotImplementedError('Method must be implemented by subclass')

    def keys(self):
        return list(self.iterkeys())

    def itervalues(self):
        for key in self.iterkeys():
            try:
                value = self[key]
            except KeyError:
                continue

            yield value

    def __iter__(self):
        return self.itervalues()

    def values(self):
        return list(self.itervalues())

    def iteritems(self):
        for key in self.iterkeys():
            try:
                value = self[key]
            except KeyError:
                continue

            yield (key, value)

    def items(self):
        return list(self.iteritems())

    def has_key(self, key):
        raise NotImplementedError('Method must be implemented by subclass')

    def __contains__(self, key):
        return self.has_key(key)

    def __len__(self):
        raise NotImplementedError('Method must be implemented by subclass')

    def clear(self):
        for key in self.iterkeys():
            self.discard(key)

    def pop(self, key, default=None):
        try:
            result = self[key]
        except KeyError:
            return default

        self.discard(key)
        return result

    def popitem(self):
        for key in self.iterkeys():
            return (key, self.pop(key))
        else:
            raise KeyError('No messages in mailbox')

    def update(self, arg=None):
        if hasattr(arg, 'iteritems'):
            source = arg.iteritems()
        elif hasattr(arg, 'items'):
            source = arg.items()
        else:
            source = arg
        bad_key = False
        for key, message in source:
            try:
                self[key] = message
            except KeyError:
                bad_key = True

        if bad_key:
            raise KeyError('No message with key(s)')

    def flush(self):
        raise NotImplementedError('Method must be implemented by subclass')

    def lock(self):
        raise NotImplementedError('Method must be implemented by subclass')

    def unlock(self):
        raise NotImplementedError('Method must be implemented by subclass')

    def close(self):
        raise NotImplementedError('Method must be implemented by subclass')

    _append_newline = False

    def _dump_message(self, message, target, mangle_from_=False):
        if isinstance(message, email.message.Message):
            buffer = StringIO.StringIO()
            gen = email.generator.Generator(buffer, mangle_from_, 0)
            gen.flatten(message)
            buffer.seek(0)
            data = buffer.read().replace('\n', os.linesep)
            target.write(data)
            if self._append_newline and not data.endswith(os.linesep):
                target.write(os.linesep)
        elif isinstance(message, str):
            if mangle_from_:
                message = message.replace('\nFrom ', '\n>From ')
            message = message.replace('\n', os.linesep)
            target.write(message)
            if self._append_newline and not message.endswith(os.linesep):
                target.write(os.linesep)
        elif hasattr(message, 'read'):
            lastline = None
            while True:
                line = message.readline()
                if line == '':
                    break
                if mangle_from_ and line.startswith('From '):
                    line = '>From ' + line[5:]
                line = line.replace('\n', os.linesep)
                target.write(line)
                lastline = line

            if self._append_newline and lastline and not lastline.endswith(os.linesep):
                target.write(os.linesep)
        else:
            raise TypeError('Invalid message type: %s' % type(message))
        return


class Maildir(Mailbox):
    colon = ':'

    def __init__(self, dirname, factory=rfc822.Message, create=True):
        Mailbox.__init__(self, dirname, factory, create)
        self._paths = {'tmp': os.path.join(self._path, 'tmp'),
         'new': os.path.join(self._path, 'new'),
         'cur': os.path.join(self._path, 'cur')}
        if not os.path.exists(self._path):
            if create:
                os.mkdir(self._path, 448)
                for path in self._paths.values():
                    os.mkdir(path, 448)

            else:
                raise NoSuchMailboxError(self._path)
        self._toc = {}
        self._toc_mtimes = {'cur': 0,
         'new': 0}
        self._last_read = 0
        self._skewfactor = 0.1

    def add(self, message):
        tmp_file = self._create_tmp()
        try:
            self._dump_message(message, tmp_file)
        except BaseException:
            tmp_file.close()
            os.remove(tmp_file.name)
            raise

        _sync_close(tmp_file)
        if isinstance(message, MaildirMessage):
            subdir = message.get_subdir()
            suffix = self.colon + message.get_info()
            if suffix == self.colon:
                suffix = ''
        else:
            subdir = 'new'
            suffix = ''
        uniq = os.path.basename(tmp_file.name).split(self.colon)[0]
        dest = os.path.join(self._path, subdir, uniq + suffix)
        if isinstance(message, MaildirMessage):
            os.utime(tmp_file.name, (os.path.getatime(tmp_file.name), message.get_date()))
        try:
            if hasattr(os, 'link'):
                os.link(tmp_file.name, dest)
                os.remove(tmp_file.name)
            else:
                os.rename(tmp_file.name, dest)
        except OSError as e:
            os.remove(tmp_file.name)
            if e.errno == errno.EEXIST:
                raise ExternalClashError('Name clash with existing message: %s' % dest)
            else:
                raise

        return uniq

    def remove(self, key):
        os.remove(os.path.join(self._path, self._lookup(key)))

    def discard(self, key):
        try:
            self.remove(key)
        except KeyError:
            pass
        except OSError as e:
            if e.errno != errno.ENOENT:
                raise

    def __setitem__(self, key, message):
        old_subpath = self._lookup(key)
        temp_key = self.add(message)
        temp_subpath = self._lookup(temp_key)
        if isinstance(message, MaildirMessage):
            dominant_subpath = temp_subpath
        else:
            dominant_subpath = old_subpath
        subdir = os.path.dirname(dominant_subpath)
        if self.colon in dominant_subpath:
            suffix = self.colon + dominant_subpath.split(self.colon)[-1]
        else:
            suffix = ''
        self.discard(key)
        tmp_path = os.path.join(self._path, temp_subpath)
        new_path = os.path.join(self._path, subdir, key + suffix)
        if isinstance(message, MaildirMessage):
            os.utime(tmp_path, (os.path.getatime(tmp_path), message.get_date()))
        os.rename(tmp_path, new_path)

    def get_message(self, key):
        subpath = self._lookup(key)
        f = open(os.path.join(self._path, subpath), 'r')
        try:
            if self._factory:
                msg = self._factory(f)
            else:
                msg = MaildirMessage(f)
        finally:
            f.close()

        subdir, name = os.path.split(subpath)
        msg.set_subdir(subdir)
        if self.colon in name:
            msg.set_info(name.split(self.colon)[-1])
        msg.set_date(os.path.getmtime(os.path.join(self._path, subpath)))
        return msg

    def get_string(self, key):
        f = open(os.path.join(self._path, self._lookup(key)), 'r')
        try:
            return f.read()
        finally:
            f.close()

    def get_file(self, key):
        f = open(os.path.join(self._path, self._lookup(key)), 'rb')
        return _ProxyFile(f)

    def iterkeys(self):
        self._refresh()
        for key in self._toc:
            try:
                self._lookup(key)
            except KeyError:
                continue

            yield key

    def has_key(self, key):
        self._refresh()
        return key in self._toc

    def __len__(self):
        self._refresh()
        return len(self._toc)

    def flush(self):
        pass

    def lock(self):
        pass

    def unlock(self):
        pass

    def close(self):
        pass

    def list_folders(self):
        result = []
        for entry in os.listdir(self._path):
            if len(entry) > 1 and entry[0] == '.' and os.path.isdir(os.path.join(self._path, entry)):
                result.append(entry[1:])

        return result

    def get_folder(self, folder):
        return Maildir(os.path.join(self._path, '.' + folder), factory=self._factory, create=False)

    def add_folder(self, folder):
        path = os.path.join(self._path, '.' + folder)
        result = Maildir(path, factory=self._factory)
        maildirfolder_path = os.path.join(path, 'maildirfolder')
        if not os.path.exists(maildirfolder_path):
            os.close(os.open(maildirfolder_path, os.O_CREAT | os.O_WRONLY, 438))
        return result

    def remove_folder(self, folder):
        path = os.path.join(self._path, '.' + folder)
        for entry in os.listdir(os.path.join(path, 'new')) + os.listdir(os.path.join(path, 'cur')):
            if len(entry) < 1 or entry[0] != '.':
                raise NotEmptyError('Folder contains message(s): %s' % folder)

        for entry in os.listdir(path):
            if entry != 'new' and entry != 'cur' and entry != 'tmp' and os.path.isdir(os.path.join(path, entry)):
                raise NotEmptyError("Folder contains subdirectory '%s': %s" % (folder, entry))

        for root, dirs, files in os.walk(path, topdown=False):
            for entry in files:
                os.remove(os.path.join(root, entry))

            for entry in dirs:
                os.rmdir(os.path.join(root, entry))

        os.rmdir(path)

    def clean(self):
        now = time.time()
        for entry in os.listdir(os.path.join(self._path, 'tmp')):
            path = os.path.join(self._path, 'tmp', entry)
            if now - os.path.getatime(path) > 129600:
                os.remove(path)

    _count = 1

    def _create_tmp(self):
        now = time.time()
        hostname = socket.gethostname()
        if '/' in hostname:
            hostname = hostname.replace('/', '\\057')
        if ':' in hostname:
            hostname = hostname.replace(':', '\\072')
        uniq = '%s.M%sP%sQ%s.%s' % (int(now),
         int(now % 1 * 1000000.0),
         os.getpid(),
         Maildir._count,
         hostname)
        path = os.path.join(self._path, 'tmp', uniq)
        try:
            os.stat(path)
        except OSError as e:
            if e.errno == errno.ENOENT:
                Maildir._count += 1
                try:
                    return _create_carefully(path)
                except OSError as e:
                    if e.errno != errno.EEXIST:
                        raise

            else:
                raise

        raise ExternalClashError('Name clash prevented file creation: %s' % path)

    def _refresh(self):
        if time.time() - self._last_read > 2 + self._skewfactor:
            refresh = False
            for subdir in self._toc_mtimes:
                mtime = os.path.getmtime(self._paths[subdir])
                if mtime > self._toc_mtimes[subdir]:
                    refresh = True
                self._toc_mtimes[subdir] = mtime

            if not refresh:
                return
        self._toc = {}
        for subdir in self._toc_mtimes:
            path = self._paths[subdir]
            for entry in os.listdir(path):
                p = os.path.join(path, entry)
                if os.path.isdir(p):
                    continue
                uniq = entry.split(self.colon)[0]
                self._toc[uniq] = os.path.join(subdir, entry)

        self._last_read = time.time()

    def _lookup(self, key):
        try:
            if os.path.exists(os.path.join(self._path, self._toc[key])):
                return self._toc[key]
        except KeyError:
            pass

        self._refresh()
        try:
            return self._toc[key]
        except KeyError:
            raise KeyError('No message with key: %s' % key)

    def next(self):
        if not hasattr(self, '_onetime_keys'):
            self._onetime_keys = self.iterkeys()
        while True:
            try:
                return self[self._onetime_keys.next()]
            except StopIteration:
                return None
            except KeyError:
                continue

        return None


class _singlefileMailbox(Mailbox):

    def __init__(self, path, factory=None, create=True):
        Mailbox.__init__(self, path, factory, create)
        try:
            f = open(self._path, 'rb+')
        except IOError as e:
            if e.errno == errno.ENOENT:
                if create:
                    f = open(self._path, 'wb+')
                else:
                    raise NoSuchMailboxError(self._path)
            elif e.errno in (errno.EACCES, errno.EROFS):
                f = open(self._path, 'rb')
            else:
                raise

        self._file = f
        self._toc = None
        self._next_key = 0
        self._pending = False
        self._pending_sync = False
        self._locked = False
        self._file_length = None
        return

    def add(self, message):
        self._lookup()
        self._toc[self._next_key] = self._append_message(message)
        self._next_key += 1
        self._pending_sync = True
        return self._next_key - 1

    def remove(self, key):
        self._lookup(key)
        del self._toc[key]
        self._pending = True

    def __setitem__(self, key, message):
        self._lookup(key)
        self._toc[key] = self._append_message(message)
        self._pending = True

    def iterkeys(self):
        self._lookup()
        for key in self._toc.keys():
            yield key

    def has_key(self, key):
        self._lookup()
        return key in self._toc

    def __len__(self):
        self._lookup()
        return len(self._toc)

    def lock(self):
        if not self._locked:
            _lock_file(self._file)
            self._locked = True

    def unlock(self):
        if self._locked:
            _unlock_file(self._file)
            self._locked = False

    def flush(self):
        if not self._pending:
            if self._pending_sync:
                _sync_flush(self._file)
                self._pending_sync = False
            return
        self._file.seek(0, 2)
        cur_len = self._file.tell()
        if cur_len != self._file_length:
            raise ExternalClashError('Size of mailbox file changed (expected %i, found %i)' % (self._file_length, cur_len))
        new_file = _create_temporary(self._path)
        try:
            new_toc = {}
            self._pre_mailbox_hook(new_file)
            for key in sorted(self._toc.keys()):
                start, stop = self._toc[key]
                self._file.seek(start)
                self._pre_message_hook(new_file)
                new_start = new_file.tell()
                while True:
                    buffer = self._file.read(min(4096, stop - self._file.tell()))
                    if buffer == '':
                        break
                    new_file.write(buffer)

                new_toc[key] = (new_start, new_file.tell())
                self._post_message_hook(new_file)

            self._file_length = new_file.tell()
        except:
            new_file.close()
            os.remove(new_file.name)
            raise

        _sync_close(new_file)
        self._file.close()
        mode = os.stat(self._path).st_mode
        os.chmod(new_file.name, mode)
        try:
            os.rename(new_file.name, self._path)
        except OSError as e:
            if e.errno == errno.EEXIST or os.name == 'os2' and e.errno == errno.EACCES:
                os.remove(self._path)
                os.rename(new_file.name, self._path)
            else:
                raise

        self._file = open(self._path, 'rb+')
        self._toc = new_toc
        self._pending = False
        self._pending_sync = False
        if self._locked:
            _lock_file(self._file, dotlock=False)

    def _pre_mailbox_hook(self, f):
        pass

    def _pre_message_hook(self, f):
        pass

    def _post_message_hook(self, f):
        pass

    def close(self):
        self.flush()
        if self._locked:
            self.unlock()
        self._file.close()

    def _lookup(self, key=None):
        if self._toc is None:
            self._generate_toc()
        if key is not None:
            try:
                return self._toc[key]
            except KeyError:
                raise KeyError('No message with key: %s' % key)

        return

    def _append_message(self, message):
        self._file.seek(0, 2)
        before = self._file.tell()
        if len(self._toc) == 0 and not self._pending:
            self._pre_mailbox_hook(self._file)
        try:
            self._pre_message_hook(self._file)
            offsets = self._install_message(message)
            self._post_message_hook(self._file)
        except BaseException:
            self._file.truncate(before)
            raise

        self._file.flush()
        self._file_length = self._file.tell()
        return offsets


class _mboxMMDF(_singlefileMailbox):
    _mangle_from_ = True

    def get_message(self, key):
        start, stop = self._lookup(key)
        self._file.seek(start)
        from_line = self._file.readline().replace(os.linesep, '')
        string = self._file.read(stop - self._file.tell())
        msg = self._message_factory(string.replace(os.linesep, '\n'))
        msg.set_from(from_line[5:])
        return msg

    def get_string(self, key, from_=False):
        start, stop = self._lookup(key)
        self._file.seek(start)
        if not from_:
            self._file.readline()
        string = self._file.read(stop - self._file.tell())
        return string.replace(os.linesep, '\n')

    def get_file(self, key, from_=False):
        start, stop = self._lookup(key)
        self._file.seek(start)
        if not from_:
            self._file.readline()
        return _PartialFile(self._file, self._file.tell(), stop)

    def _install_message(self, message):
        from_line = None
        if isinstance(message, str) and message.startswith('From '):
            newline = message.find('\n')
            if newline != -1:
                from_line = message[:newline]
                message = message[newline + 1:]
            else:
                from_line = message
                message = ''
        elif isinstance(message, _mboxMMDFMessage):
            from_line = 'From ' + message.get_from()
        elif isinstance(message, email.message.Message):
            from_line = message.get_unixfrom()
        if from_line is None:
            from_line = 'From MAILER-DAEMON %s' % time.asctime(time.gmtime())
        start = self._file.tell()
        self._file.write(from_line + os.linesep)
        self._dump_message(message, self._file, self._mangle_from_)
        stop = self._file.tell()
        return (start, stop)


class mbox(_mboxMMDF):
    _mangle_from_ = True
    _append_newline = True

    def __init__(self, path, factory=None, create=True):
        self._message_factory = mboxMessage
        _mboxMMDF.__init__(self, path, factory, create)

    def _post_message_hook(self, f):
        f.write(os.linesep)

    def _generate_toc(self):
        starts, stops = [], []
        last_was_empty = False
        self._file.seek(0)
        while True:
            line_pos = self._file.tell()
            line = self._file.readline()
            if line.startswith('From '):
                if len(stops) < len(starts):
                    if last_was_empty:
                        stops.append(line_pos - len(os.linesep))
                    else:
                        stops.append(line_pos)
                starts.append(line_pos)
                last_was_empty = False
            if not line:
                if last_was_empty:
                    stops.append(line_pos - len(os.linesep))
                else:
                    stops.append(line_pos)
                break
            if line == os.linesep:
                last_was_empty = True
            last_was_empty = False

        self._toc = dict(enumerate(zip(starts, stops)))
        self._next_key = len(self._toc)
        self._file_length = self._file.tell()


class MMDF(_mboxMMDF):

    def __init__(self, path, factory=None, create=True):
        self._message_factory = MMDFMessage
        _mboxMMDF.__init__(self, path, factory, create)

    def _pre_message_hook(self, f):
        f.write('\x01\x01\x01\x01' + os.linesep)

    def _post_message_hook(self, f):
        f.write(os.linesep + '\x01\x01\x01\x01' + os.linesep)

    def _generate_toc(self):
        starts, stops = [], []
        self._file.seek(0)
        next_pos = 0
        while True:
            line_pos = next_pos
            line = self._file.readline()
            next_pos = self._file.tell()
            if line.startswith('\x01\x01\x01\x01' + os.linesep):
                starts.append(next_pos)
                while True:
                    line_pos = next_pos
                    line = self._file.readline()
                    next_pos = self._file.tell()
                    if line == '\x01\x01\x01\x01' + os.linesep:
                        stops.append(line_pos - len(os.linesep))
                        break
                    if line == '':
                        stops.append(line_pos)
                        break

            if line == '':
                break

        self._toc = dict(enumerate(zip(starts, stops)))
        self._next_key = len(self._toc)
        self._file.seek(0, 2)
        self._file_length = self._file.tell()


class MH(Mailbox):

    def __init__(self, path, factory=None, create=True):
        Mailbox.__init__(self, path, factory, create)
        if not os.path.exists(self._path):
            if create:
                os.mkdir(self._path, 448)
                os.close(os.open(os.path.join(self._path, '.mh_sequences'), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 384))
            else:
                raise NoSuchMailboxError(self._path)
        self._locked = False

    def add(self, message):
        keys = self.keys()
        if len(keys) == 0:
            new_key = 1
        else:
            new_key = max(keys) + 1
        new_path = os.path.join(self._path, str(new_key))
        f = _create_carefully(new_path)
        closed = False
        try:
            if self._locked:
                _lock_file(f)
            try:
                try:
                    self._dump_message(message, f)
                except BaseException:
                    if self._locked:
                        _unlock_file(f)
                    _sync_close(f)
                    closed = True
                    os.remove(new_path)
                    raise

                if isinstance(message, MHMessage):
                    self._dump_sequences(message, new_key)
            finally:
                if self._locked:
                    _unlock_file(f)

        finally:
            if not closed:
                _sync_close(f)

        return new_key

    def remove(self, key):
        path = os.path.join(self._path, str(key))
        try:
            f = open(path, 'rb+')
        except IOError as e:
            if e.errno == errno.ENOENT:
                raise KeyError('No message with key: %s' % key)
            else:
                raise
        else:
            f.close()
            os.remove(path)

    def __setitem__(self, key, message):
        path = os.path.join(self._path, str(key))
        try:
            f = open(path, 'rb+')
        except IOError as e:
            if e.errno == errno.ENOENT:
                raise KeyError('No message with key: %s' % key)
            else:
                raise

        try:
            if self._locked:
                _lock_file(f)
            try:
                os.close(os.open(path, os.O_WRONLY | os.O_TRUNC))
                self._dump_message(message, f)
                if isinstance(message, MHMessage):
                    self._dump_sequences(message, key)
            finally:
                if self._locked:
                    _unlock_file(f)

        finally:
            _sync_close(f)

    def get_message(self, key):
        try:
            if self._locked:
                f = open(os.path.join(self._path, str(key)), 'r+')
            else:
                f = open(os.path.join(self._path, str(key)), 'r')
        except IOError as e:
            if e.errno == errno.ENOENT:
                raise KeyError('No message with key: %s' % key)
            else:
                raise

        try:
            if self._locked:
                _lock_file(f)
            try:
                msg = MHMessage(f)
            finally:
                if self._locked:
                    _unlock_file(f)

        finally:
            f.close()

        for name, key_list in self.get_sequences().iteritems():
            if key in key_list:
                msg.add_sequence(name)

        return msg

    def get_string(self, key):
        try:
            if self._locked:
                f = open(os.path.join(self._path, str(key)), 'r+')
            else:
                f = open(os.path.join(self._path, str(key)), 'r')
        except IOError as e:
            if e.errno == errno.ENOENT:
                raise KeyError('No message with key: %s' % key)
            else:
                raise

        try:
            if self._locked:
                _lock_file(f)
            try:
                return f.read()
            finally:
                if self._locked:
                    _unlock_file(f)

        finally:
            f.close()

    def get_file(self, key):
        try:
            f = open(os.path.join(self._path, str(key)), 'rb')
        except IOError as e:
            if e.errno == errno.ENOENT:
                raise KeyError('No message with key: %s' % key)
            else:
                raise

        return _ProxyFile(f)

    def iterkeys(self):
        return iter(sorted((int(entry) for entry in os.listdir(self._path) if entry.isdigit())))

    def has_key(self, key):
        return os.path.exists(os.path.join(self._path, str(key)))

    def __len__(self):
        return len(list(self.iterkeys()))

    def lock(self):
        if not self._locked:
            self._file = open(os.path.join(self._path, '.mh_sequences'), 'rb+')
            _lock_file(self._file)
            self._locked = True

    def unlock(self):
        if self._locked:
            _unlock_file(self._file)
            _sync_close(self._file)
            del self._file
            self._locked = False

    def flush(self):
        pass

    def close(self):
        if self._locked:
            self.unlock()

    def list_folders(self):
        result = []
        for entry in os.listdir(self._path):
            if os.path.isdir(os.path.join(self._path, entry)):
                result.append(entry)

        return result

    def get_folder(self, folder):
        return MH(os.path.join(self._path, folder), factory=self._factory, create=False)

    def add_folder(self, folder):
        return MH(os.path.join(self._path, folder), factory=self._factory)

    def remove_folder(self, folder):
        path = os.path.join(self._path, folder)
        entries = os.listdir(path)
        if entries == ['.mh_sequences']:
            os.remove(os.path.join(path, '.mh_sequences'))
        elif entries == []:
            pass
        else:
            raise NotEmptyError('Folder not empty: %s' % self._path)
        os.rmdir(path)

    def get_sequences(self):
        results = {}
        f = open(os.path.join(self._path, '.mh_sequences'), 'r')
        try:
            all_keys = set(self.keys())
            for line in f:
                try:
                    name, contents = line.split(':')
                    keys = set()
                    for spec in contents.split():
                        if spec.isdigit():
                            keys.add(int(spec))
                        start, stop = (int(x) for x in spec.split('-'))
                        keys.update(range(start, stop + 1))

                    results[name] = [ key for key in sorted(keys) if key in all_keys ]
                    if len(results[name]) == 0:
                        del results[name]
                except ValueError:
                    raise FormatError('Invalid sequence specification: %s' % line.rstrip())

        finally:
            f.close()

        return results

    def set_sequences(self, sequences):
        f = open(os.path.join(self._path, '.mh_sequences'), 'r+')
        try:
            os.close(os.open(f.name, os.O_WRONLY | os.O_TRUNC))
            for name, keys in sequences.iteritems():
                if len(keys) == 0:
                    continue
                f.write('%s:' % name)
                prev = None
                completing = False
                for key in sorted(set(keys)):
                    if key - 1 == prev:
                        if not completing:
                            completing = True
                            f.write('-')
                    elif completing:
                        completing = False
                        f.write('%s %s' % (prev, key))
                    else:
                        f.write(' %s' % key)
                    prev = key

                if completing:
                    f.write(str(prev) + '\n')
                f.write('\n')

        finally:
            _sync_close(f)

        return

    def pack(self):
        sequences = self.get_sequences()
        prev = 0
        changes = []
        for key in self.iterkeys():
            if key - 1 != prev:
                changes.append((key, prev + 1))
                if hasattr(os, 'link'):
                    os.link(os.path.join(self._path, str(key)), os.path.join(self._path, str(prev + 1)))
                    os.unlink(os.path.join(self._path, str(key)))
                else:
                    os.rename(os.path.join(self._path, str(key)), os.path.join(self._path, str(prev + 1)))
            prev += 1

        self._next_key = prev + 1
        if len(changes) == 0:
            return
        for name, key_list in sequences.items():
            for old, new in changes:
                if old in key_list:
                    key_list[key_list.index(old)] = new

        self.set_sequences(sequences)

    def _dump_sequences(self, message, key):
        pending_sequences = message.get_sequences()
        all_sequences = self.get_sequences()
        for name, key_list in all_sequences.iteritems():
            if name in pending_sequences:
                key_list.append(key)
            if key in key_list:
                del key_list[key_list.index(key)]

        for sequence in pending_sequences:
            if sequence not in all_sequences:
                all_sequences[sequence] = [key]

        self.set_sequences(all_sequences)


class Babyl(_singlefileMailbox):
    _special_labels = frozenset(('unseen', 'deleted', 'filed', 'answered', 'forwarded', 'edited', 'resent'))

    def __init__(self, path, factory=None, create=True):
        _singlefileMailbox.__init__(self, path, factory, create)
        self._labels = {}

    def add(self, message):
        key = _singlefileMailbox.add(self, message)
        if isinstance(message, BabylMessage):
            self._labels[key] = message.get_labels()
        return key

    def remove(self, key):
        _singlefileMailbox.remove(self, key)
        if key in self._labels:
            del self._labels[key]

    def __setitem__(self, key, message):
        _singlefileMailbox.__setitem__(self, key, message)
        if isinstance(message, BabylMessage):
            self._labels[key] = message.get_labels()

    def get_message(self, key):
        start, stop = self._lookup(key)
        self._file.seek(start)
        self._file.readline()
        original_headers = StringIO.StringIO()
        while True:
            line = self._file.readline()
            if line == '*** EOOH ***' + os.linesep or line == '':
                break
            original_headers.write(line.replace(os.linesep, '\n'))

        visible_headers = StringIO.StringIO()
        while True:
            line = self._file.readline()
            if line == os.linesep or line == '':
                break
            visible_headers.write(line.replace(os.linesep, '\n'))

        body = self._file.read(stop - self._file.tell()).replace(os.linesep, '\n')
        msg = BabylMessage(original_headers.getvalue() + body)
        msg.set_visible(visible_headers.getvalue())
        if key in self._labels:
            msg.set_labels(self._labels[key])
        return msg

    def get_string(self, key):
        start, stop = self._lookup(key)
        self._file.seek(start)
        self._file.readline()
        original_headers = StringIO.StringIO()
        while True:
            line = self._file.readline()
            if line == '*** EOOH ***' + os.linesep or line == '':
                break
            original_headers.write(line.replace(os.linesep, '\n'))

        while True:
            line = self._file.readline()
            if line == os.linesep or line == '':
                break

        return original_headers.getvalue() + self._file.read(stop - self._file.tell()).replace(os.linesep, '\n')

    def get_file(self, key):
        return StringIO.StringIO(self.get_string(key).replace('\n', os.linesep))

    def get_labels(self):
        self._lookup()
        labels = set()
        for label_list in self._labels.values():
            labels.update(label_list)

        labels.difference_update(self._special_labels)
        return list(labels)

    def _generate_toc(self):
        starts, stops = [], []
        self._file.seek(0)
        next_pos = 0
        label_lists = []
        while True:
            line_pos = next_pos
            line = self._file.readline()
            next_pos = self._file.tell()
            if line == '\x1f\x0c' + os.linesep:
                if len(stops) < len(starts):
                    stops.append(line_pos - len(os.linesep))
                starts.append(next_pos)
                labels = [ label.strip() for label in self._file.readline()[1:].split(',') if label.strip() != '' ]
                label_lists.append(labels)
            if line == '\x1f' or line == '\x1f' + os.linesep:
                if len(stops) < len(starts):
                    stops.append(line_pos - len(os.linesep))
            if line == '':
                stops.append(line_pos - len(os.linesep))
                break

        self._toc = dict(enumerate(zip(starts, stops)))
        self._labels = dict(enumerate(label_lists))
        self._next_key = len(self._toc)
        self._file.seek(0, 2)
        self._file_length = self._file.tell()

    def _pre_mailbox_hook(self, f):
        f.write('BABYL OPTIONS:%sVersion: 5%sLabels:%s%s\x1f' % (os.linesep,
         os.linesep,
         ','.join(self.get_labels()),
         os.linesep))

    def _pre_message_hook(self, f):
        f.write('\x0c' + os.linesep)

    def _post_message_hook(self, f):
        f.write(os.linesep + '\x1f')

    def _install_message(self, message):
        start = self._file.tell()
        if isinstance(message, BabylMessage):
            special_labels = []
            labels = []
            for label in message.get_labels():
                if label in self._special_labels:
                    special_labels.append(label)
                labels.append(label)

            self._file.write('1')
            for label in special_labels:
                self._file.write(', ' + label)

            self._file.write(',,')
            for label in labels:
                self._file.write(' ' + label + ',')

            self._file.write(os.linesep)
        else:
            self._file.write('1,,' + os.linesep)
        if isinstance(message, email.message.Message):
            orig_buffer = StringIO.StringIO()
            orig_generator = email.generator.Generator(orig_buffer, False, 0)
            orig_generator.flatten(message)
            orig_buffer.seek(0)
            while True:
                line = orig_buffer.readline()
                self._file.write(line.replace('\n', os.linesep))
                if line == '\n' or line == '':
                    break

            self._file.write('*** EOOH ***' + os.linesep)
            if isinstance(message, BabylMessage):
                vis_buffer = StringIO.StringIO()
                vis_generator = email.generator.Generator(vis_buffer, False, 0)
                vis_generator.flatten(message.get_visible())
                while True:
                    line = vis_buffer.readline()
                    self._file.write(line.replace('\n', os.linesep))
                    if line == '\n' or line == '':
                        break

            else:
                orig_buffer.seek(0)
                while True:
                    line = orig_buffer.readline()
                    self._file.write(line.replace('\n', os.linesep))
                    if line == '\n' or line == '':
                        break

            while True:
                buffer = orig_buffer.read(4096)
                if buffer == '':
                    break
                self._file.write(buffer.replace('\n', os.linesep))

        elif isinstance(message, str):
            body_start = message.find('\n\n') + 2
            if body_start - 2 != -1:
                self._file.write(message[:body_start].replace('\n', os.linesep))
                self._file.write('*** EOOH ***' + os.linesep)
                self._file.write(message[:body_start].replace('\n', os.linesep))
                self._file.write(message[body_start:].replace('\n', os.linesep))
            else:
                self._file.write('*** EOOH ***' + os.linesep + os.linesep)
                self._file.write(message.replace('\n', os.linesep))
        elif hasattr(message, 'readline'):
            original_pos = message.tell()
            first_pass = True
            while True:
                line = message.readline()
                self._file.write(line.replace('\n', os.linesep))
                if line == '\n' or line == '':
                    if first_pass:
                        first_pass = False
                        self._file.write('*** EOOH ***' + os.linesep)
                        message.seek(original_pos)
                    else:
                        break

            while True:
                buffer = message.read(4096)
                if buffer == '':
                    break
                self._file.write(buffer.replace('\n', os.linesep))

        else:
            raise TypeError('Invalid message type: %s' % type(message))
        stop = self._file.tell()
        return (start, stop)


class Message(email.message.Message):

    def __init__(self, message=None):
        if isinstance(message, email.message.Message):
            self._become_message(copy.deepcopy(message))
            if isinstance(message, Message):
                message._explain_to(self)
        elif isinstance(message, str):
            self._become_message(email.message_from_string(message))
        elif hasattr(message, 'read'):
            self._become_message(email.message_from_file(message))
        elif message is None:
            email.message.Message.__init__(self)
        else:
            raise TypeError('Invalid message type: %s' % type(message))
        return

    def _become_message(self, message):
        for name in ('_headers', '_unixfrom', '_payload', '_charset', 'preamble', 'epilogue', 'defects', '_default_type'):
            self.__dict__[name] = message.__dict__[name]

    def _explain_to(self, message):
        if isinstance(message, Message):
            return
        raise TypeError('Cannot convert to specified type')


class MaildirMessage(Message):

    def __init__(self, message=None):
        self._subdir = 'new'
        self._info = ''
        self._date = time.time()
        Message.__init__(self, message)

    def get_subdir(self):
        return self._subdir

    def set_subdir(self, subdir):
        if subdir == 'new' or subdir == 'cur':
            self._subdir = subdir
        else:
            raise ValueError("subdir must be 'new' or 'cur': %s" % subdir)

    def get_flags(self):
        if self._info.startswith('2,'):
            return self._info[2:]
        else:
            return ''

    def set_flags(self, flags):
        self._info = '2,' + ''.join(sorted(flags))

    def add_flag(self, flag):
        self.set_flags(''.join(set(self.get_flags()) | set(flag)))

    def remove_flag(self, flag):
        if self.get_flags() != '':
            self.set_flags(''.join(set(self.get_flags()) - set(flag)))

    def get_date(self):
        return self._date

    def set_date(self, date):
        try:
            self._date = float(date)
        except ValueError:
            raise TypeError("can't convert to float: %s" % date)

    def get_info(self):
        return self._info

    def set_info(self, info):
        if isinstance(info, str):
            self._info = info
        else:
            raise TypeError('info must be a string: %s' % type(info))

    def _explain_to(self, message):
        if isinstance(message, MaildirMessage):
            message.set_flags(self.get_flags())
            message.set_subdir(self.get_subdir())
            message.set_date(self.get_date())
        elif isinstance(message, _mboxMMDFMessage):
            flags = set(self.get_flags())
            if 'S' in flags:
                message.add_flag('R')
            if self.get_subdir() == 'cur':
                message.add_flag('O')
            if 'T' in flags:
                message.add_flag('D')
            if 'F' in flags:
                message.add_flag('F')
            if 'R' in flags:
                message.add_flag('A')
            message.set_from('MAILER-DAEMON', time.gmtime(self.get_date()))
        elif isinstance(message, MHMessage):
            flags = set(self.get_flags())
            if 'S' not in flags:
                message.add_sequence('unseen')
            if 'R' in flags:
                message.add_sequence('replied')
            if 'F' in flags:
                message.add_sequence('flagged')
        elif isinstance(message, BabylMessage):
            flags = set(self.get_flags())
            if 'S' not in flags:
                message.add_label('unseen')
            if 'T' in flags:
                message.add_label('deleted')
            if 'R' in flags:
                message.add_label('answered')
            if 'P' in flags:
                message.add_label('forwarded')
        elif isinstance(message, Message):
            pass
        else:
            raise TypeError('Cannot convert to specified type: %s' % type(message))


class _mboxMMDFMessage(Message):

    def __init__(self, message=None):
        self.set_from('MAILER-DAEMON', True)
        if isinstance(message, email.message.Message):
            unixfrom = message.get_unixfrom()
            if unixfrom is not None and unixfrom.startswith('From '):
                self.set_from(unixfrom[5:])
        Message.__init__(self, message)
        return

    def get_from(self):
        return self._from

    def set_from(self, from_, time_=None):
        if time_ is not None:
            if time_ is True:
                time_ = time.gmtime()
            from_ += ' ' + time.asctime(time_)
        self._from = from_
        return

    def get_flags(self):
        return self.get('Status', '') + self.get('X-Status', '')

    def set_flags(self, flags):
        flags = set(flags)
        status_flags, xstatus_flags = ('', '')
        for flag in ('R', 'O'):
            if flag in flags:
                status_flags += flag
                flags.remove(flag)

        for flag in ('D', 'F', 'A'):
            if flag in flags:
                xstatus_flags += flag
                flags.remove(flag)

        xstatus_flags += ''.join(sorted(flags))
        try:
            self.replace_header('Status', status_flags)
        except KeyError:
            self.add_header('Status', status_flags)

        try:
            self.replace_header('X-Status', xstatus_flags)
        except KeyError:
            self.add_header('X-Status', xstatus_flags)

    def add_flag(self, flag):
        self.set_flags(''.join(set(self.get_flags()) | set(flag)))

    def remove_flag(self, flag):
        if 'Status' in self or 'X-Status' in self:
            self.set_flags(''.join(set(self.get_flags()) - set(flag)))

    def _explain_to(self, message):
        if isinstance(message, MaildirMessage):
            flags = set(self.get_flags())
            if 'O' in flags:
                message.set_subdir('cur')
            if 'F' in flags:
                message.add_flag('F')
            if 'A' in flags:
                message.add_flag('R')
            if 'R' in flags:
                message.add_flag('S')
            if 'D' in flags:
                message.add_flag('T')
            del message['status']
            del message['x-status']
            maybe_date = ' '.join(self.get_from().split()[-5:])
            try:
                message.set_date(calendar.timegm(time.strptime(maybe_date, '%a %b %d %H:%M:%S %Y')))
            except (ValueError, OverflowError):
                pass

        elif isinstance(message, _mboxMMDFMessage):
            message.set_flags(self.get_flags())
            message.set_from(self.get_from())
        elif isinstance(message, MHMessage):
            flags = set(self.get_flags())
            if 'R' not in flags:
                message.add_sequence('unseen')
            if 'A' in flags:
                message.add_sequence('replied')
            if 'F' in flags:
                message.add_sequence('flagged')
            del message['status']
            del message['x-status']
        elif isinstance(message, BabylMessage):
            flags = set(self.get_flags())
            if 'R' not in flags:
                message.add_label('unseen')
            if 'D' in flags:
                message.add_label('deleted')
            if 'A' in flags:
                message.add_label('answered')
            del message['status']
            del message['x-status']
        elif isinstance(message, Message):
            pass
        else:
            raise TypeError('Cannot convert to specified type: %s' % type(message))


class mboxMessage(_mboxMMDFMessage):
    pass


class MHMessage(Message):

    def __init__(self, message=None):
        self._sequences = []
        Message.__init__(self, message)

    def get_sequences(self):
        return self._sequences[:]

    def set_sequences(self, sequences):
        self._sequences = list(sequences)

    def add_sequence(self, sequence):
        if isinstance(sequence, str):
            if sequence not in self._sequences:
                self._sequences.append(sequence)
        else:
            raise TypeError('sequence must be a string: %s' % type(sequence))

    def remove_sequence(self, sequence):
        try:
            self._sequences.remove(sequence)
        except ValueError:
            pass

    def _explain_to(self, message):
        if isinstance(message, MaildirMessage):
            sequences = set(self.get_sequences())
            if 'unseen' in sequences:
                message.set_subdir('cur')
            else:
                message.set_subdir('cur')
                message.add_flag('S')
            if 'flagged' in sequences:
                message.add_flag('F')
            if 'replied' in sequences:
                message.add_flag('R')
        elif isinstance(message, _mboxMMDFMessage):
            sequences = set(self.get_sequences())
            if 'unseen' not in sequences:
                message.add_flag('RO')
            else:
                message.add_flag('O')
            if 'flagged' in sequences:
                message.add_flag('F')
            if 'replied' in sequences:
                message.add_flag('A')
        elif isinstance(message, MHMessage):
            for sequence in self.get_sequences():
                message.add_sequence(sequence)

        elif isinstance(message, BabylMessage):
            sequences = set(self.get_sequences())
            if 'unseen' in sequences:
                message.add_label('unseen')
            if 'replied' in sequences:
                message.add_label('answered')
        elif isinstance(message, Message):
            pass
        else:
            raise TypeError('Cannot convert to specified type: %s' % type(message))


class BabylMessage(Message):

    def __init__(self, message=None):
        self._labels = []
        self._visible = Message()
        Message.__init__(self, message)

    def get_labels(self):
        return self._labels[:]

    def set_labels(self, labels):
        self._labels = list(labels)

    def add_label(self, label):
        if isinstance(label, str):
            if label not in self._labels:
                self._labels.append(label)
        else:
            raise TypeError('label must be a string: %s' % type(label))

    def remove_label(self, label):
        try:
            self._labels.remove(label)
        except ValueError:
            pass

    def get_visible(self):
        return Message(self._visible)

    def set_visible(self, visible):
        self._visible = Message(visible)

    def update_visible(self):
        for header in self._visible.keys():
            if header in self:
                self._visible.replace_header(header, self[header])
            del self._visible[header]

        for header in ('Date', 'From', 'Reply-To', 'To', 'CC', 'Subject'):
            if header in self and header not in self._visible:
                self._visible[header] = self[header]

    def _explain_to(self, message):
        if isinstance(message, MaildirMessage):
            labels = set(self.get_labels())
            if 'unseen' in labels:
                message.set_subdir('cur')
            else:
                message.set_subdir('cur')
                message.add_flag('S')
            if 'forwarded' in labels or 'resent' in labels:
                message.add_flag('P')
            if 'answered' in labels:
                message.add_flag('R')
            if 'deleted' in labels:
                message.add_flag('T')
        elif isinstance(message, _mboxMMDFMessage):
            labels = set(self.get_labels())
            if 'unseen' not in labels:
                message.add_flag('RO')
            else:
                message.add_flag('O')
            if 'deleted' in labels:
                message.add_flag('D')
            if 'answered' in labels:
                message.add_flag('A')
        elif isinstance(message, MHMessage):
            labels = set(self.get_labels())
            if 'unseen' in labels:
                message.add_sequence('unseen')
            if 'answered' in labels:
                message.add_sequence('replied')
        elif isinstance(message, BabylMessage):
            message.set_visible(self.get_visible())
            for label in self.get_labels():
                message.add_label(label)

        elif isinstance(message, Message):
            pass
        else:
            raise TypeError('Cannot convert to specified type: %s' % type(message))


class MMDFMessage(_mboxMMDFMessage):
    pass


class _ProxyFile():

    def __init__(self, f, pos=None):
        self._file = f
        if pos is None:
            self._pos = f.tell()
        else:
            self._pos = pos
        return

    def read(self, size=None):
        return self._read(size, self._file.read)

    def readline(self, size=None):
        return self._read(size, self._file.readline)

    def readlines(self, sizehint=None):
        result = []
        for line in self:
            result.append(line)
            if sizehint is not None:
                sizehint -= len(line)
                if sizehint <= 0:
                    break

        return result

    def __iter__(self):
        return iter(self.readline, '')

    def tell(self):
        return self._pos

    def seek(self, offset, whence=0):
        if whence == 1:
            self._file.seek(self._pos)
        self._file.seek(offset, whence)
        self._pos = self._file.tell()

    def close(self):
        if hasattr(self, '_file'):
            if hasattr(self._file, 'close'):
                self._file.close()
            del self._file

    def _read(self, size, read_method):
        if size is None:
            size = -1
        self._file.seek(self._pos)
        result = read_method(size)
        self._pos = self._file.tell()
        return result


class _PartialFile(_ProxyFile):

    def __init__(self, f, start=None, stop=None):
        _ProxyFile.__init__(self, f, start)
        self._start = start
        self._stop = stop

    def tell(self):
        return _ProxyFile.tell(self) - self._start

    def seek(self, offset, whence=0):
        if whence == 0:
            self._pos = self._start
            whence = 1
        elif whence == 2:
            self._pos = self._stop
            whence = 1
        _ProxyFile.seek(self, offset, whence)

    def _read(self, size, read_method):
        remaining = self._stop - self._pos
        if remaining <= 0:
            return ''
        else:
            if size is None or size < 0 or size > remaining:
                size = remaining
            return _ProxyFile._read(self, size, read_method)

    def close(self):
        if hasattr(self, '_file'):
            del self._file


def _lock_file(f, dotlock=True):
    dotlock_done = False
    try:
        if fcntl:
            try:
                fcntl.lockf(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except IOError as e:
                if e.errno in (errno.EAGAIN, errno.EACCES, errno.EROFS):
                    raise ExternalClashError('lockf: lock unavailable: %s' % f.name)
                else:
                    raise

        if dotlock:
            try:
                pre_lock = _create_temporary(f.name + '.lock')
                pre_lock.close()
            except IOError as e:
                if e.errno in (errno.EACCES, errno.EROFS):
                    return
                raise

            try:
                if hasattr(os, 'link'):
                    os.link(pre_lock.name, f.name + '.lock')
                    dotlock_done = True
                    os.unlink(pre_lock.name)
                else:
                    os.rename(pre_lock.name, f.name + '.lock')
                    dotlock_done = True
            except OSError as e:
                if e.errno == errno.EEXIST or os.name == 'os2' and e.errno == errno.EACCES:
                    os.remove(pre_lock.name)
                    raise ExternalClashError('dot lock unavailable: %s' % f.name)
                else:
                    raise

    except:
        if fcntl:
            fcntl.lockf(f, fcntl.LOCK_UN)
        if dotlock_done:
            os.remove(f.name + '.lock')
        raise


def _unlock_file(f):
    if fcntl:
        fcntl.lockf(f, fcntl.LOCK_UN)
    if os.path.exists(f.name + '.lock'):
        os.remove(f.name + '.lock')


def _create_carefully(path):
    fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_RDWR, 438)
    try:
        return open(path, 'rb+')
    finally:
        os.close(fd)


def _create_temporary(path):
    return _create_carefully('%s.%s.%s.%s' % (path,
     int(time.time()),
     socket.gethostname(),
     os.getpid()))


def _sync_flush(f):
    f.flush()
    if hasattr(os, 'fsync'):
        os.fsync(f.fileno())


def _sync_close(f):
    _sync_flush(f)
    f.close()


class _Mailbox():

    def __init__(self, fp, factory=rfc822.Message):
        self.fp = fp
        self.seekp = 0
        self.factory = factory

    def __iter__(self):
        return iter(self.next, None)

    def next(self):
        while 1:
            self.fp.seek(self.seekp)
            try:
                self._search_start()
            except EOFError:
                self.seekp = self.fp.tell()
                return None

            start = self.fp.tell()
            self._search_end()
            self.seekp = stop = self.fp.tell()
            if start != stop:
                break

        return self.factory(_PartialFile(self.fp, start, stop))


class UnixMailbox(_Mailbox):

    def _search_start(self):
        while 1:
            pos = self.fp.tell()
            line = self.fp.readline()
            if not line:
                raise EOFError
            if line[:5] == 'From ' and self._isrealfromline(line):
                self.fp.seek(pos)
                return

    def _search_end(self):
        self.fp.readline()
        while 1:
            pos = self.fp.tell()
            line = self.fp.readline()
            if not line:
                return
            if line[:5] == 'From ' and self._isrealfromline(line):
                self.fp.seek(pos)
                return

    _fromlinepattern = 'From \\s*[^\\s]+\\s+\\w\\w\\w\\s+\\w\\w\\w\\s+\\d?\\d\\s+\\d?\\d:\\d\\d(:\\d\\d)?(\\s+[^\\s]+)?\\s+\\d\\d\\d\\d\\s*[^\\s]*\\s*$'
    _regexp = None

    def _strict_isrealfromline(self, line):
        if not self._regexp:
            import re
            self._regexp = re.compile(self._fromlinepattern)
        return self._regexp.match(line)

    def _portable_isrealfromline(self, line):
        return True

    _isrealfromline = _strict_isrealfromline


class PortableUnixMailbox(UnixMailbox):
    _isrealfromline = UnixMailbox._portable_isrealfromline


class MmdfMailbox(_Mailbox):

    def _search_start(self):
        while 1:
            line = self.fp.readline()
            if not line:
                raise EOFError
            if line[:5] == '\x01\x01\x01\x01\n':
                return

    def _search_end(self):
        while 1:
            pos = self.fp.tell()
            line = self.fp.readline()
            if not line:
                return
            if line == '\x01\x01\x01\x01\n':
                self.fp.seek(pos)
                return


class MHMailbox():

    def __init__(self, dirname, factory=rfc822.Message):
        import re
        pat = re.compile('^[1-9][0-9]*$')
        self.dirname = dirname
        list = os.listdir(self.dirname)
        list = filter(pat.match, list)
        list = map(long, list)
        list.sort()
        self.boxes = map(str, list)
        self.boxes.reverse()
        self.factory = factory

    def __iter__(self):
        return iter(self.next, None)

    def next(self):
        if not self.boxes:
            return None
        else:
            fn = self.boxes.pop()
            fp = open(os.path.join(self.dirname, fn))
            msg = self.factory(fp)
            try:
                msg._mh_msgno = fn
            except (AttributeError, TypeError):
                pass

            return msg


class BabylMailbox(_Mailbox):

    def _search_start(self):
        while 1:
            line = self.fp.readline()
            if not line:
                raise EOFError
            if line == '*** EOOH ***\n':
                return

    def _search_end(self):
        while 1:
            pos = self.fp.tell()
            line = self.fp.readline()
            if not line:
                return
            if line == '\x1f\x0c\n' or line == '\x1f':
                self.fp.seek(pos)
                return


class Error(Exception):
    pass


class NoSuchMailboxError(Error):
    pass


class NotEmptyError(Error):
    pass


class ExternalClashError(Error):
    pass


class FormatError(Error):
    pass
