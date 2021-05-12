import setuptools


setuptools.setup(
    name='upldr_apilibs',
    version='0.1.21',
    author="Gage LeBlanc",
    author_email="gleblanc@symnet.io",
    description="Upldr Library for apiserver",
    long_description_content_type="text/markdown",
    url="https://github.com/gageleblanc/upldr",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'clilib>=1.9.10'
    ],
    include_package_data=True,
)
