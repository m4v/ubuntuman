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

import supybot.log as log
from urllib2 import urlopen, Request
from urllib import quote

class ManpageCache:
    """
    Class implementing the manual page cache.
    """

    def __init__(self, baseurl, cachedir):
        self.header = { 'User-agent':'Mozilla/5.0 (compatible; UbuntuMan '\
                'Supybot plugin/2.0.0a' }
        self.baseurl = baseurl
        self.cachedir = cachedir
        #self.parsers = {'en': en.ManpageParser} # XXX 'en' isn't defined yet

    def __buildUrl(self, release, section, command, language):
        """Build URL to a manual page."""
        url = '%s/manpages.gz/%s/%s/man%s/%s.%s.gz' % (self.baseurl(), release,
                language, section, command, section)
        url = quote(url)
        # XXX check if is a valid url? probably better not to.
        return url

    def __tryUrl(self, url):
        """Try to open the given URL.  If succeeds, returns it's file
        descriptor; otherwise returns None."""
        try:
            request = Request(url, header=self.header)
            return urlopen(request)
        except:
            return None

    def __getManPageFd(self, release, language, command):
        """Get a file descriptor to the manual page in the Ubuntu Manpage
        Repository."""
        if language == 'en':
            languages = (language, )
        else:
            languages = (language, 'en')
        for section in ('1', '5', '8'): # XXX sections hardcoded for now
            for language in languages:
                url = self.__buildUrl(release, section, command, language)
                log.debug('ManpageCache.__getManPageFd: Trying url %s' % url)
                fd = self.__tryUrl(url)
                if fd:
                    log.debug('ManpageCache.__getManPageFd: Success.')
                    return fd
        return None

    def download(self, release, language, command):
        """
        Download, parse and cache locally the manual page from the configured
        online manual page repository. Returns the manual page as a dictionary.
        """

        assert(type(self.baseurl()) is str)

        fd = self.__getManPageFd(release, language, command)
        if fd:
            # TODO decompress, parse, and cache it
            return 'got something I don\'t know what to do with!'
        return None

    def fetch(self, release, language, command):
        """
        Fetches the requested manual page from the cache or downloads it from
        the online repository.
        """

        assert(type(self.cachedir) is str)
        assert(type(release) is str)
        assert(type(language) is str)
        assert(type(command) is str)

        try:
            # Open the cached manual page.
            path = "%s/%s/%s/%s.repr" % \
                (self.cachedir, release, language, command)
            return eval(open(path, "r").read())
        except:
            # Not found or eval error; download from the online repo.
            return self.download(release, language, command)

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
