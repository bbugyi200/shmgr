"""setup.py file for shmgr_dummy_lib package."""

from setuptools import find_namespace_packages, setup


setup(
    entry_points={"shmgr": ["dummy_lib = shmgr_dummy_lib.impl"]},
    include_package_data=True,
    install_requires="shmgr",
    name="shmgr-dummy-lib",
    package_data={"shmgr_dummy_lib.data.dummy": ["*.sh"]},
    package_dir={"": "src"},
    packages=find_namespace_packages(where="src"),
    version="3.0.0",
)
