from __future__ import with_statement
from cStringIO import StringIO
import unittest
import zipfile

import mock

import appengine


def make_zip(members):
    """Creates a new ZipFile and returns a file-like object open for reading.

    For each tuple (name, bytes) in members, an archive member with the name
    and bytes is added to the zipfile.
    """
    filename = StringIO()
    archive = zipfile.ZipFile(filename, 'w')

    for name, bytes in members:
        archive.writestr(name, bytes)

    archive.close()
    filename.seek(0)

    return filename


class ExtractZipTestCase(unittest.TestCase):
    def test_extract_zip(self):

        filename = make_zip([
            ('/foo', 'contents of foo'),
        ])
        zip = zipfile.ZipFile(filename)

        with mock.patch('appengine._extract_zip_member') as mock_extract:
            appengine._extract_zip(zip)

        self.assertEqual(mock_extract.call_count, 1)
        self.assertEqual(mock_extract.call_args_list[0][0][0], zip)
        self.assertEqual(mock_extract.call_args_list[0][0][1].filename, '/foo')


class ArgvParsingTestCase(unittest.TestCase):

    def test_opts(self):
        # Argument option parsing.

        argv = '--prefix /foo/local --bindir /foo/local/bin --force --no-bindir'
        parser = appengine.make_parser()
        args = parser.parse_args(argv.split())

        self.assertEqual(args.force, True)
        self.assertEqual(args.prefix, '/foo/local')
        self.assertEqual(args.bindir, '/foo/local/bin')
        self.assertEqual(args.no_bindir, True)

    def test_default_opts(self):
        # Default values for missing options.

        parser = appengine.make_parser()
        args = parser.parse_args(''.split())

        self.assertEqual(args.force, False)
        self.assertEqual(args.prefix, None)
        self.assertEqual(args.bindir, None)
        self.assertEqual(args.no_bindir, False)


if __name__ == "__main__":
    unittest.main()
