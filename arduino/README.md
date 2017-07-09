## Instructions

```
sudo apt install arduino-core
git submodule init # from the parent directory
git submodule update
mkdir arduino/build
cd arduino/build
cmake ..
make  # build
make upload  # upload
```

You may need to change the TTY listed in CMakeLists.txt.

