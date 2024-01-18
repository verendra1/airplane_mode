from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in revenue_management/__init__.py
from revenue_management import __version__ as version

setup(
	name="revenue_management",
	version=version,
	description="Revenue Management",
	author="Caratred Technologies",
	author_email="info@caratred.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
