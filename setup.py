from setuptools import setup

from gmaster import __version__


setup(
    name='gmaster',
    version=__version__,
    description='A gRPC management tool like Gunicorn',
    packages=['gmaster'],
    entry_points={
        'console_scripts': ['gmaster=gmaster:console_main'],
    },
    author='eddyzhou',
    author_email='zhouqian1103@gmail.com',
    url='https://github.com/eddyzhou/gmaster',
)
