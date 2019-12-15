import pytest

if __name__ == '__main__':
    pytest.main(['test_runner.py'])
    pytest.main(['-vs', 'test_ma.py'])
