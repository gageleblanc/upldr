import setuptools

with open("readme.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='upldr',
    version='1.0',
    scripts=['upldr'],
    author="Gage LeBlanc",
    author_email="gleblanc@symnet.io",
    description="A file transfer utility",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gageleblanc/upldr",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: GNU GPL v3",
        "Operating System :: OS Independent",
    ],

)
