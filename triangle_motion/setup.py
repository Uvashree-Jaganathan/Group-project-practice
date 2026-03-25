#!/usr/bin/env python3
from setuptools import setup, find_packages

package_name = 'triangle_motion'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/triangle_launch.py']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='uva',
    maintainer_email='uva@todo.todo',
    description='Triangle motion turtle in ROS 2',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'triangle_turtle = triangle_motion.triangle_turtle:main',
        ],
    },
)