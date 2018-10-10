# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/distutils/dir_util.py
__revision__ = '$Id$'
import os
import errno
from distutils.errors import DistutilsFileError, DistutilsInternalError
from distutils import log
_path_created = {}

def mkpath(name, mode=511, verbose=1, dry_run=0):
    global _path_created
    if not isinstance(name, basestring):
        raise DistutilsInternalError, "mkpath: 'name' must be a string (got %r)" % (name,)
    name = os.path.normpath(name)
    created_dirs = []
    if os.path.isdir(name) or name == '':
        return created_dirs
    if _path_created.get(os.path.abspath(name)):
        return created_dirs
    head, tail = os.path.split(name)
    tails = [tail]
    while head and tail and not os.path.isdir(head):
        head, tail = os.path.split(head)
        tails.insert(0, tail)

    for d in tails:
        head = os.path.join(head, d)
        abs_head = os.path.abspath(head)
        if _path_created.get(abs_head):
            continue
        if verbose >= 1:
            log.info('creating %s', head)
        if not dry_run:
            try:
                os.mkdir(head, mode)
            except OSError as exc:
                if not (exc.errno == errno.EEXIST and os.path.isdir(head)):
                    raise DistutilsFileError("could not create '%s': %s" % (head, exc.args[-1]))

            created_dirs.append(head)
        _path_created[abs_head] = 1

    return created_dirs


def create_tree(base_dir, files, mode=511, verbose=1, dry_run=0):
    need_dir = {}
    for file in files:
        need_dir[os.path.join(base_dir, os.path.dirname(file))] = 1

    need_dirs = need_dir.keys()
    need_dirs.sort()
    for dir in need_dirs:
        mkpath(dir, mode, verbose=verbose, dry_run=dry_run)


def copy_tree(src, dst, preserve_mode=1, preserve_times=1, preserve_symlinks=0, update=0, verbose=1, dry_run=0):
    from distutils.file_util import copy_file
    if not dry_run and not os.path.isdir(src):
        raise DistutilsFileError, "cannot copy tree '%s': not a directory" % src
    try:
        names = os.listdir(src)
    except os.error as (errno, errstr):
        if dry_run:
            names = []
        else:
            raise DistutilsFileError, "error listing files in '%s': %s" % (src, errstr)

    if not dry_run:
        mkpath(dst, verbose=verbose)
    outputs = []
    for n in names:
        src_name = os.path.join(src, n)
        dst_name = os.path.join(dst, n)
        if n.startswith('.nfs'):
            continue
        if preserve_symlinks and os.path.islink(src_name):
            link_dest = os.readlink(src_name)
            if verbose >= 1:
                log.info('linking %s -> %s', dst_name, link_dest)
            if not dry_run:
                os.symlink(link_dest, dst_name)
            outputs.append(dst_name)
        if os.path.isdir(src_name):
            outputs.extend(copy_tree(src_name, dst_name, preserve_mode, preserve_times, preserve_symlinks, update, verbose=verbose, dry_run=dry_run))
        copy_file(src_name, dst_name, preserve_mode, preserve_times, update, verbose=verbose, dry_run=dry_run)
        outputs.append(dst_name)

    return outputs


def _build_cmdtuple(path, cmdtuples):
    for f in os.listdir(path):
        real_f = os.path.join(path, f)
        if os.path.isdir(real_f) and not os.path.islink(real_f):
            _build_cmdtuple(real_f, cmdtuples)
        cmdtuples.append((os.remove, real_f))

    cmdtuples.append((os.rmdir, path))


def remove_tree(directory, verbose=1, dry_run=0):
    if verbose >= 1:
        log.info("removing '%s' (and everything under it)", directory)
    if dry_run:
        return
    cmdtuples = []
    _build_cmdtuple(directory, cmdtuples)
    for cmd in cmdtuples:
        try:
            cmd[0](cmd[1])
            abspath = os.path.abspath(cmd[1])
            if abspath in _path_created:
                del _path_created[abspath]
        except (IOError, OSError) as exc:
            log.warn('error removing %s: %s', directory, exc)


def ensure_relative(path):
    drive, path = os.path.splitdrive(path)
    if path[0:1] == os.sep:
        path = drive + path[1:]
    return path
