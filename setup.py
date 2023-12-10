from setuptools import setup, find_packages

setup(
    name='RiaTableOcr',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        "pillow",
        "pytesseract",
        "keyboard",
        "numpy",
        "pyperclip"
    ],
    entry_points={
        'console_scripts': [
            'riatableocr=riatableocr.__main__:main',
        ],
    },
)
