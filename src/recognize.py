#!/usr/bin/python3
# USAGE
# python detect_faces_video.py --prototxt deploy.prototxt.txt --model
# res10_300x300_ssd_iter_140000.caffemodel

# import the necessary packages
import argparse
import logging as log
from datetime import datetime
from pathlib import Path

import cv2
from tqdm import tqdm


font = cv2.FONT_HERSHEY_SIMPLEX
PADDING = 0
DEFAULT_CAFFE_PROTO = '../trained_model/deploy.prototxt.txt'
DEFAULT_CAFFE_MODEL = ('../trained_model/res10_300x300_ssd_iter'
                       '_140000.caffemodel')
NUM_JITTERS = 5
TOLERANCE = 0.7


def write(image, write_dir, episode, index):
    write_dir = Path(write_dir / episode)
    if not write_dir.exists():
        write_dir.mkdir()
    frame_name = "{0}.jpg".format(index)
    cv2.imwrite(str(write_dir / frame_name), image)


def main(args):
    """ main """
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read('../trained_model/trainer.yml')
    names = ['Ashley', 'Laura', 'Liam', 'Marisha',
             'Matthew', 'Sam', 'Talisien', 'Travis']

    jpg_files = [str(p)
                 for p in Path(args.in_dir).glob(f'**/*{args.pattern}*/*.jpg')]

    for jpg_file in tqdm(jpg_files, total=len(jpg_files), unit="images"):
        log.debug('Processing image %s', jpg_file)
        jpg_file_path = Path(jpg_file)
        frame_name = jpg_file_path.name
        log.debug(frame_name)
        face_name = jpg_file_path.stem
        log.debug(face_name)

        # read img
        try:
            image = cv2.imread(jpg_file)
        except BaseException:
            log.warning('Failed to open: %s', jpg_file)
            continue

        h, w = image.shape[:2]

        startY = 0
        endY = h - 1
        startX = 0
        endX = w - 1
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        name_index, confidence = recognizer.predict(
            gray[startY:endY, startX:endX])
        # If confidence is less them 100 ==> "0" : perfect match
        if confidence < 80:
            confidence = "{0}%".format(round(100 - confidence))
            name_index = names[name_index]
        else:
            name_index = "unknown"
            confidence = "{0}%".format(round(100 - confidence))

        # probability
        text = f"{name_index}-{confidence}"
        # y = startY - 10 if startY - 10 > 10 else startY + 10
        # cv2.rectangle(image, (startX, startY), (endX, endY),
        #               (0, 0, 255), 2)
        # cv2.putText(image, text, (startX, y),
        #             cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)

        # show the output image
        if name_index != "unknown":
            if args.verbose:
                cv2.imshow(text, image)
                key = cv2.waitKey(0) & 0xFF
                # Add face to ds unless 's' to skip
                if key == ord("s"):
                    continue
                if key == ord("q"):
                    cv2.destroyAllWindows()
                    return 0
                cv2.destroyAllWindows()
            write(image, Path(args.out_dir), name_index,
                  f'{confidence}_{datetime.now()}')
    return 0


# construct the argument parse and parse the arguments
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', dest="verbose", action='store_true')
    parser.add_argument('-t', '--tolerance', dest="tolerance", type=float,
                        default=0.6)
    parser.add_argument('-fp', '--pattern', dest="pattern", default='')
    parser.add_argument("-o", "--out", dest='out_dir', default="../ds_new",
                        help="path save recognized images")
    parser.add_argument('-i', '--i', dest='in_dir', default='../faces/',
                        help='input dir')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    ARGS = parse_args()
    if ARGS.verbose:
        log.basicConfig(format="%(levelname)s: %(message)s", level=log.DEBUG)
        print("Verbose output.")
    else:
        log.basicConfig(format="%(levelname)s: %(message)s")

    TOLERANCE = ARGS.tolerance

    # Create out_dir
    out_dir = Path(ARGS.out_dir)
    if not out_dir.exists():
        out_dir.mkdir()

    exit_code = main(ARGS)

    # Exit
    exit(exit_code)
