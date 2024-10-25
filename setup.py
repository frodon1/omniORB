#!/usr/bin/env python3

import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

import setuptools
from setuptools import Extension, setup
from setuptools.command.build_ext import build_ext

this_dir = Path(__file__).parent
os.chdir(this_dir)

python_dir = 'omniORBpy/' + ('python' if sys.version_info[0] == 2 else 'python3')

setup_args = dict()


if platform.system() == 'Windows':
    python_dir = 'omniORB/src/lib/' + python_dir
    class my_build_ext(build_ext):
        def build_extension(self, ext):
            # shutil.copyfile(os.path.join(this_dir, r'' % sys.version_info[0:2]), self.get_ext_fullpath(ext.name))
            src = this_dir / 'omniORB' / 'lib' / 'x86_win32' / f"{ext.name}.pyd"
            dest = self.get_ext_fullpath(ext.name)
            shutil.copyfile(src, dest)

    setup_args['ext_modules'] = [
        Extension(name,
                ['_build_with_make.cpp'],
                libraries=['omniorb'],
                ) for name in  ['_omnipy', '_omniConnMgmt', '_omnicodesets',
    # FIXME do we need this or others: _omnisslTP
    ]]
    setup_args['cmdclass'] = {'build_ext': my_build_ext}
    # setup_args['data_files'] = [r"omniORB\bin\x86_win32\omniORB423_vc14_rt.dll"],
    setup_args['data_files'] = [
        ("lib\\site-packages",
         [r"omniORB\bin\x86_win32\omniORB423_vc14_rt.dll",
          r"omniORB\bin\x86_win32\omnithread41_vc14_rt.dll"]
        )
    ]
    setup_args["package_dir"] = {'': python_dir}
    setup_args["packages"] = setuptools.find_packages(where=python_dir)

elif platform.system() == "Linux":
    install_dir = "install/usr/local"
    site_lib = f"lib/python{'.'.join(platform.python_version_tuple()[:2])}/site-packages"
    lib_dir = this_dir / install_dir / site_lib
    
    class my_build_ext(build_ext):
        def run(self):
            print(">>>> Running build.sh script")
            subprocess.check_call(['bash', f"{this_dir}/build.sh"])
            Path(self.build_lib).mkdir(parents=True, exist_ok=True)
            for path in os.listdir(lib_dir):
                p = Path(lib_dir, path)
                if p.suffix == ".egg-info":
                    continue
                if p.is_file():
                    shutil.copyfile(p, Path(self.build_lib) / p.name)
                if p.is_dir():
                    shutil.copytree(p, Path(self.build_lib) / p.name)
            super().run()
        def build_extension(self, ext):
            print(f">>>> Building extension {ext.name}")
            # install_omniorb/usr/local/lib/python3.9/site-packages
            dest_dir = Path(self.get_ext_fullpath(ext.name)).parent
            dest_dir.mkdir(parents=True, exist_ok=True)
            for lib in lib_dir.glob(f"{ext.name}*.so"):
                dest = dest_dir / lib.name
                shutil.copyfile(lib, dest)

    setup_args['ext_modules'] = [
        Extension(name,
                ['_build_with_make.cpp'],
                libraries=['omniorb'],
                ) for name in  ['_omnipy', '_omniConnMgmt', '_omnicodesets', '_omniidl', '_omniZIOP']
    ]

    setup_args['cmdclass'] = {'build_ext': my_build_ext}
    setup_args['data_files'] = [
        ("include", ["omniORBpy/include/omniORBpy.h"]),
        ]
    setup_args["package_dir"] = {'': python_dir}
    setup_args["packages"] = setuptools.find_packages(where=".")

else:
    raise ValueError('non-Windows and non-Linux platforms are unimplemented')

setup(**setup_args)
