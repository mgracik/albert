Albert
======

Albert is a simple markov chain chat bot. It can be run in an interactive mode
or as an IRC bot.

In the interactive mode, you need to supply a path to the training text, from
which Albert will generate his replies.

In the IRC mode, you need to supply a channel name and the owner's nickname.
Only the owner can tell Albert to quit, with the command `!quit`. Albert
learns all the messages he receives, or sees on the IRC channel, but replies
only to those containing his nickname.

Note: The package also contains the War and Peace book by Leo Tolstoy, which
can be used as the training text.

Installation
------------

`cd` into the project directory and run:

    make && sudo make install

Usage
-----

Interactive mode:

    albert <filename>

IRC mode:

    albert-irc -c <channel> -o <owner> [-s server] [-p port] [-n nickname]
