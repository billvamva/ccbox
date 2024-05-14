from setuptools import setup

setup(
   name='ccbox',
   version='1.0',
   description='Virtual Drive Module',
   packages=['ccbox'],  #same as name
   install_requires=['wheel', 'bar', 'greek'], #external packages as dependencies
)
