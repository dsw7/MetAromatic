dump="htmlcov"
python3 -m pytest --cov=. -vs test_ma.py  --cov-report html:$dump
echo "Report written to $(pwd)/$dump/index.html"
