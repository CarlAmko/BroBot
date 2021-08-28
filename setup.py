from setuptools import setup

with open("README.md", 'r') as f:
	long_description = f.read()

setup(
	name='BroBot',
	version='1.0',
	description='Discord bot for the bros.',
	license="MIT",
	long_description=long_description,
	author='Carl Amko',
	author_email='carl@carlamko.me',
	install_requires=[]
)
