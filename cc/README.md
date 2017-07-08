Requires opencv built with in a specific location -- edit CMakeLists.txt with
the absolute path.

```bash
sudo apt install \
  cmake git \
  build-essential pkg-config \
  qt4-default libgtk2.0-dev \
  libavcodec-dev libavformat-dev libswscale-dev \
  python-dev python-numpy \
  libtbb2 libtbb-dev \
  libjpeg-dev libpng-dev libtiff-dev libjasper-dev libdc1394-22-dev
git clone https://github.com/opencv/opencv.git
cd opencv
mkdir build
cd build
cmake -D CMAKE_BUILD_TYPE=RELEASE \
  -D CMAKE_INSTALL_PREFIX=/home/sagarm/code/opencv/install-tree \
  -D WITH_TBB=ON -D BUILD_NEW_PYTHON_SUPPORT=ON -D WITH_V4L=ON \
  -D INSTALL_C_EXAMPLES=ON  -D INSTALL_PYTHON_EXAMPLES=ON -D BUILD_EXAMPLES=ON \
  -D WITH_QT=ON -D WITH_OPENGL=ON -D ENABLE_FAST_MATH=1 \
  -D WITH_CUDA=ON -D CUDA_FAST_MATH=1 -D WITH_CUBLAS=1 ..
make
make install
```

Then build here with
```
cmake .  # In-source build.
make
```
