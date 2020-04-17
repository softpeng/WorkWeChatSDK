try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='WorkWeChat',
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
)
