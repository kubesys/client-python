from setuptools import setup

setup(
    name='kubesys',
    version='1.0.7',
    keywords='k8s',
    description='a python-based wrapper library for kubernetes-calls',
    author='a_flying_fish',
    license='MIT',
    author_email='a_flying_fish@outlook.com',
    packages=['kubesys'],
    install_requires=['requests>=0.0.0']
)