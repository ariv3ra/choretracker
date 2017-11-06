from setuptools import setup

setup(name='choretracker',
      version='1.0',
      description='Alexa Skill for Chore Tracker',
      author='Angel Rivera',
      author_email='ariv3ra@gmail.com',
      url='http://www.python.org/sigs/distutils-sig/',
     install_requires=['flask','flask_ask','requests','pymongo',]
)
