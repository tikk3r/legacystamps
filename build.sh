# Remove old builds.
rm -rf build/ dist/ legacystamps.egg-info/

# Build the package.
python setup.py sdist bdist_wheel

# Upload to PyPi
#python3 -m twine upload --repository-url https://test.pypi.org/legacy/ dist/* --verbose
python3 -m twine upload dist/* --verbose
