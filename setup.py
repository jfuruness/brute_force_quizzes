from setuptools import setup, find_packages
import sys

setup(
    name='lib_brute_force_quizzes',
    packages=find_packages(),
    version='0.0.0',
    author='Justin Furuness',
    author_email='jfuruness@gmail.com',
    url='https://github.com/jfuruness/lib_brute_force_quizzes.git',
    download_url='https://github.com/jfuruness/lib_brute_force_quizzes.git',
    keywords=['Furuness', 'Assistant', 'Brute Force', 'Quizzes'],
    install_requires=[
        'pynput',
        'selenium==3.141.0',
        'unidecode'
    ],
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3'],
    entry_points={
        'console_scripts': 'lib_brute_force_quizzes = lib_brute_force_quizzes.__main__:main'},
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
)
