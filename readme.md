# Indroduction
This project creates real-time pipelines to record, simulate, process, and plot signal data. The following are key features and highlights:
- Real-time processing
- Pipelines
- Multiprocessing
- Hardware acceleration
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

# Realtime DSP

## Stage
To archive real-time processing, pipelines can be created using **stages**. **Stages** have a list of **ports** (queues of data), a list of **destinations** (ports of another stage), and a **process**. Each stage is responsible for getting data from the ports, processing the data, and pushing the processed data to destinations. Destinations are ports of another stage.
Stages also introduce multiprocessing. Each stage is ran by its own processes, letting the project leverage the whole CPU.
To use a stage, one must create a subclass which inherits the stage class. The new subclass will create the correct amount of input ports , the length of the input ports (default is 4), and destinations.

### Properties
- num_ports - int: The number of ports. i.e., the number of sources of data the stage requires
- port_size - int: Ports are essentially queues inherited from multiprocessing. This is the length of the queue
- destinations - multiprocessing.queue: Default to none. A list of ports from another stage. Recall that ports are multiprocessing queues of a stage.
- has_process - bool: Default is true. Set to false if the stage does not require a process. For example, when using matplotlib for plotting, matplotlib runs its own thread to update plots, thus a process is not needed.

### methods
- run(self): To be implemented by a subclass. Runs forever in a while true loop. This is the code that the subclass customizes to it own purpose.
- start(self): Starts the stage. Run whenever you are ready to begin the process
- stop(self): Stops the stage.
- link_to_destination(self): Adds a new destination to the stage. This is easier to read than providing all destinations at once when creating the object.
- port_get(self): Gets data from all ports. Always use this than accessing individual queues/ports. If a single port is used, add [0] to the end of the call to get the data. This is a blocking operation.
- port_put(self, data): Puts data to all destination ports.

## Message
Messages are used to send data between stages. They are similar in thinking of emails between people. Messages have a main payload and metadata about the payload.

### Properties
payload - any: The main content of the message.
timestamp - datetime.time: The time the message was created. This is also automatically set.
kwargs: Pass any other key word arguments as metadata if wanted. For example: source, size, state, etc.

## Bus
Buses are a stage which take several import ports, merges them into a tuple, and pushes to destinations. Useful for passing several stages to a single stage. It is preferred to have stages with several input ports, but this is an alternative if needed.

### Properties
- num_ports - int: The number of ports to merge.
- port_size - int: The size of the ports.
- destinations - multiprocessing.queue: The destinations of the bus.

## Concatinator
Concatinators concatenate several signal matrices. For example, if there are several recorders to be merged into one recorder, a concatenator will concatenate the signal matrices together. Same properties and methods as bus.

### Properties
- axis - int: The axis which to concatenate over. Default is 1.

## ChannelPicker
When given a matrix, return a column of the matrix. Useful for example when you would like to play back a single channel of a signal matrix.

### Properties
- channel - int: The index of the channel to grab

## Accumulator
Waits and merges several messages together. For example, wait until ten messages are received, put them together, and continue. Useful for saving data to CSV files for example.

### Properties
- num_messages - int: The number of messages to merge
- concatenate - int: If given, rather than returning a list of messages, return a numpy array of several payloads (which must be numpy arrays if ture) concatenated together. Give the axis to concatenate to (typically either 0 or 1)

## FunctionStage
Pass a function to this class to create a stage which runs the function on input data. The function must only have one parameter which accepts data from other stages. This is simpler than creating subclasses for Stage, but is limited in functionality. For example, use this if you would like to call np.ravel() on data, or something just as simple

### Properties
- function - function: The function of which to run on incoming data.

## ToDisk
Writes every payload it receives to disk. Be careful as this can flood data to a disk quickly. Only use when you actually need to record everything. Use a Tap for intermittent recording. It is recommended to put an Accumulator before this to collect data.

### Properties
- label - str: The label to put in the file-name. Every file name has a label and a timestamp
- path - str: The folder where to save data. Do not include a / or \ at the end of the string.

## FromDisk
Takes a file, snips it into blocks, and injects it into a pipeline. Usefully for reading back data from ToDisk or Taps. Data must be saved by numpy. The stage automatically stops when the file is fully read.
- path - str: The path to the file to load
- blocksize - int: The size of the blocks to inject into the pipelines

## Tap
A tap into a pipeline. Does nothing to the data, but saves the last message and makes it user-accessible.

### Properties
- num_ports - int: The number of ports of the stage

