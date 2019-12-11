YELLOW='\033[1;33m'
NC='\033[0m'
echo -e "${YELLOW}- - - - - - - - - - - - - - - - - - - - - - - - - - - - -${NC}"
echo -e "${YELLOW}Building package:${NC}"
python3 setup.py sdist bdist_wheel
echo -e "${YELLOW}- - - - - - - - - - - - - - - - - - - - - - - - - - - - -${NC}"
echo -e "${YELLOW}Uploading package:${NC}"
echo -e "${YELLOW}Username is: dsw7${END}"
echo -e "${YELLOW}Password is: *********${NC}"
python3 -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*
echo -e "${YELLOW}Done!${NC}"
echo -e "${YELLOW}- - - - - - - - - - - - - - - - - - - - - - - - - - - - -${NC}"

