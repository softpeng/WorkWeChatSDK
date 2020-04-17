try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='WorkWeChatSDK',
    version='20200416',
    packages=['work_wechat'],
    url='https://github.com/tonytony2020/WorkWeChatSDK',
    license='The MIT License',
    author='Tony Pang',
    author_email='tonypangtonypang@gmail.com',
    description='A non-official WorkWeChat SDK in Pythonic Python.',
    requires=[
        'requests',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
