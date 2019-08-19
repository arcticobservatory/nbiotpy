from setuptools import setup

setup(name='nbiotpy',
      version='0.1',
      description='Python library for SARA N210 NB-IoT modem',
      url='https://vvgitlab.cs.uit.no/COAT/nb-iot-py',
      author='Sergiusz Michalik',
      author_email='lukasz.s.michalik@uit.no',
      license='GPL v3',
      packages=['nbiotpy'],
      install_requires=[
            'pyserial',
            'timeout_decorator'
      ],
      zip_safe=False)
