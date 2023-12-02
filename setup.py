from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in rmrs/__init__.py
from rmrs import __version__ as version

setup(
	name="rmrs",
	version=version,
	description="Rmrs system",
	author="verendra",
	author_email="veeren107778@gmail.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
