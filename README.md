# Conda Build Control

[toc]

At this stage in the game, "Conda Build Control" is a misnomer of sorts. Having originally set out to write a build system with little internal knowledge of how Conda worked, I quickly realized there were **very** few wheels that really needed to be reinvented.

CBC has organically morphed into a translator capable of generating Conda build recipes *on the fly* rather than becoming a replacement build system altogether. 

What does it translate? Well, Conda's recipe format consists of three or more files, each with their own purpose, and must be written by hand for each package. I felt like this was a major caveat, because each stage in the build was controlled by completely separate files. Files that need to be opened and closed repeatedly (more like constantly) during the creation process. In theory this is cool... you only need to change the bit that matters to the task at hand, but in practice, when working with a large convoluted recipes its extremely easy to get lost and/or frustrated.

The layout of a Conda recipe is as follows:

```
# d = dir, f = file

[d] hello_world
    \
    |-[f] meta.yaml     # RECIPE META DATA
    |-[f] build.sh      # *Nix build script
    |-[f] runtests.sh   # *Nix test script
    |-[f] bld.bat       # Windows build script
    |-[f] runtests.bat  # Windows test script
    |-[f] ...           # misc patches, files, etc.
```

Instead, cbc consolidates the layout and allows you to focus all recipe-related work into a single point of entry:

```
[d] hello_world
    \
    |-[f] hello_world.ini   # Single INI
    |-[f] ...               # misc patches, files, etc.
```


# Installation

CBC requires Python 3, and will not work under Python 2.

```bash
git clone https://bitbucket.org/jhunkeler/cbc
```

```bash
cd cbc
```

```bash
python setup.py install
```

# Configuration

**This will change to something more appropriate: stay tuned...**

CBC writes translated Conda recipes to a static directory, referenced by the `CBC_HOME` environment variable (primarily for house-keeping purposes). There is no default value, and an exception will be raised if it is undefined at run-time.

**Create a directory:**

The location is not important, so long as your account has read-write access. Your home directory is good place to start with.


```bash
mkdir -p ~/cbc-output
```

**Define CBC_HOME:**

```bash
export CBC_HOME=~/cbc-output
```

**CSH users will want to do this instead:**

```bash
setenv CBC_HOME ~/cbc-output
```

# Example Package

