from setuptools import setup

setup(
    name='kubesys',
    version='1.0.7',
    keywords='k8s',
    description='a python-based wrapper library for kubernetes-calls',
    author='a_flying_fish',
    license='MIT',
    author_email='yutian20@otcaix.iscas.ac.cn, wuheng@iscas.ac.cn',
    packages=['kubesys'],
    install_requires=['requests>=0.0.0']
)