After installing requirements.txt run the below in order in venv
python -m ensurepip --upgrade
python -m pip install --upgrade pip
python -m pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl
python -m spacy validate