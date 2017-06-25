

# Annotation file containing manually generated annotations for input image set.
OPENCV_BIN=~/code/opencv/install-tree/bin
RAW_IMAGE_DIR=/home/sagarm/code/googliser/person_with_open_mouth
ANNOTATION_FILE=./open-mouth.annotations
VEC_FILE=./open-mouth.vec

function annotate {
  $OPENCV_BIN/opencv_createsamples -info "${ANNOTATION_FILE}" \
    -w 24 -h 24 -num 1000 -show -vec "${VEC_FILE}"
  $OPENCV_BIN/opencv_annotation \
    --annotations="${ANNOTATION_FILE}" \
    --images="${RAW_IMAGE_DIR}"
}

function generate-vec {
  $OPENCV_BIN/opencv_createsamples -info "${ANNOTATION_FILE}" \
    -w 24 -h 24 -num 1000 -show -vec "${VEC_FILE}"
}

for cmd in "$@"; do
  $cmd
done
