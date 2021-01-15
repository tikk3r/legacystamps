import setuptools

with open('README.md', 'r') as f:
    long_desc = f.read()

setuptools.setup(
    name='legacystamps',
    version='1.0.0',
    author='Frits Sweijen',
    author_email='frits.sweijen@gmail.com',
    description='Small module to retrieve cutouts from the Legacy Survey.',
    long_description=long_desc,
    long_description_content_type='text/markdown',
    url='https://github.com/tikk3r/legacystamps',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    install_requires=[
        'requests',
        'tqdm',
    ],
)
