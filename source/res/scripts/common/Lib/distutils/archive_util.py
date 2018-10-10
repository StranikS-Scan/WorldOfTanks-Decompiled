# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/distutils/archive_util.py
__revision__ = '$Id$'
import os
from warnings import warn
import sys
from distutils.errors import DistutilsExecError
from distutils.spawn import spawn
from distutils.dir_util import mkpath
from distutils import log
try:
    from pwd import getpwnam
except ImportError:
    getpwnam = None

try:
    from grp import getgrnam
except ImportError:
    getgrnam = None

def _get_gid(name):
    if getgrnam is None or name is None:
        return
    else:
        try:
            result = getgrnam(name)
        except KeyError:
            result = None

        return result[2] if result is not None else None


def _get_uid(name):
    if getpwnam is None or name is None:
        return
    else:
        try:
            result = getpwnam(name)
        except KeyError:
            result = None

        return result[2] if result is not None else None


def make_tarball(base_name, base_dir, compress='gzip', verbose=0, dry_run=0, owner=None, group=None):
    tar_compression = {'gzip': 'gz',
     'bzip2': 'bz2',
     None: '',
     'compress': ''}
    compress_ext = {'gzip': '.gz',
     'bzip2': '.bz2',
     'compress': '.Z'}
    if compress is not None and compress not in compress_ext.keys():
        raise ValueError, "bad value for 'compress': must be None, 'gzip', 'bzip2' or 'compress'"
    archive_name = base_name + '.tar'
    if compress != 'compress':
        archive_name += compress_ext.get(compress, '')
    mkpath(os.path.dirname(archive_name), dry_run=dry_run)
    import tarfile
    log.info('Creating tar archive')
    uid = _get_uid(owner)
    gid = _get_gid(group)

    def _set_uid_gid(tarinfo):
        if gid is not None:
            tarinfo.gid = gid
            tarinfo.gname = group
        if uid is not None:
            tarinfo.uid = uid
            tarinfo.uname = owner
        return tarinfo

    if not dry_run:
        tar = tarfile.open(archive_name, 'w|%s' % tar_compression[compress])
        try:
            tar.add(base_dir, filter=_set_uid_gid)
        finally:
            tar.close()

    if compress == 'compress':
        warn("'compress' will be deprecated.", PendingDeprecationWarning)
        compressed_name = archive_name + compress_ext[compress]
        if sys.platform == 'win32':
            cmd = [compress, archive_name, compressed_name]
        else:
            cmd = [compress, '-f', archive_name]
        spawn(cmd, dry_run=dry_run)
        return compressed_name
    else:
        return archive_name


def make_zipfile(base_name, base_dir, verbose=0, dry_run=0):
    try:
        import zipfile
    except ImportError:
        zipfile = None

    zip_filename = base_name + '.zip'
    mkpath(os.path.dirname(zip_filename), dry_run=dry_run)
    if zipfile is None:
        if verbose:
            zipoptions = '-r'
        else:
            zipoptions = '-rq'
        try:
            spawn(['zip',
             zipoptions,
             zip_filename,
             base_dir], dry_run=dry_run)
        except DistutilsExecError:
            raise DistutilsExecError, "unable to create zip file '%s': could neither import the 'zipfile' module nor find a standalone zip utility" % zip_filename

    else:
        log.info("creating '%s' and adding '%s' to it", zip_filename, base_dir)
        if not dry_run:
            zip = zipfile.ZipFile(zip_filename, 'w', compression=zipfile.ZIP_DEFLATED)
            for dirpath, dirnames, filenames in os.walk(base_dir):
                for name in filenames:
                    path = os.path.normpath(os.path.join(dirpath, name))
                    if os.path.isfile(path):
                        zip.write(path, path)
                        log.info("adding '%s'" % path)

            zip.close()
    return zip_filename


ARCHIVE_FORMATS = {'gztar': (make_tarball, [('compress', 'gzip')], "gzip'ed tar-file"),
 'bztar': (make_tarball, [('compress', 'bzip2')], "bzip2'ed tar-file"),
 'ztar': (make_tarball, [('compress', 'compress')], 'compressed tar file'),
 'tar': (make_tarball, [('compress', None)], 'uncompressed tar file'),
 'zip': (make_zipfile, [], 'ZIP file')}

def check_archive_formats(formats):
    for format in formats:
        if format not in ARCHIVE_FORMATS:
            return format

    return None


def make_archive(base_name, format, root_dir=None, base_dir=None, verbose=0, dry_run=0, owner=None, group=None):
    save_cwd = os.getcwd()
    if root_dir is not None:
        log.debug("changing into '%s'", root_dir)
        base_name = os.path.abspath(base_name)
        if not dry_run:
            os.chdir(root_dir)
    if base_dir is None:
        base_dir = os.curdir
    kwargs = {'dry_run': dry_run}
    try:
        format_info = ARCHIVE_FORMATS[format]
    except KeyError:
        raise ValueError, "unknown archive format '%s'" % format

    func = format_info[0]
    for arg, val in format_info[1]:
        kwargs[arg] = val

    if format != 'zip':
        kwargs['owner'] = owner
        kwargs['group'] = group
    try:
        filename = func(base_name, base_dir, **kwargs)
    finally:
        if root_dir is not None:
            log.debug("changing back to '%s'", save_cwd)
            os.chdir(save_cwd)

    return filename
