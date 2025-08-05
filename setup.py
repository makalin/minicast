#!/usr/bin/env python3
"""
Setup script for Minicast package.
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="minicast",
    version="1.0.0",
    author="Minicast Team",
    author_email="team@minicast.dev",
    description="Ultra-Low-Bandwidth Reaction GIF Channel",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/minicast/minicast",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Multimedia :: Video",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Communications :: Chat",
    ],
    python_requires=">=3.9",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "minicast-transcode=transcode:main",
            "minicast-server=server:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="rtsp streaming gif video low-bandwidth",
    project_urls={
        "Bug Reports": "https://github.com/minicast/minicast/issues",
        "Source": "https://github.com/minicast/minicast",
        "Documentation": "https://github.com/minicast/minicast#readme",
    },
) 