import argparse
import os

import cv2 as cv
from PIL import Image
from skimage.metrics import structural_similarity as compare_ssim


class ConfigParser:
    def __init__(self):
        self.args = None

        self.parser = argparse.ArgumentParser()

        self.parser.add_argument('-f', '--file',
                                 help='Video file or folder containing video files',
                                 type=str,
                                 required=True)

        self.parser.add_argument('-r', '--rate',
                                 help='Frame rate of the video(s)',
                                 type=int,
                                 required=True)

        self.parser.add_argument('-i', '--interval',
                                 help='Interval between two consecutive frames',
                                 type=int,
                                 required=True)

        self.parser.add_argument('-s', '--start',
                                 help='Index of the start frame',
                                 type=int,
                                 required=True)

        self.parser.add_argument('-c', '--cut',
                                 help='Area of the frame to cut ( x1, y1, x2, y2 )',
                                 type=str,
                                 required=False)

        self.parser.add_argument('-w', '--webcam',
                                 help='Area of the webcam to remove from frames (x1, y1)',
                                 required=False)

        self.file = './input'
        self.rate = 30
        self.interval = 10
        self.start = 0

        self.cut = []
        self.webcam = []

    def parse_args(self):
        self.args = self.parser.parse_args()

        if self.args.file:
            self.file = self.args.file

        if self.args.rate:
            self.rate = self.args.rate

        if self.args.interval:
            self.interval = self.args.interval

        if self.args.start:
            self.start = self.args.start

        if self.args.cut:
            self.cut = [int(x) for x in self.args.cut.split(',')]

        if self.args.webcam:
            self.webcam = [int(x) for x in self.args.webcam.split(',')]

        return {
            'file': self.file,
            'rate': self.rate,
            'interval': self.interval,
            'start': self.start,
            'cut': self.cut,
            'webcam': self.webcam
        }


def generate_pdf(output_path, frames_path, video_name):
    images = []
    files = os.listdir(frames_path)

    files.sort(key=lambda f: int(f.split('.')[0]))

    for file in files:
        images.append(Image.open(f'{frames_path}{file}'))

    cape = images.pop(0)

    cape.save(
        f'{output_path}/{video_name}.pdf',
        'PDF',
        resolution=100.0,
        save_all=True,
        append_images=images
    )


class SlideExtractor:
    def __init__(self, slide_extractor_config):
        self.slide_extractor_config = slide_extractor_config

        self.output_folder = './output/'

        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

        self.diff_th = 1 - .05

    def extract(self):
        # verify if the folder is a file or a folder
        if os.path.isfile(self.slide_extractor_config['file']):
            self._extract_slides(
                self.slide_extractor_config['file'],
                self.slide_extractor_config['file'].split('/')[-1].split('.')[0]
            )
        else:
            self._multiple_extract_slides()

    def _extract_slides(self, video_path, video_name):
        # get the video file path
        output_path = f'{self.output_folder}{video_name}'
        frames_path = f'{output_path}/frames/'

        if not os.path.exists(output_path):
            os.makedirs(output_path)

        if not os.path.exists(frames_path):
            os.makedirs(frames_path)

        capture = cv.VideoCapture(video_path)
        total_frames = int(capture.get(cv.CAP_PROP_FRAME_COUNT))

        start = self.slide_extractor_config['start']
        interval = self.slide_extractor_config['interval'] * self.slide_extractor_config['rate']

        end_frame = total_frames - start
        prev_frame = None

        width = int(capture.get(cv.CAP_PROP_FRAME_WIDTH))
        height = int(capture.get(cv.CAP_PROP_FRAME_HEIGHT))

        cut = len(self.slide_extractor_config['cut']) == 4
        webcam = len(self.slide_extractor_config['webcam']) == 2

        x1, y1, x2, y2 = 0, 0, width, height
        webcam_x1, webcam_y1 = 0, 0
        webcam_x2, webcam_y2 = 0, 0

        if cut:
            x1, y1, x2, y2 = self.slide_extractor_config['cut']

        if webcam:
            webcam_x1, webcam_y1 = self.slide_extractor_config['webcam']
            webcam_x2, webcam_y2 = webcam_x1 + width, webcam_y1 + height

        for i in range(start, end_frame, interval):
            capture.set(cv.CAP_PROP_POS_FRAMES, i)
            ret, frame = capture.read()

            if ret:
                roi = frame[y1:y2, x1:x2]

                if webcam:
                    roi[webcam_y1:webcam_y2, webcam_x1:webcam_x2] = 255

                if prev_frame is None:
                    cv.imwrite(frames_path + str(i) + '.jpg', roi)
                    prev_frame = roi
                else:
                    gray_prev = cv.cvtColor(prev_frame, cv.COLOR_BGR2GRAY)
                    gray_curr = cv.cvtColor(roi, cv.COLOR_BGR2GRAY)

                    score, _ = compare_ssim(gray_prev, gray_curr, full=True)

                    if score < self.diff_th:
                        cv.imwrite(frames_path + str(i) + '.jpg', roi)
                        prev_frame = roi

        generate_pdf(output_path, frames_path, video_name)

    def _multiple_extract_slides(self):
        folder = self.slide_extractor_config['file']

        # get the video files from the folder
        video_files = [f for f in os.listdir(folder)]

        for video in video_files:
            video_name = video.split('.')[0]

            self._extract_slides(
                f'{folder}/{video}',
                video_name
            )

            print(f'\n{video_name}: Extraction finished')

