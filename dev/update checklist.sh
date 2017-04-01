git pull
git commit -m ''
git push

bumpversion patch

python setup.py sdist bdist_wheel

twine upload dist/*

# pip install --upgrade cinefiles