#!/usr/bin/python
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
import optparse
import sys

from industriart.artifactory import Artifactory, ArtifactoryError

def setup_logging(debug=False):
    logging.getLogger('industriart').addHandler(logging.StreamHandler())

    logger = logging.getLogger()
    level = logging.DEBUG if debug else logging.INFO
    logger.setLevel(level)



def main():
    parser = optparse.OptionParser()

    parser.add_option('-d', '--debug',
                      action="store_true",
                      default=False,
                      dest="debug",
                      help='Be more verbose.')
    parser.add_option('-a', '--artifactory-base',
                      dest="base",
                      help='Artifactory base URL to use.')
    parser.add_option('-u', '--user',
                      dest="user",
                      help='Artifactory user to use.')
    parser.add_option('-p', '--password',
                      dest="password",
                      help='Artifactory user\'s password to use.')

    (options, args) = parser.parse_args()
    setup_logging(options.debug)

    if options.base is None:
        logging.error("Artifactory url must be given.")
        return 1
    else:
        artifactory = Artifactory(options.base,
                                  options.user,
                                  options.password)

    if not len(args):
        logging.error("Which repo should I refresh?")
        return 1

    ret = 0
    for repo in args:
        try:
            msg = artifactory.calc_yum_metadata(repo)
            logging.info(msg)
        except ArtifactoryError as e:
            ret = 1
            logging.error("Refresh of %s failed with %d: %s",
                          e.url, e.status_code, str(e))

    return ret


if __name__ == '__main__':
    sys.exit(main())
