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
    author='zhouqian1',
    author_email='zhouqian1@xunlei.com',
    url='https://xlbj-gitlab.xunlei.cn/shoulei-service/gmaster',
)
