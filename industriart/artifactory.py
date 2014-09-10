# vim: set fileencoding=utf-8 :
#
# (C) 2014 Guido Gunther <agx@sigxcpu.org>
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

import logging
import os
import posixpath
import requests

log = logging.getLogger(__name__)

class ArtifactoryError(Exception):
    def __init__(self, msg, url, status_code=0):
        self.url = url
        self.status_code = status_code
        Exception.__init__(self, msg)

class ArtifactoryObjectNotFound(ArtifactoryError):
    """Object not found aka 404"""
    pass

class ArtifactoryNoPermission(ArtifactoryError):
    """Object not found aka 401"""
    pass

class Artifactory(object):
    """
    Extremely simple JFrog Artifactory API Wrapper

    :arg str base: The base URL of to connect to, e.g. 'http://example.com/artifactory'
    :arg str user: The user to connect as
    :arg str password: The user's password

    If not noted otherwise all methods return the deserialized JSON data.
    """
    def __init__(self, base, user=None, password=None):
        self.user = user
        self.password = password
        self.base = base

    def search_gavc(self, groupid=None, artifactid=None, version=None, classifier=None):
        """
        Query the artifactory via Groupid, ArtifacId, Version and classifier

        :arg str groupid: The group id to search for
        :arg str artifacid: The artifact id to search for
        :arg str version: The version to search for
        :arg str classifier: The classifier to search for (e.g. rpm)
        :returns: The URLs of the found items
        :rtype: list of str
        """
        path='api/search/gavc'
        param_map = {
            'groupid':    'g',
            'artifactid': 'a',
            'version':    'v',
            'classifier': 'c',
        }
        params = {}
        for k,v in locals().items():
            if k in param_map and v is not None:
                params[param_map[k]] = v

        url = posixpath.join(self.base, path)
        log.debug("Searching on %s with %s" % (url, params))
        return self.get(url, params)['results']


    def calc_yum_metadata(self, repository):
        """
        Recalculate YUM metadata

        :arg str repository: The repository to calculate the metadata for
        """
        url = posixpath.join(self.base, 'api/yum', repository)
        params = { 'async': 0 }
        log.debug("Refreshing on %s" % url)
        return self.post(url, params)

    def get_repositories(self):
        """
        Get available repositories
        """
        url = posixpath.join(self.base, 'api/repositories')
        return self.get(url)

    def _copy_or_move(self, action, source, target):
        try:
            if len(source) != 2:
                raise ValueError("Source tuple not (repo, path)")
        except TypeError:
            raise TypeError("Source must be a tuple")

        try:
            if len(target) != 2:
                raise ValueError("Target tuple not (repo, path)")
        except TypeError:
            raise TypeError("Source must be a tuple")

        url = posixpath.join(self.base,
                             'api', action,
                             source[0], source[1])
        dst = posixpath.join(target[0], target[1])

        log.debug("%s %s", action.capitalize(), url)
        # Parameter order matters for artifactory
        return self.post(url, {'to': dst})

    def copy(self, source, target):
        """
        Copy artifacts in the repository from soure to target

        :arg tuple source: The source in the form (repo, path) to copy
        :arg tuple target: The target in the form (repo, path) to copy
        """
        return self._copy_or_move('copy', source, target)

    def move(self, source, target):
        """
        Move artifacts in the repository from soure to target

        :arg tuple source: The source in the form (repo, path) to copy
        :arg tuple target: The target in the form (repo, path) to copy
        """
        return self._copy_or_move('move', source, target)

    def _transform_url(self, url):
        """
        Helper to rewrite URLs. All artifactory URLs are passed through this method
        in order to cope with broken installations where e.g. artifactory sits behind
        a reverse proxy but doesn't know about it.

        Rewrite this in derived classes as needed (but hopefully not).
        """
        return url


    @staticmethod
    def _parse_error(data):
        try:
            if data.has_key('errors'):
                return data['errors'][0]['message']
            return None
        except:
            return None


    def _request(self, http_method, url, params=None):
        """
        Perform a HTTP request on the artifactory
        """
        url = self._transform_url(url)
        auth = None

        if self.user and self.password:
            auth = requests.auth.HTTPBasicAuth(self.user, self.password)

        method = getattr(requests, http_method.lower())
        r = method(url, params=params, auth=auth)
        if r.status_code / 100 != 2:
            err = self._parse_error(r.json())
            if r.status_code == 404:
                raise ArtifactoryObjectNotFound(err or "Not found" % url,
                                                url,
                                                r.status_code)
            elif r.status_code == 401:
                raise ArtifactoryNoPermission(err or "Unauthorized" % url,
                                              url,
                                              r.status_code)
            raise ArtifactoryError(err or "Did not get a 2xx",
                                   url,
                                   r.status_code)
        if r.headers['content-type'].endswith('json'):
            return r.json()
        else:
            return r.text


    def get(self, url, params=None):
        """
        Perform a GET request on the artifactory

        :arg str url: The URL to perform the get request on
        :arg dict params: Additional URL params
        :returns: The retrieved data deserialized from JSON if the
            request returns JSON otherwise as plain string.
        """
        return self._request('GET', url, params)


    def post(self, url, params):
        """
        Perform a POST request on the artifactory

        :arg str url: The URL to perform the get request on
        :arg dict params: Additional URL params
        :returns: The retrieved data deserialized from JSON if the
            request returns JSON otherwise as plain string.
        """
        return self._request('POST', url, params)
