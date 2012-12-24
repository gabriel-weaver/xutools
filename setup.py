import os

from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))

setup(name='xutools',
      version='0.0.1',
      description='XUTools',
      long_description='',
      classifiers=[
        'Programming Language :: Python',
        ],
      author='',
      author_email='',
      url='',
      keywords='',
      # packages=find_packages(),
      packages=['xutools', ],
      package_dir={'': 'src'},
      include_package_data=True,
      zip_safe=False,
      test_suite='',
      install_requires=['numpy==1.6.2', 'pyparsing==1.5.6'],
      entry_points='''\
      [console_scripts]
      ''',
      scripts=['src/xutools/cmd/xudiff.py', 'src/xutools/cmd/xugrep.py',
        'src/xutools/cmd/xuwc.py'],
      )
