from setuptools import setup
from setuptools import find_packages


setup(
    name='cloudify-etcd-plugin',
    version='1.0.0',
    author='Jakub Cierlik',
    author_email='jakub.cierlik@amartus.com',
    license='LICENSE',
    zip_safe=False,
    packages=find_packages(exclude=['tests*']),
    install_requires=['cloudify-common>=4.4',
                      'openstacksdk==0.39.0',
                      'IPy==0.81',
                      'pycrypto==2.6.1'],
    test_requires=['mock', 'requests-mock'])
