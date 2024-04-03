Up-to date as of 4/3/2024
# Table of Contents
- [Table of Contents](#table-of-contents)
- [Indroduction](#indroduction)
  - [Background knowledge](#background-knowledge)
    - [Array processing](#array-processing)
      - [Steering vector](#steering-vector)
      - [Steering matrix](#steering-matrix)
- [Management](#management)
  - [Pipeline](#pipeline)
    - [Stages](#stages)
      - [Properties](#properties)
      - [Functions](#functions)
    - [Busses](#busses)
      - [Properties](#properties-1)
    - [Concatinator](#concatinator)
- [DSP](#dsp)
  - [Sources](#sources)
    - [Recorders](#recorders)
      - [print\_audio\_devices - Function](#print_audio_devices---function)
      - [AudioRecorder - Stage](#audiorecorder---stage)
        - [Properties](#properties-2)
        - [Functions](#functions-1)
    - [Simulators](#simulators)
      - [Source](#source)
        - [Properties](#properties-3)
      - [AudioSimulator - Stage](#audiosimulator---stage)
        - [Properties](#properties-4)
        - [Functions](#functions-2)
  - [Processes](#processes)
    - [Filters](#filters)
      - [Filter - Stage](#filter---stage)
        - [Properties](#properties-5)
        - [Functions](#functions-3)
      - [ButterFilter - Stage](#butterfilter---stage)
        - [Properties](#properties-6)
      - [FIRWINFilter - Stage](#firwinfilter---stage)
        - [Properties](#properties-7)
      - [HanningWindow - Stage](#hanningwindow---stage)
    - [Spectral](#spectral)
      - [FFT - Stage](#fft---stage)
    - [direction\_of\_arrival](#direction_of_arrival)
      - [Beamformer - Stage](#beamformer---stage)
        - [Properties](#properties-8)
        - [Functions](#functions-4)
      - [MUSIC - Stage](#music---stage)
        - [Properties](#properties-9)
        - [Functions](#functions-5)
  - [Sinks](#sinks)
    - [Plotters](#plotters)
      - [SingleLinePlotter - Stage](#singlelineplotter---stage)
        - [Properties](#properties-10)
      - [MultiLinePlotter - Stage](#multilineplotter---stage)
      - [Parametric Plots](#parametric-plots)
    - [Applications](#applications)
    - [Playback](#playback)
      - [AudioPlayback - Stage](#audioplayback---stage)
        - [Properties](#properties-11)
- [Example](#Example) 


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
- 
## Background knowledge
Background knowledge in order to understand the project

### Array processing
[Array processing](https://en.wikipedia.org/wiki/Array_processing) is a wide area of research in the field of signal processing that extends from the simplest form of 1 dimensional line arrays to 2 and 3 dimensional array geometries. Array processing is the background for DoA estimation.

#### Steering vector
Steering vectors are vectors which describe how a signal changes as elements receive the signal at different times. This happens as the same signal is delayed at different elements at different positions. Steering matrixes require spacing (in units of wavelengths), and DoA.

![Graphic of a steering matrix](https://ars.els-cdn.com/content/image/3-s2.0-B978012398499900008X-f08-03-9780123984999.jpg)
#### Steering matrix
A steering matrix is composed of several steering vectors at several different angles. Each row on the matrix describes a different steering vector at a different angle. These matrixes are used in DoA estimation algorithms.

# Management

## Pipeline

### Stages
To achive real-time processing, pipelines can be created using **stages**. **Stages** have a list of **ports** (queues of data), a list of **destinations** (ports of another stage), and a **process**. Each stage is responsible for getting data from the ports, processing the data, and pushing the processed data to destinations. Destinations are ports of another stage.
Stages also introduce multiprocessing. Each stage is ran by its own processes, letting the project leverage the whole CPU.

#### Properties
- num_ports: The number of ports. i.e., the number of sources of data the stage requires
- port_size: Ports are essentially queues inherited from multiprocessing. This is the length of the queue
- destinations: Default to none. A list of ports from another stage
- has_process: Default is true. Set to false if the stage does not require a process. For example, when using pyqtplot, timers are used instead of processes.

#### Functions
- run: To be implemented by a subclass. Runs forever in a while true loop. This is the code that the subclass customizes to it own purpose.
- start: Starts the stage. Run whenever you are ready to begin the process
- stop: Stops the stage.
- link_to_destination. Adds a new destination to the stage. This is easier to read than providing all destinations at once when creating the object.
- port_get: Gets data from all ports. Always use this than accessing individual queues/ports. If a single port is used, add [0] to the end of the call to get the data. This is a blocking operation.
- port_put: Puts data to all destination ports.
To use a stage, one must create a subclass which inherits the stage class. The new subclass will create the correct amount of input ports , the length of the input ports (default is 4), and destinations.

### Busses
Busses are a stage which take several import ports, merges them into a tuple, and pushes to destinations. Useful for passing several stages to a single stage. It is preferred to have stages with several input ports, but this is an alternative if needed.

#### Properties
- num_ports: The number of ports to merge.
- port_size: The size of the ports.
- destinations: The destinations of the bus.

### Concatinator
Concatinators concatenates several signal matrixes. For example, if there are several recorders to be merged into one recorder, a concatinatinator will concatenate the signal matrixes together. Same properties as bus.

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
- device-id: The ID of the device to record from. Use print_audio_devices to find it.
- samplerate: The sample rate of the device.
- num_channels: The number of channels of the device.
- blocksize: The number of samples per block of data.
- channel_map: Pass a list to reorganize the channels. For example [2, 3, 1, 0] will swap the channels so that channel 2 is in index 0, 3 to 1, 1 to 2, and 0 to 3.

##### Functions
- Start: Starts the recorder and begins pushing data.
- Stop: Stops the recorder.

### Simulators
Simulators emulate ideal recorders.

#### Source
*WIP - custom geometries*
Defines and audio source. Only holds frequency and theta (DOA) values. Needed for simulators to project onto a steering matrix.

##### Properties
- frequency: The frequency in Hz of the source.
- theta: The DOA of the source.

#### AudioSimulator - Stage
*WIP - custom geometries*
Simulates ideal audio matrixes. Only simulates a vector of microphones which are evenly spaced for now. Precomputes all signals. Each block of data is the same, but with different noise to simulate real life.

##### Properties
- sources: A list of sources.
- spacing: The spacing between elements in wavelengths.
- snr: Signal-to-noise ratio of the simulator.
- samplerate: The sample rate of the simulator.
- num_channels: The number of elements on the element vector. i.e., the number of audio channels.
- blocksize: The number of samples per block of data.
- speed_of_sound: The speed of sound in the environment.
- sleep: If true, add a delay to simulate the delay it takes to get a block of audio in real life.

##### Functions
- update_precompute: Run whenever a system property changes to update the signal matrix
Don't forget to start the simulator using start(). See stage for a reminder

## Processes
Processes have input ports and destinations. Processes manipulate data from sources or other processes. For example, filters, windows, and DoA estimation algorithms are processes.

### Filters
Filters manipulate data, either by applying a filter or a window to a block of data

#### Filter - Stage
A filter is a [digital filter](https://en.wikipedia.org/wiki/Digital_filter). These filters can either be FIR or IIR filters

##### Properties
- b_coefficients: b coefficients of the filter.
- a_coefficients: a coefficients of the filter.
- samplerate: The sample rate of the incoming data
- num_channels: The number of elements of the incoming data
- method: The method of which to apply the filter
  - lfilter: [Normal convolusion](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.lfilter.html)
  - filtfilt: [apply the filter forwards, then backwards again](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.filtfilt.html#scipy.signal.filtfilt). This guaranties that the phase of the data is not changed **(this is very important for DoA estimators)**, but squares the response of the filter. This is recommended over lfilter for this reason. Note that this is a non-causal operation, but that is okay since all data is know in the block.
- remove_offset: Sets the DC component of the data to zero if true.
- normalize: Set the maximum value of the signal to one if true.

##### Functions
- plot_response: Plots the response of the filter. This is a blocking operation.

#### ButterFilter - Stage
A lowpass [butterworth filter](https://en.wikipedia.org/wiki/Butterworth_filter). A subclass of filter, inheriting all properties and functions

##### Properties
- N: The order of the filter
- cutoff: The cutoff frequency of the filter in Hz

#### FIRWINFilter - Stage
A lowpass [ideal filter](https://en.wikipedia.org/wiki/Sinc_filter) using the window method. This is mathematically better than ButterFilter and is recomended. Can have extremely sharp cutoffs. A subclass of filter, inheriting all properties and functions

##### Properties
- N: The length of the filter
- cutoff: The cutoff frequency of the filter in Hz

#### HanningWindow - Stage
Applies a [hanning window](https://en.wikipedia.org/wiki/Hann_function) to incoming data. No properties of functions, simply a **stage** that applies a hanning window.

### Spectral
Applies spectral analysis on data.

#### FFT - Stage
Applies FFT to data. Returns complex data to match [scipy](https://docs.scipy.org/doc/scipy/reference/generated/scipy.fft.fft.html#scipy.fft.fft). No properties or functions, just a **stage** that applies FFT to incoming data.

### direction_of_arrival
Direction of arrival algorithms.

#### Beamformer - Stage
A classic [beamforming](https://en.wikipedia.org/wiki/Beamforming) algorithm. Uses a steering matrix to guess which steering vector that was used to get incoming data.

##### Properties
- num_channels: The number of elements of the incoming data
- spacing: The spacing in wavelengths of the element vector
- test_angles: The number of possible angles to test for. Default is 1000

##### Functions
- precompute: Run whenever a system property changes

#### MUSIC - Stage
Applies the [MUltiple SIgnal Classification (MUSIC) algorithm](https://en.wikipedia.org/wiki/MUSIC_(algorithm)) to incoming data. Significantly more accurate than beamformer, but much more computational intensive. Can find multiple sources simultaneously.

##### Properties
- num_channels: The number of elements of the incoming data
- num_sources: The number of signal sources in the data
- spacing: The spacing in wavelengths of the element vector
- test_angles: The number of possible angles to test for. Default is 1000

##### Functions
- precompute: Run whenever a system property changes

## Sinks
Sinks have no destinations. An example of a sink is a plot or audio playback.

### Plotters
Plotters are simple GUIs that plot incoming data. Can only have one plot open at once and plotters can only have one port of data.
Call 'app = QtWidgets.QApplication([])' before creating an object. Open the window by calling '.exec()' on the object.

#### SingleLinePlotter - Stage
Plots a single line of data. Data is expected to be a vector.

##### Properties
- title: The title of the plot.
- x_label: The X label of the plot.
- y_label: The Y label of the plot.
- x_range: The X range of the plot.
- y_range: The y range of the plot.
- blocksize: The blocksize of incoming data. SHould be equivalent to the other blocksizes in your program.
- x_data: Provide if a custom x_data is needed. For example, np.arrange(-90, 90, 1000) for a DoE estimator

#### MultiLinePlotter - Stage
Plots multiple lines of data. Same properties as SingleLinePlotter, but data is expected to be a matrix.

#### Parametric Plots
**SingleLinePlotterPrameteric** and **MultiPlotterParameteric** classes inherit **SingleLinePlotter** and **MultiLinePlotter** respectively. Expect two sets of data in one port as a tuple, such as (x, y). These classes have the same properties, but just expect different data.

### Applications
Applications are more complicated than plotters. They are custom-built to custom scripts, such as a three-axis MUSIC analyzer. Put future applications here. All documentation is in the file.

### Playback
Listen to your pipeline. Pass data back out of your speakers.

#### AudioPlayback - Stage
Play data back out to your speakers. Useful for hearing how filters effect data easily for demonstrative purposes. Expects a matrix to keep consistency from recorders and simulators

##### Properties
- samplerate: The sample rate of the data
- blocksize: The blocksize of the data
- channel: The channel which to play

# Example
```python
  from DSP.Sinks import plotters
  from DSP.Processes import direction_of_arrival, filters
  from DSP.Sources import simulators
  from pyqtgraph.Qt import QtWidgets
  import numpy as np
  
  
  def main():
  
      # Variables
      samplerate = 44100
      blocksize = 44100
      spacing = 0.5
      snr = 50
      channels = 8
      sleep = False
  
      # Sources
      sources = [simulators.Source(675, 10), simulators.Source(775, 30)]
  
      # Recorder to get data
      recorder = simulators.AudioSimulator(
          sources=sources,
          spacing=spacing,
          snr=snr,
          samplerate=samplerate,
          num_channels=channels,
          blocksize=blocksize,
          sleep=sleep
      )
  
      # Filter
      filt = filters.FIRWINFilter(
          N=101,
          num_channels=channels,
          cutoff=1000,
          samplerate=samplerate,
          method='filtfilt',
      )
  
      # MUSIC
      music = direction_of_arrival.MUSIC(num_channels=channels, num_sources=4, spacing=spacing)
  
      # Plotter
      app = QtWidgets.QApplication([])
      plot = plotters.SingleLinePlotter(
          title='MUSIC',
          x_label='Angle',
          y_label='Power',
          blocksize=1000,
          x_data=np.linspace(-90, 90, 1000),
          x_range=(-90, 90),
          y_range=(0, 1)
      )
  
      # Linking
      recorder.link_to_destination(filt, 0)
      filt.link_to_destination(music, 0)
      music.link_to_destination(plot, 0)
  
      # Start processes
      recorder.start()
      filt.start()
      music.start()
      plot.show()
      app.exec()
  
  
  if __name__ == '__main__':
      main()
```
