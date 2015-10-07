# Conda Build Control

[toc]

At this stage in the game, "Conda Build Control" is a misnomer of sorts. Having originally set out to write a build system with little internal knowledge of how Conda worked, I quickly realized there were **very** few wheels that really needed to be reinvented.

CBC has organically morphed into a translator capable of generating Conda build recipes *on the fly* rather than becoming a replacement build system altogether. 

What does it translate? The Conda recipe format consists of three or more files, each with their own purpose, and must be written by hand for each package. I felt like this was a major caveat, because each stage in the build was controlled by completely separate files. Files that need to be opened and closed repeatedly (more like constantly) during the creation process. In theory this is cool... you only need to change the bit that matters to the task at hand, but in practice, when working with a large convoluted recipes its extremely easy to get lost and/or frustrated.

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
git clone https://bitbucket.org/exampleeler/cbc
```

```bash
cd cbc
```

```bash
python setup.py install
```

# Obtaining STScI Recipes

The following repository provides the recipes maintained by STScI. Keep in mind, however, many of the recipes reference non-public git repositories. Depending on where you are and what you have access to, **these recipes may not work at all.** 

(See also: `git_url` and/or `url` directives in each .ini file).

```bash
cd ~
git clone https://bitbucket.org/exampleeler/cbc-recipes
```

# Configuration

**This will change to something more appropriate: stay tuned...**

CBC writes translated Conda recipes to a static directory, referenced by the `CBC_HOME` environment variable (primarily for house-keeping purposes). There is no default value, and an exception will be raised if it is undefined at run-time.

The companion environment variable, `CBC_RECIPES`, should be defined if you want to use the build wrapper, `cbc_monolith`.

**Create a directory:**

The location is not important, so long as your account has read-write access. Your home directory is good place to start with.


```bash
mkdir -p ~/cbc-output
```

**Define CBC_HOME:**

```bash
export CBC_HOME=~/cbc-output
export CBC_RECIPES=~/cbc-recipes
```

**CSH users will want to do this instead:**

```bash
setenv CBC_HOME ~/cbc-output
setenv CBC_RECIPES ~/cbc-recipes
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
url: https://bitbucket.org/exampleeler/cbc-recipes/downloads/${fn}

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
    url: https://bitbucket.org/exampleeler/cbc-recipes/downloads/cbc_test_package-1.0.0.tar.gz
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

`cbc_build` can, as the name suggests, build packages directly, but I don not recommend doing it. Why? Because its good for testing a quick build to see if it works; just not for the real deal. Conda has built-in mechanisms CBC does not provide (the list is many). Yes, this goes back to what I mentioned regarding not reinventing the wheel. CBC was *supposed* to be more than *it is* because at the time I didn't know Conda could *do more* than it *does*. I blame frantic poor planning.

How would you go about doing that? Simple enough:

```bash
cbc_build --no-upload ~/cbc-recipes/cbc_test_package.ini
```

The output will look roughly the same as before just massively out of order. Python's `subprocess` module seems to print output asynchronously for no apparent reason. By the time I realized this was happening I had already decided `cbc_build` would not be used as a true build tool.

No fix is likely.


# Working with cbc_monolith

> Monolith
> > noun: monolith; plural noun: monoliths
> >
> >  1. A large single upright block of stone, especially one shaped into or serving as a pillar or monument.

`cbc_monolith` provides a minimalistic approach to building several recipes in sequence, resulting in a *frozen build*. This is especially useful for hosted repositories that you do *not* want to change over the course of time, or perhaps you wish to control the rate at which they receive new packages. Either way, it was not designed to upload packages to anaconda.org. That functionality could be added in the future, but is not considered a high priority at the moment.

Below we will discuss two ways to use `cbc_monolith`, depending on your needs... but first...


## Configuration

