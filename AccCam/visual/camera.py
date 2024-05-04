from AccCam.__config__ import __USE_CUPY__

if __USE_CUPY__:
    import cupy as np
else:
    import numpy as np

import logging
import pickle
import glob
import cv2 as cv

logger = logging.getLogger(__name__)


class Camera:
    """
    Hold camera data. Can give frames with calibration, resizing, and other modifications
    """
    def __init__(self,
                 output_resolution: tuple,
                 inclination_fov: tuple,
                 azimuth_fov: tuple,
                 video_source=0
                 ):
        """
        :param output_resolution: The output resolution of the camera with (min, max) angles
        :param inclination_fov: The fov on the inclination axis with (min, max) angles
        :param azimuth_fov: The fov on the azimuth axis
        :param video_source: The source of the video stream. Default is 0. Can be either an id (int) or an url (str).
        documentation in calibrate()
        """
        self.video_source = video_source
        self.camera = None

        self.camera_resolution = None   # Must take first image to get this
        self.output_resolution = output_resolution
        self.inclination_fov = inclination_fov
        self.azimuth_fov = azimuth_fov

        self.calibration = None

        self.open()

    def open(self):
        """
        Open the camera source.
        :return: None
        """

        if self.camera is None:
            self.camera = cv.VideoCapture(self.video_source)
            return

        if not self.camera.isOpened:
            self.camera.open(self.video_source)
            return

    def release(self):
        """
        Release the camera, effectively stopping the instance of this class.
        :return:
        """
        if self.camera.isOpened:
            self.camera.release()

    def read(self):
        """
        Get a single frame
        :return: A frame taken from the camera
        """
        ret, image = self.camera.read()

        # Make sure camera took a picture
        if not ret:
            logger.warning('could not get image')

        # calibrate
        if self.calibration is not None:
            image = cv.undistort(image, *self.calibration)

        # If no calibration is available, still resize image
        else:
            image = cv.resize(image, self.output_resolution)

        # Return image
        return image

    def calibrate(self, checkerboard_size: tuple):
        """
        Calibrate the camera
        :return: None
        """

        # Get camera resolution if needed
        if self.camera_resolution is None:
            self.read()     # Read finds camera resolution from a test image

        # termination criteria
        criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)

        # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
        objp = np.zeros((checkerboard_size[0] * checkerboard_size[1], 3), np.float32)
        objp[:, :2] = np.mgrid[0:checkerboard_size[1], 0:checkerboard_size[0]].T.reshape(-1, 2)

        # Arrays to store object points and image points from all the images.
        objpoints = []  # 3d point in real world space
        imgpoints = []  # 2d points in image plane.

        images = glob.glob('/calibration_images/*.jpeg')

        for fname in images:
            img = cv.imread(fname)
            gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

            # Find the chess board corners
            ret, corners = cv.findChessboardCorners(gray, checkerboard_size, None)

            # If found, add object points, image points (after refining them)
            if ret:
                objpoints.append(objp)

            corners2 = cv.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
            imgpoints.append(corners2)

            # Draw and display the corners
            cv.drawChessboardCorners(img, checkerboard_size, corners2, ret)
            cv.imshow('img', img)
            cv.waitKey(500)

        cv.destroyAllWindows()

        # Post-processing
        ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
        newcameramtx, roi =(mtx, dist, self.camera_resolution, 1, self.output_resolution)

        # Pack in order to unpack in cv.undistort
        self.calibration = (mtx, dist, None, newcameramtx)

    def save_calibration(self, path):
        """
        Saves a calibration profile to a pickle file
        :param path: The path to save the file to. File should have extension .pickle
        :return: None
        """
        with open(path, 'wb') as output_file:
            pickle.dump(self.calibration, output_file)

    def load_calibration(self, path):
        """
        Loads a calibration profile from a pickle file
        :param path: The path to get the pickle file from. File should have extension .pickle
        :return: None
        """
        with open(path, 'rb') as input_file:
            self.calibration = pickle.load(input_file)
