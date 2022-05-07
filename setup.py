from setuptools import setup

setup(
    name='translator',
    version='0.0.0',
    packages=['translator'],
    url='',
    license='',
    author='Noelle Falk',
    author_email='n.falk@ymail.com',
    description='English to German translator',
    install_requires=['fastapi[all]',
                      'uvicorn',
                      'tensorflow-serving-api',
                      'pyonmttok>=1.14.0,<2',
                      'tensorflow',
                      'grpcio',
                      'redis']  # dependencies
)
