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

from collections import defaultdict
import logging
import os
import pickle
import random
import time


DEFAULT_ORDER = 3
DEFAULT_SWAPWORDS = {}
DEFAULT_BANWORDS = []
DEFAULT_TIMEOUT = 3.0
DEFAULT_DBFILE = os.path.join(os.getenv('HOME'), '.albert-brain')
DEFAULT_REPLIES = ['wat', ':)']


class Albert(object):

    @staticmethod
    def tokenize(message):
        words = message.lower().split()
        # Remove the double quotes.
        words = [word.replace('"', '') for word in words]
        return words

    def __init__(self, order=DEFAULT_ORDER, swapwords=DEFAULT_SWAPWORDS,
                 banwords=DEFAULT_BANWORDS, timeout=DEFAULT_TIMEOUT):

        self.log = logging.getLogger('albert.Albert')
        self.order = order
        self.swapwords = swapwords
        self.banwords = banwords
        self.timeout = timeout
        self.forward = defaultdict(list)
        self.backward = defaultdict(list)
        self.dummy_replies = set(DEFAULT_REPLIES)

    def load(self, dbfile=DEFAULT_DBFILE):
        with open(dbfile, 'rb') as fileobj:
            self.order = pickle.load(fileobj)
            self.swapwords = pickle.load(fileobj)
            self.banwords = pickle.load(fileobj)
            self.forward = pickle.load(fileobj)
            self.backward = pickle.load(fileobj)
            self.dummy_replies = pickle.load(fileobj)

    def save(self, dbfile=DEFAULT_DBFILE):
        with open(dbfile, 'wb') as fileobj:
            pickle.dump(self.order, fileobj)
            pickle.dump(self.swapwords, fileobj)
            pickle.dump(self.banwords, fileobj)
            pickle.dump(self.forward, fileobj)
            pickle.dump(self.backward, fileobj)
            pickle.dump(self.dummy_replies, fileobj)

    def communicate(self, message, learn=True, reply=True):
        words = self.tokenize(message)
        self.log.debug(words)
        if learn:
            self.learn(words)
        if reply:
            return self.get_reply(words)

    def learn(self, words):
        if len(words) > self.order:
            self._add_chain(self.forward, words)
            self._add_chain(self.backward, list(reversed(words)))
        else:
            message = ' '.join(words)
            self.dummy_replies.add(message)

    def _add_chain(self, context, words):
        for i in range(len(words) - self.order):
            key = tuple(words[i:i + self.order])
            next_word = words[i + self.order]
            if next_word not in context[key]:
                context[key].append(next_word)

    def get_reply(self, words):
        keywords = self._get_keywords(words)
        if keywords:
            seed = random.choice(keywords)
            reply = self._generate_reply(seed)
            if reply and reply != words:
                return ' '.join(reply)
        return random.choice(list(self.dummy_replies))

    def _get_keywords(self, words):
        keywords = set()
        for word in words:
            word = self.swapwords.get(word, word)
            if word[0].isalnum() and word not in self.banwords:
                keywords |= set(k for k in self.forward if word in k)
        return list(keywords)

    def _generate_reply(self, seed):
        suffix = self._get_chain(self.forward, seed)
        suffix = suffix[self.order:] if suffix else []
        prefix = self._get_chain(self.backward, tuple(reversed(seed)))
        prefix.reverse()
        return prefix + suffix

    def _get_chain(self, context, start):
        words = list(start)
        starttime = time.time()
        while (time.time() - starttime) < self.timeout:
            if start in context:
                next_word = random.choice(context[start])
                words.append(next_word)
                start = tuple(words[-self.order:])
            else:
                break
        return words

    def train(self, filename):
        words = []
        with open(filename, 'r') as fileobj:
            for line in fileobj:
                line = line.strip()
                if line and not line.startswith('#'):
                    for word in line.split():
                        words.append(word)
                        if word[-1] in '.?!':
                            self.communicate(' '.join(words), reply=False)
                            words = []

    def interact(self):
        while True:
            try:
                message = raw_input('>>> ')
            except (EOFError, KeyboardInterrupt):
                break

            if message:
                print(self.communicate(message))
