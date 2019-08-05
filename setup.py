from setuptools import setup, find_packages


with open('README.md') as f:
    README = f.read()

setup(
    name='textractor',
    version='0.2.1',
    description='Extracting build-essential files from a LaTeX project and zip them.',
    long_description=README,
    long_description_content_type="text/markdown",
    keywords=["tex", "latex", "zip"],
    maintainer='Christian Burkert',
    maintainer_email='textractor@cburkert.de',
    url='https://github.com/cburkert/textractor',
    license="MIT",
    packages=find_packages(exclude=('tests', 'docs')),
    python_requires='>=3.6',
    install_requires=[
        'click>=7',
    ],
    entry_points={
        'console_scripts': [
            'textract = textractor.textractor:textract'
        ]
    },
    classifiers=[
        "Topic :: Software Development :: Version Control :: Git",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Operating System :: OS Independent",
    ],
)
