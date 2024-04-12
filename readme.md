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
[Array processing](https://en.wikipedia.org/wiki/Array_processing) is a wide area of research in the field of signal processing that extends from the simplest form of 1 dimensional line arrays to 2 and 3 dimensional array geometries. Array processing is the background for DoA estimation.

#### Steering vector
Steering vectors are vectors which describe how a signal changes as elements receive the signal at different times. This happens as the same signal is delayed at different elements at different positions. Steering matrixes the position of each element, and the original wavevector(s) of the source(s).

![Graphic of a steering matrix](https://ars.els-cdn.com/content/image/3-s2.0-B978012398499900008X-f08-03-9780123984999.jpg)
#### Steering matrix
A steering matrix is composed of several steering vectors at several different angles. Each row on the matrix describes a different steering vector at a different angle. These matrixes are used in DoA estimation algorithms.

# Management

## Pipeline

### Stages
To achive real-time processing, pipelines can be created using **stages**. **Stages** have a list of **ports** (queues of data), a list of **destinations** (ports of another stage), and a **process**. Each stage is responsible for getting data from the ports, processing the data, and pushing the processed data to destinations. Destinations are ports of another stage.
Stages also introduce multiprocessing. Each stage is ran by its own processes, letting the project leverage the whole CPU.
To use a stage, one must create a subclass which inherits the stage class. The new subclass will create the correct amount of input ports , the length of the input ports (default is 4), and destinations.

#### Properties
- num_ports - int: The number of ports. i.e., the number of sources of data the stage requires
- port_size - int: Ports are essentially queues inherited from multiprocessing. This is the length of the queue
- destinations - multiprocessing.queue: Default to none. A list of ports from another stage. Recall that ports are multiprocessing queues of a stage.
- has_process - bool: Default is true. Set to false if the stage does not require a process. For example, when using matplotlib for plotting, matplotlib runs its own thread to update plots, thus a process is not needed.

#### methods
- run(self): To be implemented by a subclass. Runs forever in a while true loop. This is the code that the subclass customizes to it own purpose.
- start(self): Starts the stage. Run whenever you are ready to begin the process
- stop(self): Stops the stage.
- link_to_destination(self): Adds a new destination to the stage. This is easier to read than providing all destinations at once when creating the object.
- port_get(self): Gets data from all ports. Always use this than accessing individual queues/ports. If a single port is used, add [0] to the end of the call to get the data. This is a blocking operation.
- port_put(self, data): Puts data to all destination ports.

### Busses
Busses are a stage which take several import ports, merges them into a tuple, and pushes to destinations. Useful for passing several stages to a single stage. It is preferred to have stages with several input ports, but this is an alternative if needed.

#### Properties
- num_ports - int: The number of ports to merge.
- port_size - int: The size of the ports.
- destinations - multiprocessing.queue: The destinations of the bus.

### Concatinator
Concatinators concatenate several signal matrixes. For example, if there are several recorders to be merged into one recorder, a concatinatinator will concatenate the signal matrixes together. Same properties and methods as bus.

# DSP
Hold sources, processes, and sinks for audio processing.

## Sources
Sources have no ports, only destinations. Examples include recorders and simulators.

### Recorders
Recorders get data from real-life, such as microphones or audio mixers

#### print_audio_devices - Function
This function prints all available audio devices to the terminal. Useful for finding the ID of the device you are looking to record data from

#### AudioRecorder - Stage
Manages an audio device and pushes data to destinations.

##### Properties
- device-id - int: The ID of the device to record from. Use print_audio_devices to find it.
- samplerate - int: The sample rate of the device.
- num_channels: - int The number of channels of the device. Must match the channels listed from print_audio_devices()
- blocksize - int: The number of samples per block of data.
- channel_map - list: Pass a list to reorganize the channels. For example [2, 3, 1, 0] will swap the channels so that channel 2 is in index 0, 3 to 1, 1 to 2, and 0 to 3.

##### Methods
- Start(self): Starts the recorder and begins pushing data.
- Stop(self): Stops the recorder.

### Simulators
Simulators emulate ideal recorders.

#### AudioSimulator - Stage
Simulates ideal audio matrixes. Only simulates a vector of microphones which are evenly spaced for now. Precomputes all signals. Each block of data is the same, but with different noise to simulate real life.

##### Properties
- wave_vectors - List[Geometry.geometry.WaveVector] - The list of wavevectors to simulate projected onto elements.
- elements - List[Geometry.geometry.Element]: The list of elements that wavevectors is projected onto.
- snr - float: Signal-to-noise ratio of the simulator.
- samplerate - int: The sample rate of the simulator.
- num_channels - int: The number of elements on the element vector. i.e., the number of audio channels.
- blocksize - int: The number of samples per block of data.
- sleep: If true, add a delay to simulate the delay it takes to get a block of audio in real life.
###### Calculated properties
- time_vector - np.array: The points in time that samples are generated at
- waveforms - np.array: The sound waves generated from the provided wavevectors
- steering_vectors - np.array: A list of steering vectors. Index matches index of elements.
- signal_matrix - np.array: The simulation result for each element. Result of the optimal simulation
- signal_power - float: The power of the signal matrix
- noise_power - float: The power of the simulated noise

##### Methods
- Same as Stage

## Processes
Processes have input ports and destinations. Processes manipulate data from sources or other processes. For example, filters, windows, and DoA estimation algorithms are processes.

### Filters
Filters manipulate data, either by applying a filter or a window to a block of data

#### Filter - Stage
A filter is a [digital filter](https://en.wikipedia.org/wiki/Digital_filter). These filters can either be FIR or IIR filters

##### Properties
- b_coefficients - np.array: b coefficients of the filter.
- a_coefficients - np.array: a coefficients of the filter.
- samplerate - int: The sample rate of the incoming data
- num_channels - int: The number of elements of the incoming data
- method - str: The method of which to apply the filter
  - lfilter: [Normal convolusion](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.lfilter.html)
  - filtfilt: [apply the filter forwards, then backwards again](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.filtfilt.html#scipy.signal.filtfilt). This guaranties that the phase of the data is not changed **(this is very important for DoA estimators)**, but squares the response of the filter. This is recommended over lfilter for this reason. Note that this is a non-causal operation, but that is okay since all data is know in the block.
- remove_offset - bool: Sets the DC component of the data to zero if true.
- normalize - bool: Set the maximum value of the signal to one if true.

##### Methods
- plot_response(self): Plots the response of the filter. This is a blocking operation.
- plot_coefficients(self): Plots the coefficients of the filter. This is a blocking operation.
- 
#### ButterFilter - Stage
A lowpass [butterworth filter](https://en.wikipedia.org/wiki/Butterworth_filter). A subclass of filter, inheriting all properties and functions

##### Properties
- N - int: The order of the filter
- cutoff - float: The cutoff frequency of the filter in Hz

##### Methods
Same as Filter.

#### FIRWINFilter - Stage
A lowpass [ideal filter](https://en.wikipedia.org/wiki/Sinc_filter) using the window method. This is mathematically better than ButterFilter and is recomended. Can have extremely sharp cutoffs. A subclass of filter, inheriting all properties and functions

##### Properties
- N - int: The length of the filter
- cutoff - float: The cutoff frequency of the filter in Hz

##### Methods
Same as Filter.

#### HanningWindow - Stage
Applies a [hanning window](https://en.wikipedia.org/wiki/Hann_function) to incoming data. Simply a **stage** that applies a hanning window.

##### Properties
None

##### Methods
Same as Stage

### Spectral
Applies spectral analysis on data.

#### FFT - Stage
Applies FFT to data. Returns complex data to match [scipy](https://docs.scipy.org/doc/scipy/reference/generated/scipy.fft.fft.html#scipy.fft.fft). Just a **stage** that applies FFT to incoming data.

##### Properties
None

##### Methods
Same as Stage

### direction_of_arrival
Direction of arrival algorithms.

#### Beamformer - Stage
A classic [beamforming](https://en.wikipedia.org/wiki/Beamforming) algorithm. Uses a steering matrix to guess which steering vector that was used to get incoming data.

##### Properties
- steering_matrix - Geometry.geometry.SteeringMatrix: The steering matrix for which to solve

##### Methods
Same as Stage

#### MUSIC - Stage
Applies the [MUltiple SIgnal Classification (MUSIC) algorithm](https://en.wikipedia.org/wiki/MUSIC_(algorithm)) to incoming data. Significantly more accurate than beamformer, but much more computational intensive. Can find multiple sources simultaneously.

##### Properties
- steering_matrix - Geometry.geometry.SteeringMatrix: The steering matrix for which to solve
- num_sources - int: The number of sources in the environment

##### Methods
Same as Stage

## Sinks
Sinks have no destinations. An example of a sink is a plot or audio playback.

### Plotters
Plotters are simple GUIs from matplotlib that show data generated by this program.

#### LinePlotter - Stage
Plots one line or several lines on a grid. If input data is a vector, plot one line. If a matrix, plot one line per list on axis=0.

##### Properties
- title - str: The title of the plot.
- x_label - str: The X label of the plot.
- y_label - str: The Y label of the plot.
- num_points - int: The number of points per line. SHould match .shape[0] of incoming data if a matrix of length of the data if a vector.
- num_lines - int: The number of lines to draw. Should match .shape[0] of incoming data if a matrix, or simpily one if the data is a vector.
- interval - float: The delay in seconds between frame updates. SHould match the period of data arrivals to the port (blocksize / samplerate)
- x_data - np.array: If provided, use this as the x-axis data component. If not provided, it is 0 to num_points.
- x_extent - tuple: If provided, show this range on the x-axis by cropping
- y_extent - tuple: If provided, show this range on the y-axis by cropping

##### Methods
- show: Show the plot. This is a blocking methods. Call it at the end of your script.

#### ThreeDimPlotter - Stage
Plots a matrix on a heatmap. Same properties and methods as LinePlotter

### Playback
Listen to your pipeline. Pass data back out of your speakers.

#### AudioPlayback - Stage
Play data back out to your speakers. Useful for hearing how filters effect data easily for demonstrative purposes. Expects a matrix to keep consistency from recorders and simulators

##### Properties
- samplerate - int: The sample rate of the data
- blocksize - int: The blocksize of the data
- channel - int: The channel which to play

# Geometry
Holds elements, wave vectors, steering vectors, and steering matrixes. Use to calculate steering vectors for simulators and steering matrixes for DoA algorithms. All classes here are dataclass. They have no methods, only hold and calculate data

## geometry
Main file

### Element
Holds positional information about an element (a microphone or antena)

#### Properties
- cartesian_position - tuple: A tuple holding (x, y, z) position

##### Calculated properties
- spherical_position - tuple: A tuple holding (r, inclination, azimuth) position

### WaveVector
Holds wave vector information (wavenumber, inclination, azimuth) and (kx, ky, kz)

#### Properties
- spherical_k - tuple: A tuple holding (wavenumber, inclination, azimuth)

##### Calculated properties
- cartesian_k - tuple: A tuple holding (kx, ky, kz)

### SteeringVector
Representes a steering vector when given elements and a wave vector

#### Properties
- elements - List[Element]: A list of elements to project a wavevector onto
- wavevector - WaveVector: A wave vector to project onto elements

##### Calculated properties
- vector - np.array: The resulting steering vector

### SteeringMatrix
Hold every possible steering vector when given elements, wavenumber, and all angles to include

#### Properties
- elements - List[Element]: A list of elements to project a wavevector onto
- wavenumber - float: The wave number of the incoming signal
- inclinations - np.array: An array of all possible inclinations to include in the matrix
- azimuths - np.array: An array of all possible azimuths to include in the matrix

##### Calculated properties
- matrix - np.array: The resulting steering matrix

# Example

```python
from DSP.Sinks import plotters
from DSP.Processes import filters, direction_of_arrival
from DSP.Sources import simulators
from Geometry.geometry import Element, WaveVector, SteeringMatrix, spherical_to_cartesian
import numpy as np


def main():
  # Variables
  samplerate = 44100
  blocksize = 1024
  wave_number = 1.5
  speed_of_sound = 343

  # ELEMENTS
  # sphere
  # elements = [Element(spherical_to_cartesian(1, theta, phi)) for (theta, phi) in product(np.linspace(0, np.pi, 5), np.linspace(0, 2 * np.pi, 10))]

  # Box
  # elements = [Element([x, y, z]) for (x, y, z) in product(np.arange(0, 4, 0.5), np.arange(0, 4, 0.5), np.arange(0, 4, 0.5))]

  # +
  elements = [Element([-1.25, 0, 0]),
              Element([-0.75, 0, 0]),
              Element([-0.25, 0, 0]),
              Element([0.25, 0, 0]),
              Element([0.75, 0, 0]),
              Element([1.25, 0, 0]),
              Element([0, -1.25, 0]),
              Element([0, -0.75, 0]),
              Element([0, -0.25, 0]),
              Element([0, 0.25, 0]),
              Element([0, 0.75, 0]),
              Element([0, 1.25, 0]),
              Element([0, 0, 0.25]),
              Element([0, 0, 0.75]),
              Element([0, 0, 1.25])]

  wave_vectors = [
    WaveVector([wave_number * 1, np.pi / 3.5, np.pi / 2.5], speed_of_sound),
    WaveVector([wave_number * 1.05, np.pi / 2.5, np.pi / 3.5], speed_of_sound)
  ]

  # Recorder to get data
  recorder = simulators.AudioSimulator(
    elements=elements,
    wave_vectors=wave_vectors,
    snr=50,
    samplerate=samplerate,
    blocksize=blocksize,
    sleep=True
  )

  # Filter
  filt = filters.FIRWINFilter(
    N=101,
    num_channels=len(elements),
    cutoff=2000,
    samplerate=samplerate,
    method='filtfilt',
  )

  # MUSIC
  azimuth_angles = np.linspace(0, 2 * np.pi, 500)
  inclination_angles = np.linspace(0, np.pi, 500)
  matrix = SteeringMatrix(
    elements=elements,
    azimuths=azimuth_angles,
    inclinations=inclination_angles,
    wavenumber=wave_number,
    wave_speed=speed_of_sound
  )
  music = direction_of_arrival.MUSIC(
    steering_matrix=matrix,
    num_sources=len(wave_vectors) * 4
  )

  # Plot
  plot = plotters.ThreeDimPlotter(
    title='MUSIC',
    x_label="azimuth",
    y_label="inclination",
    x_data=azimuth_angles,
    y_data=inclination_angles,
    interval=blocksize / samplerate
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
