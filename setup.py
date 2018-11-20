#!/usr/bin/env python
import io
import re
from setuptools import setup, find_packages
import sys

with io.open('./automateExpenseReports/__init__.py', encoding='utf8') as version_file:
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file.read(), re.M)
    if version_match:
        version = version_match.group(1)
    else:
        raise RuntimeError("Unable to find version string.")


with io.open('README.rst', encoding='utf8') as readme:
    long_description = readme.read()


setup(
    name='automateExpenseReports',
    version=version,
    description='Automate expense reporting for Certify',
    long_description=long_description,
    author='Matt Keagle',
    author_email='keaglem@gmail.com',
    license='BSD license',
    packages=['automateExpenseReports'],
    package_data={'automateExpenseReports': ['input_info.json',
                                             'chromedriver.exe']},
    classifiers=[
        'Development Status :: 1 - Planning',
        'License :: OSI Approved :: BSD license',
    ],
    install_requires=[
    ],
    options={
        'app': {
            'formal_name': 'AutomateExpenseReports',
        },

        # Desktop/laptop deployments
        'macos': {
            'app_requires': [
            ]
        },
        'linux': {
            'app_requires': [
            ]
        },
        'windows': {
            'app_requires': [
                'pyqt5',
                'pandas',
                'selenium',
                'xlrd'
            ]
        },

        # Mobile deployments
        'ios': {
            'app_requires': [
            ]
        },
        'android': {
            'app_requires': [
            ]
        },

        # Web deployments
        'django': {
            'app_requires': [
            ]
        },
    }
)
