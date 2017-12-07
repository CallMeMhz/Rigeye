from setuptools import setup

setup(
    name='rigeye',
    version='0.5',
    author='callmemhz',
    author_email='callmemhz@gmail.com',
    url='callmemhz.github.io',
    packages=['rigeye'],
    include_package_data=True,
    install_requires=[
        'flask', 'bson', 'pymongo', 'apscheduler'
    ],
)