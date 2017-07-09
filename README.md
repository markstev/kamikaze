
## Setup instructions

To use main.py, run:

```bash
sudo apt install python-opencv python-pip
sudo pip install python-gflags six
```

cc/ and arduino/ have separate setup instructions / READMEs, but unless you are
planning to use the C++ version (no Arduino suport) or flash the Arduino these
are not required.

Recognition will run faster if you build OpenCV as suggested in `cc/README.md`, but it' not required.


## Run

`./main.py --fake --webcam=0 --tty=ttyACM0`

* `--nofake` enables signalling the Arduino. No limits in place yet!
* `--tty` is the name of the tty to use without the /dev/.
* type `q` while the preview window is focused to exit.
* by default, recognition will be done on webcam input. Run recognition on
  images by passing them as command line arguments.
* `--webcam=1`: you may want to use webcam=1 if you have >1 webcam.
* note that `open-mouth.*` and `train.sh` are currently unused.
* `--nopreview`: will disable the preview window, if you want to test
  recognition speed on a corpus of images.  Abort with Ctrl-C.

## To make things move

Pass the `--nofake` flag.
