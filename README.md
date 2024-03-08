# GT7 SpeedBoard
A simple dashboard for Gran Turismo 7. Also includes a graphical lap comparison tool and a playback server.

Based on code from https://github.com/Bornhall/gt7telemetry and https://github.com/snipem/gt7dashboard.

## Apps

### gt7speedboard

The actual dashboard for racing. 

Features:

- Tyre temperatures
- Fuel consumption and fuel remaining
- Speed comparisons to 
    - the previous lap
    - the best lap
    - the meidan lap
    - up to three pre-loaded reference laps
- Brake points (optionaly with countdown)
- Racing line comparisons
- Special mode for Circuit Experiences
- Record data to a file
- Save the best, last or all laps to a file
- The location-based markers

### gt7playbackserver

Can act as a virtual PlayStation running GT7 to serve pre-recorded telemetry data to any app that can receive it.

### graphicallapcomparison

Load two pre-recorded laps and compare them in a visual way.

- Racing lines
- Brake points
- Speed
- Throttle
- Time gains/losses
- Gears

![Racing line](doc/raceline.png)


Licensed under the GNU General Public License Version 3 (see LICENSE file).
