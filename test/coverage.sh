cd $(dirname "$0")
python3 -m pytest -vs test_errors.py --cov=../src --cov-report html:../htmlcov
echo "Path to coverage report: " && readlink -f ../htmlcov/index.html
cd -
