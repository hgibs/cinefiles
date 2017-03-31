git pull
git commit -m ''
git push
bumpversion patch
python setup.py sdist bdist_wheel

twine

# pip install --upgrade cinefiles