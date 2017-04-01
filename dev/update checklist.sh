git pull

#Update HISTORY.md

git add HISTORY.md
git commit -m "Changelog for upcoming release 1.0.1."

python setup.py cinefiles develop

bumpversion patch

#generate pull request

#add new release for the newly created tag

python setup.py sdist bdist_wheel

twine upload dist/*