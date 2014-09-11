#!/usr/bin/python
# vim: set fileencoding=utf-8 :
#
# (C) 2014 Guido Günther <agx@sigxcpu.org>
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

import unittest
from mock import patch

from industriart.artifactory import Artifactory

def request_mock(http_method, url, params):
        return http_method, url, params

class TestArtifactory(unittest.TestCase):
    def test_copy(self):
        a = Artifactory('http://a.exmple.com')
        with patch.object(Artifactory, '_request') as mocked_request:
            mocked_request.side_effect = request_mock
            ret = a.copy(('unstable','/foo'), ('release', 'bar'))
            self.assertEquals(ret[0], 'POST')
            self.assertEquals(ret[1], 'http://a.exmple.com/api/copy/unstable/foo')
            self.assertDictEqual(ret[2], {'to': 'release/bar'})

            # src needs to be a two element tuple
            with self.assertRaises(ValueError):
                a.copy('unstable', ('release', 'bar'))
            with self.assertRaises(TypeError):
                a.copy(10, ('release', 'bar'))

            # dst needs to be a two element tuple
            with self.assertRaises(ValueError):
                a.copy(('unstable', 'foo'), 'release')
            with self.assertRaises(TypeError):
                a.copy(('unstable', 'foo'), 10)


    def test_move(self):
        a = Artifactory('http://a.exmple.com')
        with patch.object(Artifactory, '_request') as mocked_request:
            mocked_request.side_effect = request_mock
            ret = a.move(('unstable','foo'), ('release', 'bar'))
            self.assertEquals(ret[0], 'POST')
            self.assertEquals(ret[1], 'http://a.exmple.com/api/move/unstable/foo')
            self.assertDictEqual(ret[2], {'to': 'release/bar'})

    def test_filecopy(self):
        a = Artifactory('http://a.exmple.com')
        with patch.object(Artifactory, '_request') as mocked_request:
            mocked_request.side_effect = request_mock
            ret = a.get_fileinfo('unstable', '/foo')
            self.assertEquals(ret[0], 'GET')
            self.assertEquals(ret[1], 'http://a.exmple.com/api/storage/unstable/foo')
            self.assertIsNone(ret[2])
