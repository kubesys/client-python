from setuptools import setup

setup(
    name='kubesys',
    version='2.0.0',
    keywords='k8s',
    description='a python-based wrapper library for kubernetes-calls',
    author='a_flying_fish',
    license='MIT',
    author_email='yutian20@otcaix.iscas.ac.cn, wuheng@iscas.ac.cn',
    packages=['kubesys'],
    install_requires=['requests>=2.31.0', 'pyyaml>=6.0', 'cryptography>=41.0.1']
)