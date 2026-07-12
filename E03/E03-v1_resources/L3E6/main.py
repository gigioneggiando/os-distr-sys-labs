#!/usr/bin/env python
from __future__ import print_function, absolute_import, division

import logging
import mysql.connector

from errno import ENOENT
from stat import S_IFDIR, S_IFREG
from time import time

from fuse import FUSE, FuseOSError, Operations, LoggingMixIn, fuse_get_context


# Global connection handle, set up in __main__ before FUSE mounts the filesystem
db = None


class Context(LoggingMixIn, Operations):
    'Example filesystem to demonstrate fuse_get_context()'

    def getattr(self, path, fh=None):
        if path == "/":
            st = dict(st_mode=(S_IFDIR | 0o755), st_nlink=2)
        else:
            filename = path[1:]  # Remove leading /

            cursor = db.cursor()
            cursor.execute(
                "SELECT filesize FROM Files WHERE filename = %s", (filename,)
            )
            row = cursor.fetchone()
            cursor.close()

            if row is None:
                raise FuseOSError(ENOENT)

            filesize = row[0]
            st = dict(st_mode=(S_IFREG | 0o755), st_size=filesize)

        st['st_ctime'] = st['st_mtime'] = st['st_atime'] = time()
        return st

    def read(self, path, size, offset, fh):

        def encoded(x):
            return ('%s\n' % x).encode('utf-8')

        filename = path[1:]

        cursor = db.cursor()
        cursor.execute(
            "SELECT filecontent FROM Files WHERE filename = %s", (filename,)
        )
        row = cursor.fetchone()
        cursor.close()

        if row is None:
            raise FuseOSError(ENOENT)

        content = encoded(row[0])
        return content[offset:offset + size]

    def readdir(self, path, fh):
        Files = []

        cursor = db.cursor()
        cursor.execute("SELECT filename FROM Files")
        for (filename,) in cursor.fetchall():
            Files.append(filename)
        cursor.close()

        return ['.', '..'] + Files

    # Disable unused operations:
    access = None
    flush = None
    getxattr = None
    listxattr = None
    open = None
    opendir = None
    release = None
    releasedir = None
    statfs = None


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('mount')
    parser.add_argument('--host', default='localhost')
    parser.add_argument('--user', default='root')
    parser.add_argument('--password', default='')
    parser.add_argument('--database', default='fusedb')
    args = parser.parse_args()

    # Establish mysql connection
    db = mysql.connector.connect(
        host=args.host,
        user=args.user,
        password=args.password,
        database=args.database,
    )

    logging.basicConfig(level=logging.WARNING)
    fuse = FUSE(
        Context(), args.mount, foreground=True, ro=True, allow_other=True)