As mentioned earlier this script requires both `CBC_HOME` and `CBC_RECIPES` be defined in your environment. It is also possible to pass these paths as arguments at run-time by issuing `--cbc-output-dir` and `--cbc-recipe-dir` respectively.

It is recommended `cbc_monolith` be executed from its own directory, because the log file(s) as well as input files generally create a lot of clutter.

```bash
mkdir -p ~/monolith
cd ~/monolith
```

## Usage Statement

```
usage: cbc_monolith {manifest} [-pnco]
    manifest                List of recipes to build (in order)
    --python            -p  Version to pass to conda-build
    --numpy             -n  Version to pass to conda-build
    --cbc-recipes       -c  Path to CBC recipes directory
    --cbc-output-dir    -o  Path to CONDA recipes
```

## Method 1 - Outer Scope

Assume the manifest, `outer.lst`, contains the following two packages:

```
stsci.tools
stsci.image

```

What happens when we run `cbc_monolith outer.lst`?

```
cbc_monolith outer.lst
[output truncated to show important details]

BUILD START: stsci.tools-0.0.0.git-py34_768
BUILD START: d2to1-0.0.0.git-py34_0
BUILD END: d2to1-0.2.12.git-py34_0
BUILD START: stsci.tools-0.2.12.git-py34_0
BUILD START: stsci.distutils-0.0.0.git-py34_1
BUILD END: stsci.distutils-0.0.0.git-py34_1
BUILD START: stsci.tools-0.0.0.git-py34_157
BUILD START: pyfits-0.0.0.git-py34_0
BUILD START: cfitsio-3.370-1
BUILD END: cfitsio-3.370-1
BUILD START: pyfits-0.0.0.git-py34_0
BUILD END: pyfits-v3.3.0.git-py34_8
BUILD START: stsci.tools-v3.3.0.git-py34_8
BUILD END: stsci.tools-0.0.0.git-py34_785
BUILD START: stsci.image-0.0.0.git-py34_785
BUILD START: stsci.convolve-0.0.0.git-py34_0
BUILD END: stsci.convolve-0.0.0.git-py34_37
BUILD START: stsci.image-0.0.0.git-py34_37
BUILD END: stsci.image-0.0.0.git-py34_45
```

You were only expecting to see two packages build, correct? Wrong. What's happening here is Conda's dependency resolution taking over. Notice `stsci.tools` shows up many times throughout the build, because as each dependency completes it jumps back to `stsci.tools` and continues scanning for, and building, additional dependencies. The same applies to `stsci.image`, albeit, it has far fewer requirements.

Indenting the output into a tree might help drive the concept home:

```
BUILD START: stsci.tools-0.0.0.git-py34_768
    BUILD START: d2to1-0.0.0.git-py34_0
    BUILD END: d2to1-0.2.12.git-py34_0
BUILD START: stsci.tools-0.2.12.git-py34_0
    BUILD START: stsci.distutils-0.0.0.git-py34_1
    BUILD END: stsci.distutils-0.0.0.git-py34_1
BUILD START: stsci.tools-0.0.0.git-py34_157
    BUILD START: pyfits-0.0.0.git-py34_0
        BUILD START: cfitsio-3.370-1
        BUILD END: cfitsio-3.370-1
    BUILD START: pyfits-0.0.0.git-py34_0
    BUILD END: pyfits-v3.3.0.git-py34_8
BUILD START: stsci.tools-v3.3.0.git-py34_8
BUILD END: stsci.tools-0.0.0.git-py34_785
BUILD START: stsci.image-0.0.0.git-py34_785
    BUILD START: stsci.convolve-0.0.0.git-py34_0
    BUILD END: stsci.convolve-0.0.0.git-py34_37
BUILD START: stsci.image-0.0.0.git-py34_37
BUILD END: stsci.image-0.0.0.git-py34_45
```

Let's look at the resultant repository structure. As you can see, the timestamps correlate with the build order:

