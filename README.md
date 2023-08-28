# guitartuner
A guitar tuner app written in python.  It can be used to tune guitar regularly as well while changing the guitar strings to to tune the strings.  

## usage

On linux install pyalsaaudio and aubio as:

```
pip install -U pyalsaaudio
pip install -U aubio
```

On systems if alsaaudio is not available you could use pyaudio and aubio:

```
pip install -U pyaudio
pip install -U aubio
```

Then run the program from script as:

`from guitartuner import myguitargui`
`myguitargui.startTuner()`

or from commandline as

`guitartuner`

## screenshot
![alt text](https://github.com/jithesh82/guitartuner/blob/main/screenshot.png)

## demo video
![alt text](https://github.com/jithesh82/guitartuner/blob/main/demo.gif)
