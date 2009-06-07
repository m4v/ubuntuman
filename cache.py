# -*- Encoding: UTF-8 -*-
# Copyright (c) 2009 Henri Häkkinen, Elián Hanisch.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import supybot.log as log
import supybot.conf as conf
import supybot.utils as utils
from urllib import basejoin

class ManpageCache:
    """
    Class implementing the manual page cache.
    """

    def __init__(self, name):
        self.header = { 'User-agent':
                'Mozilla/5.0 (compatible; UbuntuMan Supybot plugin/2.0.0a' }
        self.baseurl = conf.supybot.plugins.UbuntuMan.baseurl
        self.sections = conf.supybot.plugins.UbuntuMan.sections
        self.cachedir = conf.supybot.directories.data.dirize(name)
        #self.parsers = {'en': en.ManpageParser} # XXX 'en' isn't defined yet

    def __buildUrl(self, release, section, command, language):
        """Build URL to a manual page."""
        url = 'manpages.gz/%s/%s/man%s/%s.%s.gz' % (release, language, section,
                command, section)
        url = basejoin(self.baseurl(), utils.web.urlquote(url))
        return url

    def __tryUrl(self, url):
        """Try to open the given URL.  If succeeds, returns it's file
        descriptor; otherwise returns None."""
        try:
            return utils.web.getUrlFd(url, headers=self.header)
        except Exception, e:
            #raise Exception, e # XXX we should handle timeouts and invalid
                                # urls errors
            return None

    def __getManPageFd(self, release, language, command):
        """Get a file descriptor to the manual page in the Ubuntu Manpage
        Repository."""
        for section in self.sections():
            url = self.__buildUrl(release, section, command, language)
            log.debug('ManpageCache.__getManPageFd: Trying url %s' % url)
            fd = self.__tryUrl(url)
            if fd:
                log.debug('ManpageCache.__getManPageFd: Success.')
                return fd
        return None

    def __unzip(self, path):
        """Returns a gzip file descriptor for reading a compressed file."""
        import gzip
        return gzip.open(path)

    def __makepath(self, release, language, file=''):
        """Returns path in cache for a given release and language."""
        return os.path.join(self.cachedir, release, language, file)

    def save(self, data, filename='', release='', language='', filepath=''):
        """Saves data in the cache, returns the path of the new file.
        The path is constructed with the filename, release, and language
        variables, or you can provide the complete path in filepath."""
        if not filepath:
            assert filename, 'Error: no filename or filepath suplied'
            filepath = self.__makepath(release, language, filename)
        path = os.path.dirname(filepath)
        if not os.path.exists(path):
            os.makedirs(path)
        log.info('ManpageCache.save: saving as %r.' % filepath)
        try:
            fd = open(filepath, 'w')
            fd.write(data)
            fd.close()
        except IOError, e:
            raise IOError, e
        return filepath

    def download(self, release, language, command, nocache=False):
        """
        Download, parse and cache locally the manual page from the configured
        online manual page repository. Returns the manual page as a dictionary.
        """
        # check if the .gz is cached, we don't download in that case.
        gzpath = self.__makepath(release, language, '%s.gz' % command)
        try:
            if nocache: raise Exception, 'nocache=True'
            fd = open(gzpath)
        except Exception, e:
            log.debug('ManpageCache.download: not using %s.gz from cache: %s'\
                    % (command, e))
            fd = self.__getManPageFd(release, language, command)
        if fd:
            # save gzip
            filepath = self.save(fd.read(), filepath=gzpath)
            fd.close()
            # read gzip
            fd = self.__unzip(filepath)
            manpage = fd.readline() # TODO we should do the parsing here!
            fd.close()
            self.save(manpage, '%s.repr' % command, release, language)
            return manpage
        return None

    def fetch(self, release, language, command):
        """
        Fetches the requested manual page from the cache or downloads it from
        the online repository.
        """

        try:
            # Open the cached manual page.
            path = self.__makepath(release, language, '%s.repr' % command)
            log.debug('ManpageCache.fetch: checking for %s.repr in cache.' %\
                    command)
            fd = open(path, 'r')
            str = fd.read()
            log.debug('ManpageCache.fetch: Success.')
            return str
        except Exception, e:
            log.debug('ManpageCache.fetch: Manpage for %s isn\'t cached: %s' %\
                    (command, e))
            return self.download(release, language, command)

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
