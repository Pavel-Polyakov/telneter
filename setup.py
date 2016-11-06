#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name     = 'telneter',
    version  = '0.0.1',
    packages = find_packages(),
    description  = 'Telnet interface for popular network devices.',
    author       = 'Pavel Polyakov',
    author_email = 'polyakov.pavel.xyz@gmail.com',
    url          = 'https://github.com/Pavel-Polyakov/telneter',
    download_url = 'https://github.com/Pavel-Polyakov/telneter/archive/master',
    license      = 'MIT License',
    keywords     = 'telnet',
    classifiers  = [
        'Intended Audience :: Developers',
        'Programming Language :: Python',
    ],
)