### Methods:
- tap(self): Returns a list of messages. The length of messages matches num_ports.

## print_audio_devices - Function
This function prints all available audio devices to the terminal. Useful for finding the ID of the device you are looking to record data from

## AudioRecorder - Stage
Manages an audio device and pushes data to destinations.

### Properties
- device-id - int: The ID of the device to record from. Use print_audio_devices to find it.
- samplerate - int: The sample rate of the device.
- num_channels: - int The number of channels of the device. Must match the channels listed from print_audio_devices()
- blocksize - int: The number of samples per block of data.
- channel_map - list: Pass a list to reorganize the channels. For example [2, 3, 1, 0] will swap the channels so that channel 2 is in index 0, 3 to 1, 1 to 2, and 0 to 3.

### Methods
- Start(self): Starts the recorder and begins pushing data.
- Stop(self): Stops the recorder.

## AudioSimulator - Stage
Simulates ideal audio matrixes. Only simulates a vector of microphones which are evenly spaced for now. Precomputes all signals. Each block of data is the same, but with different noise to simulate real life.

### Properties
- wave_vectors - List[Geometry.geometry.WaveVector] - The list of wavevectors to simulate projected onto elements.
- elements - List[Geometry.geometry.Element]: The list of elements that wavevectors is projected onto.
- snr - float: Signal-to-noise ratio of the simulator.
- samplerate - int: The sample rate of the simulator.
- num_channels - int: The number of elements on the element vector. i.e., the number of audio channels.
- blocksize - int: The number of samples per block of data.
- sleep: If true, add a delay to simulate the delay it takes to get a block of audio in real life.

### Calculated properties
- time_vector - np.array: The points in time that samples are generated at.
- waveforms - np.array: The sound waves generated from the provided wavevectors.
- steering_vectors - np.array: A list of steering vectors. Index matches index of elements.
- signal_matrix - np.array: The simulation result for each element. Result of the optimal simulation
- signal_power - float: The power of the signal matrix.
- noise_power - float: The power of the simulated noise.

