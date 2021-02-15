"""Setup script"""
import setuptools
import os
import re

HERE = os.path.abspath(os.path.dirname(__file__))
VERSION_RE = re.compile(r"""__version__ = ['"]([0-9.]+)['"]""")
TESTS_REQUIRE = ["coverage", "nose", "pytest", "moto[s3]"]


def get_version():
    init = open(os.path.join(HERE, "endgame", "bin", "version.py")).read()
    return VERSION_RE.search(init).group(1)


def get_description():
    return open(
        os.path.join(os.path.abspath(HERE), "README.md"), encoding="utf-8"
    ).read()


setuptools.setup(
    name="endgame",
    include_package_data=True,
    version=get_version(),
    author="Kinnaird McQuade",
    author_email="kinnairdm@gmail.com",
    description="An AWS Pentesting tool that lets you use one-liner commands to backdoor an AWS account's resources with a rogue AWS account - or to the entire internet 😈",
    long_description=get_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/salesforce/endgame",
    packages=setuptools.find_packages(exclude=["test*"]),
    tests_require=TESTS_REQUIRE,
    install_requires=[
        "botocore",
        "boto3",
        "click",
        "policy_sentry>=0.11.5",
        "colorama",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={"console_scripts": "endgame=endgame.bin.cli:main"},
    zip_safe=True,
    keywords="aws iam security",
    python_requires=">=3.7",
)
