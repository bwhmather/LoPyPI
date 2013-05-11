from distutils.core import setup

setup(
    name='LoPyPI',
    version='0.0.1',
    description="A local PyPi server and PyPi caching proxy",
    author='Ben Mather',
    author_email='bwhmather@bwhmather.com',
    url='https://github.com/bwhmather/lopypi',
    packages=['lopypi'],
    scripts=['lopypi-server', 'lopypi-proxy'],
    include_package_data=True,
    package_data={'lopypi': ['templates/*.html']},
    install_requires=[
        'Flask',
        'requests',
        'beautifulsoup4',
    ]
)
