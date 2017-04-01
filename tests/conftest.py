# Put this in the conftest.py at the top of your unit tests folder,
# so it's available to all unit tests
import pytest
import _socket_toggle


# def pytest_runtest_setup():
#     """ disable the interet. test-cases can explicitly re-enable """
#     _socket_toggle.disable_socket()


@pytest.fixture(scope='function')
def disable_socket(request):
    """ re-enable socket.socket for duration of this test function """
    _socket_toggle.disable_socket()
    request.addfinalizer(_socket_toggle.enable_socket)