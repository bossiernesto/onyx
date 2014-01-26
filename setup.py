from setuptools import setup, find_packages
import os

PATH = os.path.dirname(os.path.abspath(__file__))
templates_dir = os.path.join(PATH, ".")
templates_files = [os.path.join(templates_dir, file) for file in os.listdir(templates_dir)]

setup(name='Onyx',
      version='0.0.1b',
      description='General purpose scrapper for the web',
      author='Ernesto Bossi',
      author_email='bossi.ernestog@gmail.com',
      license='BSD',
      keywords='Onyx scrapper',
      packages=find_packages(exclude=["test", "code_swarm"]),
      data_files=[
          (templates_dir, templates_files)
      ],
      install_requires=['lxml', 'simplejson', 'json', 'coucbdb', 'elixir', 'pymongo', 'ordereddict', 'pillow']
      #TODO: fill another dependecies
)
