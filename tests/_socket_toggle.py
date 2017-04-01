from __future__ import print_function
import socket
import sys

_module = sys.modules[__name__]

def disable_socket():
    """ disable socket.socket to disable the Internet. useful in testing.
    .. doctest::
        >>> # we'll try httplib a little later, but import it immediately, before tampering.
        >>> # hopefully this proves that the 'patch' doesn't have to happen before other imports.
        >>> import httplib
        >>> enable_socket() # should be able to call "enable" at any time, even when enabled...
        [!] socket.socket is UN-blocked, and the network can be accessed.
        >>> disable_socket()  # OK let's disable it.
        [!] socket.socket is now blocked. The network should be inaccessible.
        >>> socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        Traceback (most recent call last):
        ...
        RuntimeError: A test tried to use socket.socket without explicitly un-blocking it.
        >>> httplib.HTTPConnection("scanme.nmap.org:80").request("GET", "/")
        Traceback (most recent call last):
        ...
        RuntimeError: A test tried to use socket.socket without explicitly un-blocking it.
        >>> enable_socket()
        [!] socket.socket is UN-blocked, and the network can be accessed.
        >>> enable_socket() # twice in a row should work.
        [!] socket.socket is UN-blocked, and the network can be accessed.
        >>> disable_socket()
        [!] socket.socket is now blocked. The network should be inaccessible.
        >>> socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        Traceback (most recent call last):
        ...
        RuntimeError: A test tried to use socket.socket without explicitly un-blocking it.
        >>> enable_socket()
        [!] socket.socket is UN-blocked, and the network can be accessed.
    """
    setattr(_module, u'_socket_disabled', True)

    def guarded(*args, **kwargs):
        if getattr(_module, u'_socket_disabled', False):
            raise RuntimeError(
                u"A test tried to use socket.socket without explicitly un-blocking it.")
        else:
            # SocketType is a valid, public alias of socket.socket,
            # we use it here to avoid namespace collisions
            return socket.SocketType(*args, **kwargs)

    socket.socket = guarded

    print(u'[!] socket.socket is now blocked. The network should be inaccessible.')


def enable_socket():
    """ re-enable socket.socket to enable the Internet. useful in testing.
    """
    setattr(_module, u'_socket_disabled', False)
print(u'[!] socket.socket is UN-blocked, and the network can be accessed.')