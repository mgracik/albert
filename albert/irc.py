# Copyright (c) 2012 Martin Gracik
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# Author(s): Martin Gracik <martin@gracik.me>
#

import logging
import re

from twisted.internet import protocol, reactor
from twisted.words.protocols import irc

import albert


class AlbertIRCClient(irc.IRCClient):

    def signedOn(self):
        print('signed on as %s' % self.nickname)
        self.albert = albert.Albert()
        try:
            self.albert.load()
        except IOError:
            pass

        self.join(self.channel)

    def joined(self, channel):
        print('joined %s' % channel)

    def privmsg(self, user, channel, msg):
        if not user:
            return

        username = user.split('!', 1)[0]
        do_reply = False
        if self.nickname in msg:
            do_reply = True
            msg = re.sub(r'^%s[:,]{0,1}\s*' % self.nickname, r'', msg, flags=re.I)
            if self._process_command(username, msg):
                return

        msg = re.sub(r'^(\w+)[:,]{1}', r'', msg)
        self.factory.log.debug('>>> %s', msg)
        reply = self.albert.communicate(msg, reply=do_reply)
        self.factory.log.debug(reply)
        if reply:
            self.msg(self.channel, '%s: %s' % (username, reply))

    def _process_command(self, username, msg):
        if username != self.owner:
            return False

        if msg in ('!q', '!quit'):
            self.quit()
            self.albert.save()
            return True

    @property
    def channel(self):
        return self.factory.channel

    @property
    def nickname(self):
        return self.factory.nickname

    @property
    def owner(self):
        return self.factory.owner


class AlbertIRCClientFactory(protocol.ClientFactory):

    protocol = AlbertIRCClient

    def __init__(self, channel, nickname, owner):
        self.log = logging.getLogger('albert.IRC')
        self.channel = channel
        self.nickname = nickname
        self.owner = owner

    def clientConnectionFailed(self, connector, reason):
        print('connection failed')
        reactor.stop()

    def clientConnectionLost(self, connector, reason):
        print('connection lost')
        reactor.stop()