```
$ ls -ltr ~/anaconda3/conda-bld/linux-64/
total 6260
-rw-rw-r-- 1 example example   38657 Oct  6 17:23 d2to1-0.2.12.git-py34_0.tar.bz2
-rw-rw-r-- 1 example example   42052 Oct  6 17:23 stsci.distutils-0.0.0.git-py34_1.tar.bz2
-rw-rw-r-- 1 example example 3630988 Oct  6 17:24 cfitsio-3.370-1.tar.bz2
-rw-rw-r-- 1 example example 2126961 Oct  6 17:24 pyfits-v3.3.0.git-py34_8.tar.bz2
-rw-rw-r-- 1 example example  419752 Oct  6 17:25 stsci.tools-0.0.0.git-py34_785.tar.bz2
-rw-rw-r-- 1 example example   75614 Oct  6 17:25 stsci.convolve-0.0.0.git-py34_37.tar.bz2
-rw-rw-r-- 1 example example   35301 Oct  6 17:25 stsci.image-0.0.0.git-py34_45.tar.bz2
-rw-rw-r-- 1 example example     719 Oct  6 17:25 repodata.json.bz2
-rw-rw-r-- 1 example example    2908 Oct  6 17:25 repodata.json
```


## Method 2 - Inner Scope

An inner scope build relies on the contents of Conda meta-packages, rather than individual recipes (per se).

Assume the manifest, `inner.lst`, contains the following entry:

```
stsci
```

So where do the packages come from? What's with the magic? Well it's easier to show you than it is to explain. Below is a dump of the `requirements` section of the `stsci` meta-package:

[Keep in mind -- This was lifted from a *test* meta-package, and does not likely reflect the current state of affairs.]

```
[requirements]
build :
    ${requirements:run}
run :
    #STScI
    acstools [py34]
    acstools [py27]
    asdf-standard [py34]
    asdf-standard [py27]
    astrolib.coords [py34]
    astrolib.coords [py27]
    astropy [py34]
    astropy [py27]
    astropy-helpers [py34]
    astropy-helpers [py27]
    calcos [py34]
    calcos [py27]
    cfitsio
    d2to1 [py34]
    d2to1 [py27]
    #drizzle [py34]
    drizzle [py27]
    fftw
    fitsblender [py34]
    fitsblender [py27]
    hstcal [py34]
    hstcal [py27]
    htc_utils [py34]
    htc_utils [py27]
    imexam [py34]
    imexam [py27]
    nictools [py34]
    nictools [py27]
    #photutils [py34]
    photutils [py27]
    poppy [py34]
    poppy [py27]
    purge_path [py34]
    purge_path [py27]
    pyasdf [py34]
    pyasdf [py27]
    pydrizzle [py34]
    pydrizzle [py27]
    pyfftw [py34]
    pyfftw [py27]
    pyfits [py34]
    pyfits [py27]
    #pyqtgraph #issues with building
    #pysynphot [py34]
    pysynphot [py27]
    pywcs [py34]
    pywcs [py27]
    #reftools [py34]
    reftools [py27]
    stistools [py34]
    stistools [py27]
    stsci.convolve [py34]
    stsci.convolve [py27]
    stsci.distutils [py34]
    stsci.distutils [py27]
    stsci.image [py34]
    stsci.image [py27]
    stsci.imagemanip [py34]
    stsci.imagemanip [py27]
    stsci.imagestats [py34]
    stsci.imagestats [py27]
    stsci.ndimage [py34]
    stsci.ndimage [py27]
    stsci.sphinxext [py34]
    stsci.sphinxext [py27]
    stsci.stimage [py34]
    stsci.stimage [py27]
    stsci.tools [py34]
    stsci.tools [py27]
    stwcs [py34]
    stwcs [py27]

    webbpsf [py34]
    webbpsf [py27]
    wfpc2tools [py34]
    wfpc2tools [py27]
    wfc3tools [py34]
    wfc3tools [py27]


    #3rd-party
    atlas-generic [osx]
    sextractor-generic [osx]
    sextractor [linux]
    ds9

    #Standard
    anaconda [py34]
    anaconda [py27]
    numpy [py34]
    numpy [py27]
    python [py34]
    python [py27]
```

