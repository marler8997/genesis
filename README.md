# Genesis

Writen in python for now. It's quick and easy to prototype in python.

# TODO

* for packages that need to be installed to their final location, use a "mark file" to mark when they are complete.  That way if the power goes out during the build/install, then the mark file still won't be there.
* variation sets should have reasonable defaults, i.e. version should default to latest, platform should default to host, etc
* figure out how to declare package interfaces
   - currently, can't build tcc-bootstrap2 because it is expecting gcc.
     I can pass in different C compilers but I need a way to access data about those C compiler.
     For example, what is the name of the compiler executable?
     For gcc it will be 'gcc' and for tcc it will be 'tcc'.
     Whatever solution, I think this information will need to be in the object files, rather than the final built package.  This is because that the packages that use package interfaces will need to know the interface information while they are building their own objects. So I think the object definition will need to be expanded, not just to include ins and outs, but also information about how to use it and what it provides.
* fix build ops to only accept known properties
* sandbox the 'run' operations so they don't have access to the host tools.  for now just modify the environment variables.
* add lock files
* get C compilers going

# Genesis Objects

The building-block of genesis are genesis objects that generate packages.  Each object is stored in its own file with a "hash-name" and contains a set of inputs and operations to generate the package, i.e.

```
{
  "in":[
    "<hash>-<name>",
    "<hash>-<name>",
    "<hash>-<name>",
    ...
  ],
  "ops":[
    {"run":["<program>", "<arg1>", "<arg2>", ...], ...}
    ...
  ]
}
```

# Operations

* take a genesis object, print all the data that is included in the genesis object hash
* calculate the "genesis hash" of a file/directory


# `/g` directory structure

```
# packages
/g/<hash>-<name>

# package stage dir (where packages are built)
/g/stage

# content-addressable files
/g/ca/<hash>-name>
# stage directory for content-addressable files.  Used to temporarily build resource intended
# for /g/ca while downloading/extracting them.
/g/ca/stage

# genesis object files
/g/o
# a stage directory for object files
/g/o/stage

# proxy files (i.e. the autoconf script for windows)
/g/proxy
```

# Package config

Package genesis objects can contain a global `config` property which is a map of configuration. This would contain inormation that affects how genesis builds the package, but should be the last resort.  If something can be configured via an operation, it should go there.

#### Current properties:
```
bool notmpout    True if the package needs to be in it's finalout directory.
```

# Package metadata

Each package may contain a directory named `genesis` that contains metadata about the package.

```
# contains executable programs
bin
# a file with all the dependencies
genesis/deps
# a file with extra binaries that aren't in bin
genesis/extra-bin
```

## The `genesis/extra-bin` file

One use case for the `extra-bin` directory is the windows python install.  In that case, we only want to install `python.exe`, however, it looks for libraries in the same directory that it lives, but we don't want to put all those files in the `bin` directory.  So, we leave it in the root path of the package, and just add the exe to the `extra-bin` file so we only get that one tool.

## The `deps` file

```
# an absolute path means the package depends on the given package being present and being at that absolute path, i.e.
/g/7gx4kiv5m0i7d7qkixq2cwzbr10lvxwc-glibc-2.27

# a relative path means the package is depending on another package but the path is relative
../7gx4kiv5m0i7d7qkixq2cwzbr10lvxwc-glibc-2.27

# TODO: come up with other kinds of dependencies
# maybe $PATH/7gx4kiv5m0i7d7qkixq2cwzbr10lvxwc-glibc-2.27/bin meaning that the given path needs to be in PATH?
```

# `bootstrap` packages

If a package name ends with `-bootstrap`, then it indicates that the package is built with the host environment. This means the resulting object can vary quite a bit depending on the host system so it should not be used in normal genesis objects.

# Package Naming Conventions

```
<name>-<version>[-cross-<platform]-<platform>[-prebuilt][-bootstrap]

# name = foo
# platform = linux64
foo-linux64

# name = foo
# platform = linux64
# type = prebuilt (prebuilt binaries)
foo-linux64-prebuilt

# name = foo
# platform = linux64
# type = prebuilt (built using host tools)
foo-linux64-bootstrap
```

# Package Interfaces

In order to use different packages for the same feature (i.e different versions of compilers/libraries) I'd like to have some concept of package interfaces.  A way for a package to declare that it supports some sort of interface.

I could create an interface definition format, but for now I'm going to do something simple.  I'm just going to say that each interface is defined as a name and that implementing an interface means that you will provide a file in your package called `genesis/i/<interface-name>`.  So if you're a c-compiler, you could implement the 'c-compiler' interface by providing 'genesis/i/c-compiler` in your package.  You declare which interfaces in your configuration with:
```
{
  "config":{
    "ifaces":["c-compiler", ...],
  },
  ...
}
```
By declaring which interfaces a package supports, genesis can verify that the interface files are generated when building the package.

Another idea is to provide a way for an object to require certain in packages provide certain interfaces.  I haven't designed this one yet.