CBC assumes some basic knowledge of Conda packaging semantics, so if you are not familiar, or need a refresher, go ahead and [visit the documenation](http://conda.pydata.org/docs/build_tutorials/pkgs2.html).

```bash
mkdir ~/cbc-recipes
cd ~/cbc-recipes
```

```
mkdir cbc-test-package
touch cbc-test-package.ini
```

## Recipe Configuration (CBC INI FORMAT)

Copy the contents of the following example into `cbc-test-package.ini`:

```ini
[package]
name: cbc_test_package
version: 1.0.0

[about]
home: http://example.com/${package:name}
license: GPL
summary: ${package:name} is a test package

[source]
fn: ${package:name}-${package:version}.tar.gz
url: https://bitbucket.org/jhunkeler/cbc-recipes/downloads/${fn}

[build]
number: 1

[requirements]
build:
    setuptools
    python

run:
    python

[test]
imports:
    cbc_test_package

[cbc_build]
linux:
    python setup.py install || exit 1

windows:
    python setup.py install
    if errorlevel 1 exit 1

```

## Generating the Conda Recipe

Now execute `cbc_build --no-build` to translate the CBC recipe into a format Conda can use:

```bash
cbc_build --no-build cbc-test-package.ini

CBC_HOME is /Users/example/cbc-output
Using cbc build configuration: /Users/example/cbc-recipes/cbc-test-package/cbc_test_package.ini
Scripts written to /Users/example/cbc-output/cbc_test_package
```

Let's take a look at what has been generated beneath ~/cbc-output:

```
ls -l -R ~/cbc-output

/Users/example/cbc-output/cbc_test_package:
total 12
-rw-r--r-- 1 example example  47 Sep  3 13:39 bld.bat
-rw-r--r-- 1 example example  34 Sep  3 13:39 build.sh
-rw-r--r-- 1 example example 454 Sep  3 13:39 meta.yaml
```

**Windows build script (bld.bat):**

```windows
python setup.py install
if errorlevel 1 exit 1
```

***Nix build script (build.sh):**

```bash
python setup.py install || exit 1
```

**Conda Metadata (meta.yaml):**

As you can see below, the section headers and key pairs have been converted without a problem. If you haven't noticed a difference yet, then go back a take a look at how variables are defined and reused throughout the recipe. YAML, Conda's metadata format of choice, has very poor string interpolation capabilities, and is one of the driving factors for writing CBC in the first place.

Python's ConfigParser module, on the other hand, has decent string interpolation, and it highly customizable. YAML tends to be WYSIWYG unless you spend a considerable amount of time hacking it. 


All `$` characters in the `[cbc_build]` section must be shell-escaped if you do not want them to be interpolated as a variable. This behavior could be disabled but it would seemingly defeat the purpose of having interpolation to begin with. So be warned: this minor constriction can *easily* make for an ugly build script, yes, however the benefits tend to outweigh the caveats.

Just look at how pretty this is:

```yaml
about:
    home: http://example.com/cbc_test_package
    license: GPL
    summary: cbc_test_package is a test package
build:
    number: '1'
package:
    name: cbc_test_package
    version: 1.0.0
requirements:
    build:
    - setuptools
    - python
    run:
    - python
source:
    fn: cbc_test_package-1.0.0.tar.gz
    url: https://bitbucket.org/jhunkeler/cbc-recipes/downloads/cbc_test_package-1.0.0.tar.gz
test:
    imports:
    - cbc_test_package
```

## Building the Conda Recipe

Let's build this package instead of staring at it any further:

```
conda build --no-binstar-upload ~/cbc-output/cbc_test_package
```

**Output:**

```
Removing old build environment
Removing old work directory
BUILD START: cbc_test_package-1.0.0-py34_1
Fetching package metadata: ............
Solving package specifications: .
The following NEW packages will be INSTALLED:

    openssl:    1.0.1k-1
    pip:        7.1.2-py34_0
    python:     3.4.3-0
    readline:   6.2-2
    setuptools: 18.3.2-py34_0
    sqlite:     3.8.4.1-1
    tk:         8.5.18-0
    wheel:      0.26.0-py34_1
    xz:         5.0.5-0
    zlib:       1.2.8-0

Linking packages ...
[      COMPLETE      ]|#######################| 100%
Removing old work directory
Source cache directory is: /Users/example/anaconda/conda-bld/src_cache
Found source in cache: cbc_test_package-1.0.0.tar.gz
Extracting download
Package: cbc_test_package-1.0.0-py34_1
source tree in: /Users/example/anaconda/conda-bld/work/cbc_test_package-1.0.0
+ python setup.py install
running install
running bdist_egg
running egg_info
writing top-level names to cbc_test_package.egg-info/top_level.txt
writing dependency_links to cbc_test_package.egg-info/dependency_links.txt
writing cbc_test_package.egg-info/PKG-INFO
reading manifest file 'cbc_test_package.egg-info/SOURCES.txt'
writing manifest file 'cbc_test_package.egg-info/SOURCES.txt'
installing library code to build/bdist.macosx-10.5-x86_64/egg
running install_lib
running build_py
creating build
creating build/lib
creating build/lib/cbc_test_package
copying cbc_test_package/__init__.py -> build/lib/cbc_test_package
creating build/bdist.macosx-10.5-x86_64
creating build/bdist.macosx-10.5-x86_64/egg
creating build/bdist.macosx-10.5-x86_64/egg/cbc_test_package
copying build/lib/cbc_test_package/__init__.py -> build/bdist.macosx-10.5-x86_64/egg/cbc_test_package
byte-compiling build/bdist.macosx-10.5-x86_64/egg/cbc_test_package/__init__.py to __init__.cpython-34.pyc
creating build/bdist.macosx-10.5-x86_64/egg/EGG-INFO
copying cbc_test_package.egg-info/PKG-INFO -> build/bdist.macosx-10.5-x86_64/egg/EGG-INFO
copying cbc_test_package.egg-info/SOURCES.txt -> build/bdist.macosx-10.5-x86_64/egg/EGG-INFO
copying cbc_test_package.egg-info/dependency_links.txt -> build/bdist.macosx-10.5-x86_64/egg/EGG-INFO
copying cbc_test_package.egg-info/top_level.txt -> build/bdist.macosx-10.5-x86_64/egg/EGG-INFO
zip_safe flag not set; analyzing archive contents...
creating dist
creating 'dist/cbc_test_package-1.0.0-py3.4.egg' and adding 'build/bdist.macosx-10.5-x86_64/egg' to it
removing 'build/bdist.macosx-10.5-x86_64/egg' (and everything under it)
Processing cbc_test_package-1.0.0-py3.4.egg
Copying cbc_test_package-1.0.0-py3.4.egg to /Users/example/anaconda/envs/_build/lib/python3.4/site-packages
Adding cbc-test-package 1.0.0 to easy-install.pth file

Installed /Users/example/anaconda/envs/_build/lib/python3.4/site-packages/cbc_test_package-1.0.0-py3.4.egg
Processing dependencies for cbc-test-package==1.0.0
Finished processing dependencies for cbc-test-package==1.0.0
found egg: /Users/example/anaconda/envs/_build/lib/python3.4/site-packages/cbc_test_package-1.0.0-py3.4.egg
number of files: 2
Fixing permissions
Fixing permissions
BUILD END: cbc_test_package-1.0.0-py34_1
TEST START: cbc_test_package-1.0.0-py34_1
Fetching package metadata: ............
Solving package specifications: .
The following packages will be downloaded:

    package                    |            build
    ---------------------------|-----------------
    cbc_test_package-1.0.0     |           py34_1           2 KB

The following NEW packages will be INSTALLED:

    cbc_test_package: 1.0.0-py34_1
    openssl:          1.0.1k-1
    pip:              7.1.2-py34_0
    python:           3.4.3-0
    readline:         6.2-2
    setuptools:       18.3.2-py34_0
    sqlite:           3.8.4.1-1
    tk:               8.5.18-0
    wheel:            0.26.0-py34_1
    xz:               5.0.5-0
    zlib:             1.2.8-0

Fetching packages ...
cbc_test_package 100% |#####################| Time: 0:00:00   4.53 MB/s
Extracting packages ...
[      COMPLETE      ]|#######################| 100%
Linking packages ...
[      COMPLETE      ]|#######################| 100%
===== testing package: cbc_test_package-1.0.0-py34_1 =====
import: 'cbc_test_package'
/Users/example/anaconda/envs/_test/lib/python3.4/site-packages/cbc_test_package-1.0.0-py3.4.egg/cbc_test_package/__init__.py:2: UserWarning: cbc_test_package is only a test package!
===== cbc_test_package-1.0.0-py34_1 OK =====
TEST END: cbc_test_package-1.0.0-py34_1
```

`cbc_build` can, as the name suggests, build packages directly, but I don't recommend doing it. Why? Because its good for testing a quick build to see if it works; just not for the real deal. Conda has built-in mechanisms CBC does not provide (the list is many). Yes, this goes back to what I mentioned regarding not reinventing the wheel. CBC was *supposed* to be more than *it is* because at the time I didn't know Conda could *do more* than it *does*. I blame frantic poor planning.

How would you go about doing that? Simple enough:

```bash
cbc_build --no-upload ~/cbc-recipes/cbc_test_package.ini
```

The output will look roughly the same as before just massively out of order. Python's `subprocess` module seems to print output asynchronously for no apparent reason. By the time I realized this was happening I had already decided `cbc_build` would not be used as a true build tool.

No fix is likely.
