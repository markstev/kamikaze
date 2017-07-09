arduino-cmake is a symlink to a checkout of
`https://github.com/queezythegreat/arduino-cmake.git`
Not copied over due to size.

## Instructions
Make sure you run

```
git submodule init # from the parent directory
git submodule update
mkdir arduino/build
cd arduino/build
cmake ..
make  # build
make upload  # upload
```

You may need to change the TTY listed in CMakeLists.txt.

