from distutils.core import setup

version = __import__('albert').__version__

setup(name='albert',
      version=version,
      description='Albert',
      author='Martin Gracik',
      author_email='martin@gracik.me',
      url='http://',
      download_url='http://',
      license='GPLv2+',
      packages=['albert'],
      scripts=['bin/albert', 'bin/albert-irc'],
      data_files=[('share/albert', ['data/pg2600.txt'])]
      )
