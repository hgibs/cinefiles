# A setuptools based setup module.
# See:
# https://packaging.python.org/en/latest/distributing.html
# https://github.com/pypa/sampleproject

#codecov skip start

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'PYPI-README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='cinefiles',
    
    version='1.1.1',

    description='Organize your movie folder and files',
    long_description=long_description,

    # The project's main homepage.
    url='https://github.com/hgibs/cinefiles',

    # Author details
    author='Holland Gibson',
    author_email='cinefiles-hgibs@googlegroups.com',

    # Choose your license
    license='Apache 2.0',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 5 - Production/Stable',

        # Indicate who your project is intended for
        'Intended Audience :: End Users/Desktop',
        'Topic :: Desktop Environment :: File Managers',
        'Topic :: Games/Entertainment',
        

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: Apache Software License',


        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
 #        'Programming Language :: Python :: 2',
#         'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
#         'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],

    keywords='movies organization folder',

    packages=find_packages('src'),
#     packages = [],
    package_dir={'': 'src'},
#     package_data={'': ['src/cinefiles/resources']},
    include_package_data=True,
#     entry_points = {'console_scripts': 
#                         ['cinefiles=cinefiles.__main__:main_cfiles',
#                         'cinefolders=cinefiles.__main__:main_cfolders'],},

    install_requires=[  'requests<3,>=2.4.3',
                        'youtube_dl>=2017.2.17',
                        'guessit<3,>=2.1.1',
                        'pycountry<18,>=17.0.0',
                        'google-api-python-client<2,>=1.6.2',
                        'lxml<4,>=3.7.3',
    ],
    
    # $ pip install -e .[dev,test]
    extras_require={
        'dev': ['twine','wheel'],
        'test': ['codecov','pytest','pytest-pep8','pytest-cov',
                'pytest-console-scripts'],
    },
)
#codecov skip end