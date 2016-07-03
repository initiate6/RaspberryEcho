from distutils.core import setup
setup(name='RaspberryEcho',
      version='0.1',
      description='Pi client for Amazon\'s Alexa Service',
      author='INIT6, Sam Machin',
      author_email='init6@init6.me',
      url='https://github.com/initiate6/RaspberryEcho',
      packages=['raspberry_echo',],
      long_description=open('README.md').read(),
      install_requires=[
        "Wave",
        "requests",
        "wsgiref",
        "CherryPy",
        "python-vlc",
        "netifaces",
      ],
      )