## Filter - Stage
A filter is a [digital filter](https://en.wikipedia.org/wiki/Digital_filter). These filters can either be FIR or IIR filters

### Properties
- b_coefficients - np.array: b coefficients of the filter.
- a_coefficients - np.array: a coefficients of the filter.
- samplerate - int: The sample rate of the incoming data
- num_channels - int: The number of elements of the incoming data
- method - str: The method of which to apply the filter
  - lfilter: [Normal convolusion](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.lfilter.html)
  - filtfilt: [apply the filter forwards, then backwards again](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.filtfilt.html#scipy.signal.filtfilt). This guaranties that the phase of the data is not changed **(this is very important for DoA estimators)**, but squares the response of the filter. This is recommended over lfilter for this reason. Note that this is a non-causal operation, but that is okay since all data is known in the block.
- remove_offset - bool: Sets the DC component of the data to zero if true.
- normalize - bool: Set the maximum value of the signal to one if true.

### Methods
- plot_response(self): Plots the response of the filter. This is a blocking operation.
- plot_coefficients(self): Plots the coefficients of the filter. This is a blocking operation.

## ButterFilter - Filter
A lowpass [butterworth filter](https://en.wikipedia.org/wiki/Butterworth_filter). A subclass of filter, inheriting all properties and functions

### Properties
- N - int: The order of the filter.
- cutoff - float: The cutoff frequency of the filter in Hz.

## FIRWINFilter - Filter
A lowpass [ideal filter](https://en.wikipedia.org/wiki/Sinc_filter) using the window method. This is mathematically better than ButterFilter and is recomended. Can have extremely sharp cutoffs. A subclass of filter, inheriting all properties and methods.

### Properties
- N - int: The length of the filter
- cutoff - float: The cutoff frequency of the filter in Hz

## HanningWindow - Stage
Applies a [hanning window](https://en.wikipedia.org/wiki/Hann_function) to incoming data. Simply a **stage** that applies a hanning window.

## FFT - Stage
Applies FFT to data. Returns complex data to match [scipy](https://docs.scipy.org/doc/scipy/reference/generated/scipy.fft.fft.html#scipy.fft.fft).

### Properties
- return_abs - bool: If true, instead of pushing complex data, push the absolute value of the FFT. Use for plotting.

## DOAEstimator - Stage
Takes a DoA estimator and places it into the pipeline.

### Properties
- estimator - direction_of_arival.Estimator: The estimator to utilize

## LinePlotter - Stage
Plots one line or several lines on a grid. If input data is a vector, plot one line. If a matrix, plot one line per list on axis=0.

### Properties
- title - str: The title of the plot.
- x_label - str: The X label of the plot.
- y_label - str: The Y label of the plot.
- num_points - int: The number of points per line. Should match .shape[0] of incoming data if a matrix of length of the data if a vector.
- num_lines - int: The number of lines to draw. Should match .shape[1] of incoming data if a matrix, or simply one if the data is a vector.
- interval - float: The delay in seconds between frame updates. Should match the period of data arrivals to the port (blocksize / samplerate)
- x_data - np.array: If provided, use this as the x-axis data component. If not provided, it is 0 to num_points.
- x_extent - tuple: If provided, show this range on the x-axis by cropping
- y_extent - tuple: If provided, show this range on the y-axis by cropping

### Methods
- show: Show the plot. This is a blocking methods. Call it at the end of your script.

## PolarPlotter - Stage
Similar to LienPlotter, but plots (theta, radius) rather than (x, y).

### Properties
- title - str: The title of the plot.
- num_points - int: The number of points per line. Should match .shape[0] of incoming data if a matrix of length of the data if a vector.
- num_lines - int: The number of lines to draw. Should match .shape[1] of incoming data if a matrix, or simply one if the data is a vector.
- interval - float: The delay in seconds between frame updates. Should match the period of data arrivals to the port (blocksize / samplerate)
- theta_data - np.array: If provided, use this as the x-axis data component. If not provided, it is 0 to num_points, incrementing by 1 (this is never right, always give this. It is optional just for consistency).
- theta_extent - tuple: If provided, show this range on the theta-axis by cropping
- radius_extent - tuple: If provided, show this range on the radius-axis by cropping

## HeatmapPlotter - Stage
Plots a matrix on a heatmap. Same properties and methods as LinePlotter with the addition of:
- z_extent - tuple: sets the maximum and minimum values for the color map.
- cmap - str: The [color map](https://matplotlib.org/stable/users/explain/colors/colormaps.html) which to use for the heatmap. Default is viridis.

## AudioPlayback - Stage
Play data back out to your speakers. Useful for hearing how filters effect data easily for demonstrative purposes. Expects a matrix to keep consistency from recorders and simulators

### Properties
- samplerate - int: The sample rate of the data
- blocksize - int: The blocksize of the data
- channel - int: The channel which to play

#### Properties
- label - str: The label to pass to the file name
- path - str: The path of where to save the file. Must be a folder with no / or \ at the end of the string.

# direction of arival
Holds elements, wave vectors, steering vectors, and steering matrices. Use to calculate steering vectors for simulators and steering matrixes for DoA algorithms. All classes here are dataclass. They have no methods, only hold and calculate data

## spherical_to_cartesian - function
Takes np.array([radius, inclination, azimuth]) and returns np.array([x, y, z]).

## cartesian_to_spherical - function
Takes np.array([x, y, z]) are returns np.array([radius, inclination, azimuth]).

## Element
Holds positional information about an element (a microphone or antenna)

### Properties
- position - np.array: A numpy array holding (x, y, z) position. Units are in wavelengths of a theoretical wavevector.

#### Calculated properties
- spherical_position - np.array: A tuple holding (r, inclination, azimuth) position

## WaveVector
Holds wavevector. Remember to always pass (kx, ky, kz). If you want to pass (wavenumber, inclincation, azimuth), which is more common, translate using spherical_to_cartesian inside the declaration.

### Properties
- k - np.array: A numpy array holding (kx, ky, kz)

#### Calculated properties
- spherical_k - tuple: numpy array holding (wavenumber, inclination, azimuth)
- inclination - float: The inclincation angle of the wavevector in radians. Equal to arctan(ky / kx). 
- azimuth - float: The azimuth angle of the wavevector in radians. Equal to np.arccos(kz / |k|).
- angular_wavenumber - float: The angular wavenumber of the wavevector. |k|.
- angular_wavelength - float: The angular wavelength of the wavevector. Equal to 1 / angular_wavenumber.
- angular_frequency - float: The angular frequency of the wavevector. Equal to angular_wavenumber * wave_speed.
- angular_period - float: The angular period of the wavevector. Equal to 1 / angular_frequency.
- linear_wavenumber - float: The linear wavenumber of the wavevector. Equal to angular_wavenumber / (2 * pi).
- linear_wavelength - float: The linear wavelength of the wavevector. Equal to angular_wavelength * (2 * pi).
- linear_frequency - float: The linear frequency of the wavevector. Equal to angular_frequency / (2 * pi).
- linear_period - float: The linear period of the wavevector. Equal to angular_period * (2 * pi).

## SteeringVector
Represents a steering vector when given elements and a wave vector

### Properties
- elements - List[Element]: A list of elements to project a wavevector onto
- wavevector - WaveVector: A wave vector to project onto elements

#### Calculated properties
- vector - np.array: The resulting steering vector

## SteeringMatrix
Hold every possible steering vector when given elements, wavenumber, and all angles to include

### Properties
- elements - List[Element]: A list of elements to project a wavevector onto
- wavenumber - float: The wave number of the incoming signal
- inclinations - np.array: An array of all possible inclinations to include in the matrix
- azimuths - np.array: An array of all possible azimuths to include in the matrix

### Calculated properties
- matrix - np.array: The resulting steering matrix

## Estimator
A base class for all estimators. Do not use directly

### Properties
- steering_matrix - SteeringMatrix: The main steering matrix to use in the algorithm. All subclasses have a steering matrix.

### Methods
- process(self, data): Runs the algorithm on incoming data. Reservation for subclasses. Raises a NotImplementedError by default.

## DelaySumBeamformer
A classical beamformer. The simpilist to understand and use. However, this is expensive to use and gives sub-par results, thus it is not recomended for this program. Only needs steering_matrix property.

## BartlettBeamformer
A newer beamformer and much more efficient than DelaySumBeamformer. Gives similar results to DelaySUmBeamformer. Only needs steering_matrix property.

## MVDRBeamformer
A very accurate beamformer while being more computationally expensive. Gives, in general good results. Only needs steering_matrix

## Music
The most accurate and most computationally expensive algorithm. Gives extremely accurate results when in an optimal environment.

### Properties
- steering_matrix: Still required as normal
- num_sources: The number of sources in the environment.

# Example

```python
import AccCam.realtime_dsp as dsp
import AccCam.direction_of_arival as doa
import numpy as np


def main():

    # Variables
    samplerate = 44100
    blocksize = 1024
    wave_number = 10
    speed_of_sound = 343

    elements = [doa.Element([-1.25, 0, 0]),
                doa.Element([-0.75, 0, 0]),
                doa.Element([-0.25, 0, 0]),
                doa.Element([0.25, 0, 0]),
                doa.Element([0.75, 0, 0]),
                doa.Element([1.25, 0, 0]),
                doa.Element([0, -1.25, 0]),
                doa.Element([0, -0.75, 0]),
                doa.Element([0, -0.25, 0]),
                doa.Element([0, 0.25, 0]),
                doa.Element([0, 0.75, 0]),
                doa.Element([0, 1.25, 0]),
                doa.Element([0, 0, 0.25]),
                doa.Element([0, 0, 0.75]),
                doa.Element([0, 0, 1.25])]

    wave_vectors = [
        doa.WaveVector(doa.spherical_to_cartesian(np.array([wave_number * 0.98, 1, 1])), speed_of_sound),
        doa.WaveVector(doa.spherical_to_cartesian(np.array([wave_number * 1.02, 2, 2])), speed_of_sound),
    ]

    # Print frequencies for debug
    for vector in wave_vectors:
        print(vector.linear_frequency)

    # Recorder to get data
    recorder = dsp.AudioSimulator(
        elements=elements,
        wave_vectors=wave_vectors,
        snr=50,
        samplerate=samplerate,
        blocksize=blocksize,
        sleep=True
    )

    # Filter
    filt = dsp.FIRWINFilter(
        N=101,
        num_channels=len(elements),
        cutoff=2000,
        samplerate=samplerate,
        method='filtfilt',
    )

    # MUSIC
    azimuth_angles = np.linspace(0, 2 * np.pi, 500)
    inclination_angles = np.linspace(0, np.pi, 500)
    matrix = doa.SteeringMatrix(
        elements=elements,
        azimuths=azimuth_angles,
        inclinations=inclination_angles,
        wavenumber=wave_number
    )
    estimator = doa.MVDRBeamformer(matrix)

    music = dsp.DOAEstimator(estimator)

    # Plot
    plot = dsp.HeatmapPlotter(
        title='MUSIC',
        x_label="inclination",
        y_label="azimuth",
        x_data=inclination_angles,
        y_data=azimuth_angles,
        interval=blocksize/samplerate,
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
