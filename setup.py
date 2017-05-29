from setuptools import setup, find_packages

version = '0.1.1'

setup(
    name="helga-alias",
    version=version,
    description=('track nick changes'),
    long_description=open('README.rst').read(),
    classifiers=[
        'Development Status :: 1 - Planning',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='irc bot alias',
    author='Justin Caratzas',
    author_email='bigjust@lambdaphil.es',
    license='LICENSE',
    packages=find_packages(),
    include_package_data=True,
    py_modules=['helga_alias'],
    zip_safe=True,
    entry_points = dict(
        helga_plugins = [
            'alias = helga_alias:alias',
        ],
    ),
)
