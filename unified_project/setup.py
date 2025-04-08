from setuptools import setup, find_packages

setup(
    name="epubs-accessibility",
    version="1.0.0",
    description="Toolkit for enhancing document accessibility",
    author="Broderick Schipp",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.9",
    install_requires=[
        "PyMuPDF>=1.23.0",
        "pikepdf>=8.3.0",
        "pdf2image>=1.16.3",
        "Pillow>=10.0.0",
        "opencv-python>=4.8.0",
        "scikit-image>=0.21.0",
        "pytesseract>=0.3.10",
        "numpy>=1.24.0",
        "pandas>=1.5.0",
        "scipy>=1.7.0",
        "tqdm>=4.66.0",
        "python-xmp-toolkit>=2.0.2",
        "pyyaml>=6.0.0",
    ],
    extras_require={
        "ml": [
            "mlx-vlm>=0.0.3",
            "docling-core>=0.0.1",
            "huggingface-hub>=0.20.0",
            "anthropic>=0.18.0",
            "transformers>=4.49.0",
            "torch>=2.0.0",
        ],
        "docs": [
            "python-docx>=1.0.0",
            "python-pptx>=0.6.21",
            "openpyxl>=3.0.7",
        ],
    },
    entry_points={
        "console_scripts": [
            "epubs-enhance=epubs_accessibility.cli:main",
        ],
    },
)