Aside from a giant wall of text, you may notice a few key things here. Each package is duplicated, one per line, with its own Python version requirements. In addition to this, some packages are marked `[osx]` while others are marked `[linux]`. Why? Because some packages require a little tender loving care make them work. For example, the `atlas` package is not provided by Anaconda under OSX, but it is available under Linux. That's... unfortunate.

OSX is a special case, as usual, and so is Windows for that matter. Many recipes rely on `openblas` or Apple's built-in `Accelerate` framework to take advantage of "blazing fast linear algebra" operations, so in general, ATLAS is not required. However, some packages absolutely require ATLAS to be installed regardless which operating system you are running. `sextractor` is one such package.

By suffixing the `atlas-generic` recipe with `[osx]`, we effectively tell Conda: *"Only build this package under OSX."*

By suffixing `sextractor-generic` with `[osx]`, we effectively tell Conda: *"Only build this package under OSX"*

See a trend here? Good. Also note that for obvious reasons, `sextractor-generic` depends on `atlas-generic` in the `requirements` section of its own recipe.

The same is true for the `[py27]` and `[py34]` markers. If a recipe is not compatible with Python 3 this convention makes it easy to tell Conda: *"We don't support Python 3, sorry. Only build this package for Python 2.7."*

```
my_cool_package [py27]
another_cool_package [py34]
```

This does exactly what it says it will. `my_cool_package` will only be built when Python 2.7 is the controlling interpreter during compilation (i.e. `--python [PYTHON VERSION]`), while `another_cool_package` is built if we're using Python 3.4. Confusing, yes, but its still a neat and very useful all the same.


#Miscellaneous Utilities

## cbc_remote_purge

The most destructive command in the CBC library. **Use with extreme caution.** `cbc_remote_purge` recursively removes all packages, including previous package revisions, in the currently-loaded anaconda.org remote repository. That means you will absolutely destroy the contents of your anaconda.org account, so I cannot stress this enough:

**DO NOT RUN THIS COMMAND UNLESS YOU ARE ABSOLUTELY CONVINCED YOU NEED TO!**

This script probably has no effect if you are not already logged into anaconda.org at the time, but don't take chances.

## cbc_repo_copy

A simple `rsync` wrapper to copy a local Conda repository elsewhere (e.g. a remote server). To prevent accidental destruction (or directory cluttering) you will need to change the current working directory to the remote filesystem first, then execute `cbc_repo_copy`

```bash
cd /remote/webserver/docroot/some/place
cbc_repo_copy
#[rsync operation happens here]
```

If you do not have this capability, there's still hope, just search the internet for `sshfs` with your favorite search engine.

## cbc_repo_clean

Removes the contents of the **local** Conda package repository (i.e. `[...]/conda-bld/{os}-{arch}/`). It is recommended to perform this as a housekeeping task, especially before creating a "frozen" (or static) monolithic build.


## cbc_recipe

Generates a cbc recipe file based on user-input. This is helpful for when generating trees of packages on the fly from an external script. This script may need to become more feature-rich before that's reality, however.

```
usage: cbc_recipe [-h] [--style STYLE] [--name NAME] [--version VERSION]
                  [--build-number BUILD_NUMBER] [--license LICENSE]
                  [--homepage HOMEPAGE] [--d2to1-hack] [--use-git]
                  [--meta-package]
                  recipe
```

## cbc_server

**DEPRECATED**

This is a simple http file server. It was originally designed for use with cbc recipes for performing "off the grid" builds. You can still use it as such, because it still works, however, I'm not going to document it. I don't recommend using it anymore in lieu of `git_url` or remote `url` calls.

Take a gander in the source code if you are feeling especially adventurous.
