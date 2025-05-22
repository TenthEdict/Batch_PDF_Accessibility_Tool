#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(
    name="pdf-accessibility-tools",
    version="1.0.0",
    description="Tools for enhancing and validating PDF accessibility",
    author="Broderick Schipp",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "pikepdf>=5.0.0",
        "PyMuPDF>=1.19.0",
        "opencv-python-headless>=4.5.0",
        "pytesseract>=0.3.8",
        "Pillow>=9.0.0",
        "numpy>=1.20.0",
    ],
    entry_points={
        'console_scripts': [
            'access-cli=accessibility_tools.access_cli:main',
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering :: Image Processing",
        "Topic :: Utilities",
    ],
)