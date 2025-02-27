from setuptools import setup, find_packages
setup(name='accessibility_checker', version='0.1', packages=find_packages(
    where='src'), package_dir={'': 'src'}, python_requires='>=3.11',
    install_requires=['PyMuPDF==1.22.5', 'numpy>=1.21.0', 'pandas>=1.3.0',
    'pytesseract>=0.3.8', 'opencv-python>=4.5.0', 'Pillow>=8.0.0',
    'pdf2image>=1.16.0', 'tqdm>=4.62.0', 'pyyaml>=5.4.0', 'openpyxl>=3.0.0',
    'pikepdf>=8.3.0', 'python-xmp-toolkit>=2.0.2', 'fastapi>=0.68.0',
    'uvicorn>=0.15.0', 'python-multipart>=0.0.5'], entry_points={
    'console_scripts': ['pdf-accessibility=accessibility_checker.main:main',
    'pdf-accessibility-web=accessibility_checker.web.api.main:main']})
