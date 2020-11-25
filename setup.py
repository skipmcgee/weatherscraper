#!/usr/bin/env python3
# coding:UTF-8

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="The_Looters_WeatherApp",
    version="1.0.0",
    author="Skip McGee",
    author_email="davidfranklinmcgee@gmail.com",
    description="Weather Application for displaying the weather in two different locations, written by 'The Looters'",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/skipmcgee/weatherscraper",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: Microsoft :: Windows",
    ],
    python_requires='>=3.7',
)
