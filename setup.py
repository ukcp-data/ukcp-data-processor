from setuptools import setup, find_packages
from ukcp_dp import __version__


def readme():
    with open("README.md") as f:
        return f.read()


reqs = [line.strip() for line in open("requirements.txt")]


GIT_REPO = "https://github.com/ukcp-data/ukcp-data-processor"

setup(
    name="ukcp-data-processor",
    version=__version__,
    description="Python library for reading, writing, processing and plotting UKCP data.",
    long_description=readme(),
    long_description_content_type="text/markdown",
    license="BSD - See ceda_example/LICENSE file for details",
    author="Antony Wilson",
    author_email="antony.wilson@stfc.ac.uk",
    url=GIT_REPO,
    packages=find_packages(),
    install_requires=["iris"],
    tests_require=["pytest"],
    classifiers=[
        "Development Status :: 2 - ???",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: ???",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Topic :: Scientific/Engineering",
    ],
    include_package_data=True,
    scripts=[],
    entry_points={},
    package_data={"ceda_example": ["LICENSE"]},
)
