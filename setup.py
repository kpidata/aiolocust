import os, re, ast

from setuptools import setup, find_packages, Command

# parse version from __init__.py
_version_re = re.compile(r'__version__\s+=\s+(.*)')
_init_file = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                          'aiolocust',
                          "__init__.py")
with open(_init_file, 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))

LONG_DESCRIPTION = """Locust is a python utility for doing easy, distributed
load testing of a web site"""

install_requires = [
    "aiohttp==1.0.5",
    "aiohttp-jinja2==0.8.0",
    "async-timeout==1.0.0",
    "gevent==1.1.2",
    "flask>=0.10.1",
    "requests>=2.9.1",
    "msgpack-python>=0.4.2",
    "pyzmq==15.2.0"
]

tests_require = [
    'pytest-runner',
    'mock',
    'pytest',
]

setup(
    name='aiolocust',
    version=version,
    description='Website load testing framework',
    long_description=LONG_DESCRIPTION,
    classifiers=[
        "Topic :: Software Development :: Testing :: Traffic Generation",
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
    ],
    keywords='',
    author='KPIdata',
    author_email='kpidatahq@gmail.com',
    url='http://kpidata.org',
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require={
        'testing': tests_require,
        'dev': install_requires + tests_require
    },
    entry_points={
        'console_scripts': [
            'aiolocust = aiolocust.main:main',
        ]
    },
)
