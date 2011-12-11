"""
Flask-Github
------------

Adds support to authorize users with Github to Flask.
"""
from setuptools import setup


setup(
    name='Flask-Github',
    version='0.1.0',
    url='http://github.com/jarodl/flask-github',
    license='MIT',
    author='Jarod Luebbert',
    author_email='jarodluebbert@gmail.com',
    description='Adds support for authorizing users with Github to Flask',
    long_description=__doc__,
    packages=['flaskext'],
    namespace_packages=['flaskext'],
    zip_safe=False,
    platforms='any',
    install_requires=[
        'Flask',
        'oauth2'
    ],
    classifiers=[
        'Development Status :: 1 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)

