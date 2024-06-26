- [Introduction](#introduction)
  - [Background knowledge](#background-knowledge)
    - [Array processing](#array-processing)
      - [Steering vector](#steering-vector)
      - [Steering matrix](#steering-matrix)
- [Configuration File](#configuration-file)
- [Realtime DSP](#realtime-dsp)
  - [Stage](#stage)
    - [Properties](#properties)
    - [methods](#methods)
  - [Message](#message)
    - [Properties](#properties-1)
  - [FunctionStage - Stage](#functionstage---stage)
    - [Properties](#properties-2)
  - [Bus - Stage](#bus---stage)
    - [Properties](#properties-3)
  - [Concatinator - Stage](#concatinator---stage)
    - [Properties](#properties-4)
  - [ChannelPicker - Stage](#channelpicker---stage)
    - [Properties](#properties-5)
  - [Accumulator - Stage](#accumulator---stage)
    - [Properties](#properties-6)
  - [ToDisk - Stage](#todisk---stage)
    - [Properties](#properties-7)
  - [FromDisk - Stage](#fromdisk---stage)
  - [Tap - Stage](#tap---stage)
    - [Properties](#properties-8)
    - [Methods](#methods-1)
  - [print\_audio\_devices - Function](#print_audio_devices---function)
  - [AudioRecorder - Stage](#audiorecorder---stage)
    - [Properties](#properties-9)
    - [Methods](#methods-2)
  - [AudioSimulator - Stage](#audiosimulator---stage)
    - [Properties](#properties-10)
  - [Filter - Stage](#filter---stage)
    - [Properties](#properties-11)
    - [Methods](#methods-3)
  - [ButterFilter - Filter](#butterfilter---filter)
    - [Properties](#properties-12)
  - [FirwinFilter - Filter](#firwinfilter---filter)
    - [Properties](#properties-13)
  - [FirlsFilter - Filter](#firlsfilter---filter)
    - [Properties](#properties-14)
  - [HanningWindow - Stage](#hanningwindow---stage)
  - [FFT - Stage](#fft---stage)
    - [Properties](#properties-15)
    - [Note](#note)
  - [DOAEstimator - Stage](#doaestimator---stage)
    - [Properties](#properties-16)
  - [LinePlotter - Stage](#lineplotter---stage)
    - [Properties](#properties-17)
    - [Methods](#methods-4)
  - [PolarPlotter - Stage](#polarplotter---stage)
    - [Properties](#properties-18)
  - [HeatmapPlotter - Stage](#heatmapplotter---stage)
  - [AudioPlayback - Stage](#audioplayback---stage)
    - [Properties](#properties-19)
      - [Properties](#properties-20)
- [Direction of Arrival](#Direction-of-Arrival)
  - [spherical\_to\_cartesian - function](#spherical_to_cartesian---function)
  - [cartesian\_to\_spherical - function](#cartesian_to_spherical---function)
  - [Element](#element)
    - [Properties](#properties-21)
      - [Calculated properties](#calculated-properties)
  - [WaveVector](#wavevector)
    - [Properties](#properties-22)
      - [Calculated properties](#calculated-properties-1)
  - [Structure](#structure)
    - [Properties](#properties-23)
    - [Calculated properties](#calculated-properties-2)
    - [Methods](#methods-5)
    - [Calculated properties](#calculated-properties-3)
  - [Estimator](#estimator)
    - [Properties](#properties-24)
    - [Methods](#methods-6)
  - [DelaySumBeamformer - Estimator](#delaysumbeamformer---estimator)
  - [BartlettBeamformer - Estimator](#bartlettbeamformer---estimator)
  - [MVDRBeamformer - Estimator](#mvdrbeamformer---estimator)
  - [Music - Estimator](#music---estimator)
    - [Properties](#properties-25)
  - [hz\_to\_cm - function](#hz_to_cm---function)
    - [Parameters](#parameters)
    - [Returns](#returns)
- [Visual](#visual)
  - [Camera](#camera)
    - [Properties](#properties-26)
    - [Methods](#methods-7)
- [Example](#example)


# Introduction
This project creates real-time pipelines to record, simulate, process, and plot signal data. The following are key features and highlights:
- Real-time processing
- Pipelines
- Multiprocessing
- Recording signals
- Simulating signals
- Filtering signals
- Direction of arrival (DOA) algorithms
- Real-time plotters

## Background knowledge
Background knowledge in order to understand the project

### Array processing
[Array processing](https://en.wikipedia.org/wiki/Array_processing) is a wide area of research in the field of signal processing that extends from the simplest form of 1 dimensional line arrays to 2 and 3-dimensional array geometries. Array processing is the backbone for DoA estimation.

#### Steering vector
Steering vectors are vectors which describe how a signal changes as elements receive the signal at different times. This happens as the same signal is delayed at different elements at different positions. Steering matrices the position of each element, and the original wavevector(s) of the source(s).

![Graphic of a steering matrix](https://ars.els-cdn.com/content/image/3-s2.0-B978012398499900008X-f08-03-9780123984999.jpg)
#### Steering matrix
A steering matrix is composed of several steering vectors at several different angles. Each row on the matrix describes a different steering vector at a different angle. These matrices are used in DoA estimation algorithms.

# Configuration File
Hold configuration info for the AccCam library, primarily flags.
- __USE_CUPY__ - bool: If true, replace numpy and scipy with cupy. Highly recommended when possible as it offers drastic performance improvements. When true, the project can be up to x20 faster. Cupy must be installed. Follow installation instructions [here](https://docs.cupy.dev/en/stable/install.html).

# Realtime DSP

## Stage
To archive real-time processing, pipelines can be created using **stages**. **Stages** have a list of **ports** (queues of data), a list of **destinations** (ports of another stage), and a **process**. Each stage is responsible for getting data from the ports, processing the data, and pushing the processed data to destinations. Destinations are ports of another stage.
Stages also introduce multiprocessing. Each stage is ran by its own processes, letting the project leverage the whole CPU.
To use a stage, one must create a subclass which inherits the stage class. The new subclass will create the correct amount of input ports , the length of the input ports (default is 4), and destinations.

### Properties
- num_ports - int: The number of ports. i.e., the number of sources of data the stage requires.
- port_size - int: Ports are essentially queues inherited from multiprocessing. This is the length of the queue.
- destinations - multiprocessing.queue: Default to none. A list of ports from another stage. Recall that ports are multiprocessing queues of a stage.
- has_process - bool: Default is true. Set to false if the stage does not require a process. For example, when using matplotlib for plotting, matplotlib runs its own thread to update plots, thus a process is not needed.

### methods
- run(self): To be implemented by a subclass. Runs forever in a while true loop. This is the code that the subclass customizes to it own purpose.
- start(self): Starts the stage. Run whenever you are ready to begin the process.
- stop(self): Stops the stage.
- link_to_destination(self): Adds a new destination to the stage. This is easier to read than providing all destinations at once when creating the object.
- port_get(self): Gets data from all ports. Always use this than accessing individual queues/ports. If a single port is used, add [0] to the end of the call to get the data. This is a blocking operation.
- port_put(self, data): Puts data to all destinations.

## Message
Messages are used to send data between stages. They are similar in thinking of emails between people. Messages have a main payload and metadata about the payload.

### Properties
- payload - any: The main content of the message.
- timestamp - datetime.time: The time the message was created. This is also automatically set.
- kwargs: Pass any other key word arguments as metadata if wanted. For example: source, size, state, etc.

## FunctionStage - Stage
Pass a function to this class to create a stage which runs the function on input data. This is simpler than creating subclasses for Stage, but is limited in functionality. For example, use this if you would like to call np.ravel() on data, or something just as simple.

It is okay to use this over creating a subclass when:
- The function will ever only be used once. If it is to be reused in the future, make a subclass of Stage.
- The function is simple and does not require any parameters to function. 

The function passed must meet the following requirements:
- Can only have one parameter. The parameter must expect a singular payload (typically has the type of numpy.ndarray)
- Must return a single value. This value will be wrapped into a message and pushed to destinations.
- The function must be pickleable. For example, the function cannot be a lambda function.
  - In order for the function to be pickleable, the function must be declared at the module level. For example, the function cannot be declared inside another function (main()).
An example using FunctionStage is below:
```python
import AccCam.realtime_dsp as dsp
import numpy as np

def fft_function(x):
    return np.abs(np.fft.fft(x, axis=0)) ** 2

def main():
    ...
    fft = dsp.FunctionStage(fft_function)
    ...
    
if __name__ == '__main__':
    main()

```
### Properties
- function - function: The function of which to run on incoming data.

## Bus - Stage
Buses are a stage which take several import ports, merges them into a tuple, and pushes to destinations. Useful for passing several stages to a single stage. It is preferred to have stages with several input ports, but this is an alternative if needed.

### Properties
- num_ports - int: The number of ports to merge.
- port_size - int: The size of the ports.
- destinations - multiprocessing.queue: The destinations of the bus.

## Concatinator - Stage
Concatinators concatenate several signal matrices. For example, if there are several recorders to be merged into one recorder, a concatenator will concatenate the signal matrices together. Same properties and methods as bus.

### Properties
- axis - int: The axis which to concatenate over. Default is 1.

## ChannelPicker - Stage
When given a matrix, return a column of the matrix. Useful for example when you would like to play back a single channel of a signal matrix.

### Properties
- channel - int: The index of the channel to grab.

## Accumulator - Stage
Waits and merges several messages together. For example, wait until ten messages are received, put them together, and continue. Useful for saving data to CSV files for example.

### Properties
- num_messages - int: The number of messages to merge.
- concatenate - int: If given, rather than returning a list of messages, return a numpy array of several payloads (which must be numpy arrays if ture) concatenated together. Give the axis to concatenate to (typically either 0 or 1).

## ToDisk - Stage
Writes every payload it receives to disk. Be careful as this can flood data to a disk quickly. Only use when you actually need to record everything. Use a Tap for intermittent recording. It is recommended to put an Accumulator before this to collect data.

### Properties
- label - str: The label to put in the file-name. Every file name has a label and a timestamp.
- path - str: The folder where to save data. Do not include a / or \ at the end of the string.

## FromDisk - Stage
Takes a file, snips it into blocks, and injects it into a pipeline. Useful for reading back data from ToDisk or Taps. Data must be saved by numpy. The stage automatically stops when the file is fully read.
- path - str: The path to the file to load.
- blocksize - int: The size of the blocks to inject into the pipelines.

## Tap - Stage
A tap into a pipeline. Does nothing to the data, but saves the last message and makes it user-accessible.

### Properties
- num_ports - int: The number of ports of the stage

### Methods
- tap(self): Returns a list of messages. The length of messages matches num_ports.

## print_audio_devices - Function
This function prints all available audio devices to the terminal. Useful for finding the ID of the device you are looking to record data from.

## AudioRecorder - Stage
Manages an audio device and pushes data to destinations.

### Properties
- device_id - int: The ID of the device to record from. Use print_audio_devices to find it.
- samplerate - int: The sample rate of the device.
- num_channels: - int The number of channels of the device. Must match the channels listed from print_audio_devices().
- blocksize - int: The number of samples per block of data.
- channel_map - list: Pass a list to reorganize the channels. For example [2, 3, 1, 0] will swap the channels so that channel 2 is in index 0, 3 to 1, 1 to 2, and 0 to 3.

### Methods
- Start(self): Starts the recorder and begins pushing data.
- Stop(self): Stops the recorder.

## AudioSimulator - Stage
Injects simulated audio into the pipeline. Uses a Structure to simulate audio.

### Properties
- structure - Structure: The structure to take simulations from. Structures represent a set of elements and can simulate their respective data when given wavevectors. More detail is under its own documentation.
- wavevectors - list[WaveVector]: The wavevectors to project onto the structure. More documentation on wavevectors is under its own documentation.
- wait - bool: If true, add a delay to simulate the delay it takes to get a block of audio in real life. Default is True.
- randomize_phase - bool: If true, randomize the phase of elements. All elements will have the same randomized phase. Default is True.

## Filter - Stage
A filter is a [digital filter](https://en.wikipedia.org/wiki/Digital_filter). These filters can either be FIR or IIR filters

### Properties
- b_coefficients - np.array: b coefficients of the filter.
- a_coefficients - np.array: a coefficients of the filter.
- samplerate - int: The sample rate of the incoming data.
- num_channels - int: The number of elements of the incoming data.
- method - str: The method of which to apply the filter.
  - lfilter: [Normal convolusion](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.lfilter.html).
  - filtfilt: [apply the filter forwards, then backwards again](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.filtfilt.html#scipy.signal.filtfilt). This guaranties that the phase of the data is not changed **(this is very important for DoA estimators)**, but squares the response of the filter. This is recommended over lfilter for this reason. Note that this is a non-causal operation, but that is okay since all data is known in the block.
- remove_offset - bool: Sets the DC component of the data to zero if true.
- normalize - bool: Set the maximum value of the signal to one if true.

### Methods
- plot_response(self): Plots the response of the filter. This is a blocking operation.
- plot_coefficients(self): Plots the coefficients of the filter. This is a blocking operation.

## ButterFilter - Filter
A [butterworth filter](https://en.wikipedia.org/wiki/Butterworth_filter).

### Properties
- n - int: The order of the filter.
- cutoff - float: The cutoff frequency of the filter in Hz.
- type - str: The type of filter. can be lowpass, highpass, bandpass, or bandstop. Default is lowpass

## FirwinFilter - Filter
A lowpass [ideal filter](https://en.wikipedia.org/wiki/Sinc_filter) using the window method. This is mathematically better than ButterFilter and is recommended. Can have extremely sharp cutoffs. A subclass of filter, inheriting all properties and methods.

### Properties
- n - int: The order of the filter.
- cutoff - float: The cutoff frequency of the filter in Hz.
- type - str: The type of filter. can be lowpass, highpass, bandpass, or bandstop. Default is lowpass.

## FirlsFilter - Filter
A multi-bandpass filter. Optimized via least-squares error minimization. This offers more control over FirwinFilters at the cost of complexity.

### Properties
Documentation sourced from scipy.
- n - int: The order of the filter. Must be odd
- bands - np.array: A monotonic nondecreasing sequence containing the band edges in Hz. All elements must be non-negative and less than or equal to the Nyquist frequency given by nyq. The bands are specified as frequency pairs, thus, if using a 1D array, its length must be even, e.g., np.array([0, 1, 2, 3, 4, 5]). Alternatively, the bands can be specified as a nx2 sized 2D array, where n is the number of bands, e.g, np.array([[0, 1], [2, 3], [4, 5]]).
- desired - np.array: A sequence the same size as bands containing the desired gain at the start and end point of each band.

## HanningWindow - Stage
Applies a [hanning window](https://en.wikipedia.org/wiki/Hann_function) to incoming data. Simply a **stage** that applies a hanning window. Remember to use this before a fft to remove spectral leakage.

## FFT - Stage
Applies FFT to data. Can return different results of the fft such as complex data, phase, absolute value, and power.

### Properties
- type - str: The type of output of the fft.
  - complex: Return the raw complex output of the fft.
  - phase: Return the phase of the fft.
  - abs: Return the absolute value (magnitude) of the fft.
  - power: return the special power of the fft.
- shift: If true, shift the zero-frequency component to the center of the spectrum. False by default.

### Note
When plotting fft, make sure to provide x_data of the plot to the following to get accurate results:
np.fft.fftfreq(blocksize, 1/samplerate)
This provides the frequency of each index to the plotter.

## DOAEstimator - Stage
Takes a DoA estimator and places it into the pipeline.

### Properties
- estimator - direction_of_arrival.Estimator: The estimator to utilize. See documentation in [Estimator](#estimator)

## LinePlotter - Stage
Plots one line or several lines on a grid. If input data is a vector, plot one line. If a matrix, plot one line per list on axis=0.

### Properties
- title - str: The title of the plot.
- x_label - str: The X label of the plot.
- y_label - str: The Y label of the plot.
- num_points - int: The number of points per line. Should match .shape[0] of incoming data if a matrix of length of the data if a vector.
- num_lines - int: The number of lines to draw. Should match .shape[1] of incoming data if a matrix, or simply one if the data is a vector.
- interval - float: The delay in seconds between frame updates. Should match the period of data arrivals to the port (blocksize / samplerate).
- x_data - np.array: If provided, use this as the x-axis data component. If not provided, it is 0 to num_points.
- x_extent - tuple: If provided, show this range on the x-axis by cropping.
- y_extent - tuple: If provided, show this range on the y-axis by cropping.

### Methods
- show - static: Show the plot. This is a blocking methods. Call it at the end of your script.

## PolarPlotter - Stage
Similar to LienPlotter, but plots (theta, radius) rather than (x, y).

### Properties
- title - str: The title of the plot.
- num_points - int: The number of points per line. Should match .shape[0] of incoming data if a matrix of length of the data if a vector.
- num_lines - int: The number of lines to draw. Should match .shape[1] of incoming data if a matrix, or simply one if the data is a vector.
- interval - float: The delay in seconds between frame updates. Should match the period of data arrivals to the port (blocksize / samplerate).
- theta_data - np.array: If provided, use this as the theta-axis data component. If not provided, it is 0 to 2pi with num_points points.
- theta_extent - tuple: If provided, show this range on the theta-axis by cropping.
- radius_extent - tuple: If provided, show this range on the radius-axis by cropping.

## HeatmapPlotter - Stage
Plots a matrix on a heatmap. Same properties and methods as LinePlotter with the addition of:
- z_extent - tuple: sets the maximum and minimum values for the color map.
- cmap - str: The [color map](https://matplotlib.org/stable/users/explain/colors/colormaps.html) which to use for the heatmap. Default is viridis.

## AudioPlayback - Stage
Play data back out to your speakers. Useful for hearing how filters effect data easily for demonstrative purposes. Expects a matrix to keep consistency.

### Properties
- samplerate - int: The sample rate of the data.
- blocksize - int: The blocksize of the data.
- channel - int: The channel which to play.

#### Properties
- label - str: The label to pass to the file name.
- path - str: The path of where to save the file. Must be a folder with no / or \ at the end of the string.

# Direction of Arrival
Holds elements, wave vectors, steering vectors, and steering matrices. Use to calculate steering vectors for simulators and steering matrices for DoA algorithms.

## spherical_to_cartesian - function
Takes np.array([radius, inclination, azimuth]) and returns np.array([x, y, z]). Can accept a 2d array in the form of [[x1, y1, z1], [x2, y2, z2], ...]. Use this method rather than for loops for performance improvements.

## cartesian_to_spherical - function
Takes np.array([x, y, z]) are returns np.array([radius, inclination, azimuth]). Can also accept 2d arrays like spherical_to_cartesian.

## Element
Represents an element (a microphone or antenna).

### Properties
- position - np.array: A numpy array holding (x, y, z) position. Units are in wavelengths of a theoretical wavevector.
- samplerate - int: The sample rate of the element.

#### Calculated properties
- spherical_position - np.array: A tuple holding (r, inclination, azimuth) position.

## WaveVector
Holds wavevector. Remember to always pass (kx, ky, kz). If you want to pass (wavenumber, inclination, azimuth), which is more common, translate using spherical_to_cartesian inside the declaration.

### Properties
- k - np.array: A numpy array holding (kx, ky, kz).
- power - float: The power of the signal generated from the wavevector. Default is 1
- wavespeed - float: The wave proportion speed of the environment which holds the wavevector. Default is 343, the speed of sound.

#### Calculated properties
- spherical_k - tuple: numpy array holding (wavenumber, inclination, azimuth).
- inclination - float: The inclination angle of the wavevector in radians. Equal to arctan(ky / kx). 
- azimuth - float: The azimuth angle of the wavevector in radians. Equal to arccos(kz / |k|).
- angular_wavenumber - float: The angular wavenumber of the wavevector. Equal to |k|.
- angular_wavelength - float: The angular wavelength of the wavevector. Equal to 1 / angular_wavenumber.
- angular_frequency - float: The angular frequency of the wavevector. Equal to angular_wavenumber * wave_speed.
- angular_period - float: The angular period of the wavevector. Equal to 1 / angular_frequency.
- linear_wavenumber - float: The linear wavenumber of the wavevector. Equal to angular_wavenumber / (2 * pi).
- linear_wavelength - float: The linear wavelength of the wavevector. Equal to angular_wavelength * (2 * pi).
- linear_frequency - float: The linear frequency of the wavevector. Equal to angular_frequency / (2 * pi).
- linear_period - float: The linear period of the wavevector. Equal to angular_period * (2 * pi).

![Graphic of unit conversions](https://upload.wikimedia.org/wikipedia/commons/thumb/9/9e/Commutative_diagram_of_harmonic_wave_properties.svg/450px-Commutative_diagram_of_harmonic_wave_properties.svg.png)

_A diagram representing the relationships between wavenumbers and other properties_


## Structure
Represents an assembly of elements. Takes several elements and provided functionality with the elements.

### Properties
- elements - List[Element]: A list of elements to project a wavevector onto.
- wavenumber - float: The wave number of the incoming signal.
- snr - float: The expected or to be simulated signal-to-noise ratio of the audio waves.
- samplerate - int: The global samplerate of the structure. This is taken from the first element. All elements should have the same samplerate.
- inclination_range - tuple(float): The range of possible inclinations the structure is capable of scanning.
- azimuth_range - tuple(float): The range of possible azimuths the structure is capable of scanning.
- inclination_resolution - int: The number of inclinations to scan for. The higher the number, the more accurate the structure is with the cost of computation time.
- azimuth_resolution - int: The number of azimuths to scan for. Same compromises as inclination_resolution.

### Calculated properties
- inclination_values - np.array: An array of inclinations which it scans for. This can be helpfully for getting axis data for plotters.
- azimuth_values - np.array: An array of azimuths which it scans for. This can be helpfully for getting axis data for plotters.
- steering_matrix - np.array: The steering matrix of the structure. Holds all possible steering vectors when considering its elements, wavenumber, ranges, and resolutions.

### Methods
- steering_vector(self, wavevectors): Get a steering vector for the structure when provided a list of wavevectors. If only one wavevector exists, pass it as a list of one vector.
  - wavevectors - list[WaveVector]: A list of wavevectors which hit the structure.
- simulate_audio(self, wavevectors, random_phase): Simulates ideal audio from the structure
  - wavevectors - list[WaveVector]: A list of wavevectors which hit the structure.
  - random_phase: If true, randomize the phase of elements. All elements will have the same randomized phase. Default is True.
- visualize(self): Shows a 3D scatterplot with element positions. Helps verify that the structure is what the user expects.
- steering_vector(self, wavevector): Calculates a steering vector when given a wavevector. Returns a steering vector which correlates to the structure.
  - wavevector - WaveVector: A wave vector to project onto elements.

### Calculated properties
- steering_matrix - np.array: The steering matrix accosted with the structure. Dependent on elements, azimuth and inclination ranges and resolutions. Heavily used in DoA algorithms and the core of this module.

## Estimator
A base class for all estimators. Do not use directly as this is an abstract base class.

### Properties
- steering_matrix - SteeringMatrix: The main steering matrix to use in the algorithm. All subclasses have a steering matrix.

### Methods
- process(self, data): Runs the algorithm on incoming data. Reservation for subclasses. Raises a NotImplementedError by default.

## DelaySumBeamformer - Estimator
A classical beamformer. The easiest to understand and use. However, this is expensive to use and gives sub-par results, thus it is not recommended for this program. Only needs steering_matrix property.

## BartlettBeamformer - Estimator
A beamformer much more efficient than DelaySumBeamformer. Gives similar results to DelaySUmBeamformer. Only needs steering_matrix property.

## MVDRBeamformer - Estimator
A very accurate beamformer while being more computationally expensive. Gives, in general, good results. Only needs steering_matrix

## Music - Estimator
The most accurate and most computationally expensive algorithm. Gives extremely accurate results when in an optimal environment.

### Properties
- num_sources: The number of sources in the environment.

## hz_to_cm - function
Calculates ideal spacing between uniform element spacing arrays. Useful for setting up a structure in real life.

### Parameters
- linear_frequency - float: Hz of the wave you would like to measure.
- wave_speed - float: The speed of the wave in the environment in meters per second. Sound waves are 343 meters per second.

### Returns
Distance between each element in cm if this is a uniform structure.

# Visual
Hold classes to manage visual aspects of this project, such as cameras

## Camera
This class manages a camera. It can get a picture from the camera, calibrate the image, and create calibration profiles for the camera.

### Properties
- output_resolution - tuple: The size of the image to return when calling read().
- inclination_fov - tuple: The field of view (fov) on the inclination axis in the form of (min angle, max angle).
- azimuth_fov - tuple: The fov on the azimuth axis in the form of (min angle, max angle).
- video_source - int or str: The source of the video stream. Default is 0. Can be either an id (int) or an url (str).

### Methods


- open(self): Opens the camera feed. Automatically ran during object initialization. Run if you release the camera and want to open it again.
- release(self): Releases the camera feed. Run at the end of the script, if it has an end (similar to Stage).
- read(self): Returns an image from the camera. If a calibration profile is present, it will pass the image though the calibration, then return it. Otherwise, it will change the resolution to the output resolution of the instance.
- calibrate(self, checkerboard_size): Calibrates the camera and creates a calibration profile. Requires images to be present in calibration_images. The images must be images of a checkerboard. It will display the points on the checkerboard for user verification, then create a calibration profile. The profile is automaticly applied to the instace.
  - checkerboard_size - tuple: The number of rows and columns of the checkerboard provided as (row, cols).
- save_calibration(self, path): Saves the current calibration to a python pickle file for later instances of the same camera.
  - path - str: The path to save the calibration to.  File should have extension .pickle.
- load_calibration(self, path):Loads a previous calibration of the same camera to the current instance. The previous calibration must be saved by save_calibration
  - path: The path to load the calibration from. File should have extension .pickle.

# Example

```python
from AccCam.__config__ import __USE_CUPY__

if __USE_CUPY__:
    import cupy as np
else:
    import numpy as np

import AccCam.realtime_dsp as dsp
import AccCam.direction_of_arrival as doa


def main():

    # Variables
    samplerate = 44100
    blocksize = 44100
    wavenumber = 12.3

    # Sphere
    elements = [doa.Element(np.array([-1.25, 0, 0]), samplerate),
                doa.Element(np.array([-0.75, 0, 0]), samplerate),
                doa.Element(np.array([-0.25, 0, 0]), samplerate),
                doa.Element(np.array([0.25, 0, 0]), samplerate),
                doa.Element(np.array([0.75, 0, 0]), samplerate),
                doa.Element(np.array([1.25, 0, 0]), samplerate),
                doa.Element(np.array([0, -1.25, 0]), samplerate),
                doa.Element(np.array([0, -0.75, 0]), samplerate),
                doa.Element(np.array([0, -0.25, 0]), samplerate),
                doa.Element(np.array([0, 0.25, 0]), samplerate),
                doa.Element(np.array([0, 0.75, 0]), samplerate),
                doa.Element(np.array([0, 1.25, 0]), samplerate)]

    structure = doa.Structure(
        elements=elements,
        wavenumber=wavenumber,
        snr=50,
        blocksize=blocksize,
    )
    #structure.visualize()

    wavevectors = [
        doa.WaveVector(doa.spherical_to_cartesian(np.array([wavenumber * 0.98, 1, 1]))),
        doa.WaveVector(doa.spherical_to_cartesian(np.array([wavenumber * 1.02, 2, 2]))),
    ]

    # Get hz for debugging
    for wavevector in wavevectors:
        print(wavevector.linear_frequency)

    # Recorder to get data
    recorder = dsp.AudioSimulator(
        structure=structure,
        wavevectors=wavevectors,
        wait=False
    )

    # Filter
    filt = dsp.FirwinFilter(
        n=1001,
        num_channels=len(elements),
        cutoff=np.array([400, 800]),
        type='bandpass',
        samplerate=samplerate,
        method='filtfilt',
        normalize=True,
        remove_offset=True
    )
    #filt.plot_response()
    #filt.plot_coefficients()

    # MUSIC
    estimator = doa.MVDRBeamformer(structure)

    music = dsp.DOAEstimator(estimator)

    # Plot
    plot = dsp.HeatmapPlotter(
        title='MUSIC',
        x_label="inclination",
        y_label="azimuth",
        x_data=structure.inclination_values,
        y_data=structure.azimuth_values,
        interval=0,
        cmap='inferno'
    )

    # Linking
    recorder.link_to_destination(filt, 0)
    filt.link_to_destination(music, 0)
    music.link_to_destination(plot, 0)

    # Start processes
    recorder.start()
    filt.start()
    music.start()
    plot.start()
    plot.show()


if __name__ == '__main__':
    main()

```
