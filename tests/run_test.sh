python3 -m pytest --cov=. -vs test_ma.py  --cov-report html:htmlcov
echo "Report written to $PWD/htmlcov/index.html"
