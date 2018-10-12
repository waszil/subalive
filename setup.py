from setuptools import setup

setup(name='subalive',
      version='0.1',
      description='Subprocess with alive keeping',
      url='https://github.com/waszil/subalive',
      author='csaba.nemes',
      author_email='waszil.waszil@gmail.com',
      long_description=open('README.md').read(),
      long_description_content_type="text/markdown",
      packages=['subalive'],
      install_requires=[
          'subprocess', 'xmlrpc', 'threading'
      ],
      zip_safe=False)
