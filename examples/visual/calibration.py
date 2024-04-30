from AccCam.visual import Camera
import numpy as np


def main():
    cam = Camera((500, 500), (0, 2*np.pi), (0, np.pi))
    cam.calibrate((5, 5))
    cam.save_calibration('test.pickle')


if __name__ == '__main__':
    main()
