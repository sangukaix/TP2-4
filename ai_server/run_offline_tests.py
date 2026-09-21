"""Run unittest suites without network access; preserve Windows asyncio socket pairs.

python -m ai_server.run_offline_tests [ai_server.test_module ...]
No live model, database, or external HTTP connection is allowed.
"""
from pathlib import Path
import socket
import sys
import threading
import unittest
from unittest.mock import patch


def main():
    state = threading.local()
    original_connect, original_pair = socket.socket.connect, socket.socketpair

    def internal_pair(*args, **kwargs):
        state.internal = True
        try:
            return original_pair(*args, **kwargs)
        finally:
            state.internal = False

    def offline_connect(sock, address):
        if getattr(state, 'internal', False):
            return original_connect(sock, address)
        raise OSError('Offline test: network connections are disabled')

    names = sys.argv[1:] or ['ai_server.' + path.stem for path in sorted(Path(__file__).parent.glob('test_*.py'))]
    with patch.object(socket, 'socketpair', internal_pair), patch.object(socket.socket, 'connect', offline_connect), patch.object(socket.socket, 'connect_ex', offline_connect):
        suite = unittest.defaultTestLoader.loadTestsFromNames(names)
        result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    raise SystemExit(main())
