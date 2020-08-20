import setuptools

with open("readme.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='upldr',
    version='1.6.0',
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
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'pyyaml', 'requests'
    ],
    data_files=[
        ("upldr_config", ["upldr_config/modules.json"])
    ],
    include_package_data=True,
)
