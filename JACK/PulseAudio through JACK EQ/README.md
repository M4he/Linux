# Preface
## This is a WIP
This is guide is a rough guideline that sums up the steps I have done for my system. It has only been tested on Debian 8 (Jessie) so far, YMMV!
If you succeed or fail using this guide, you can drop a feedback in the 'Issues' section of my GitHub repo if you want.

The following section will give a short overview of the goals and approaches of this guide. If you are not interested skip to chapter 'Setup' below.

## This guide will be for you if one of the following things apply:

- you want a professional, system-wide equalizer (and/or other audio manipulation modules) with as low impact on latency as possible
- you want to get rid of audio crackling when changing the volume in your applications that use PulseAudio
- you want to get rid of audio crackling that occurs when starting/quitting applications that use PulseAudio
- you want to fix audio skipping that occurs while using PulseAudio-based equalizer modules (e.g. FFT sink)


## What we will try to achieve

We will place JACK in between ALSA and PulseAudio. JACK will provide a professional, low-latency interface and control of your sound card/chip through ALSA. This attempts to solve many issues that emerge from PulseAudio being bloatware in regards of audio control. Additionally JACK can route the audio signals through any modification software (e.g. EQ) before handing it to the ALSA output, without causing latency problems or disturbances in your audio.
When successful, your system will still run PulseAudio but let JACK handle the audio control. This is extremely user-friendly as you don't have to change anything for your audio applications.
To sum it up:

- you can keep using PulseAudio for your applications
- you will get a system-wide EQ and other audio manipulation tools for limitless tweaking of your system's sound
- you will get rid of most audio imperfections caused by PulseAudio's latency


## Why not use JACK directly and ALSA as fallback?

Using JACK from your audio applications directly is the standard approach for professional audio production in Linux. However there are several consumer applications which don't provide a JACK output module. To name a few: TeamSpeak (multi-user VoIP), Adobe Flash, wine or games in general.
Sure one could use ALSA for those directly, however this would mean those applications will not get routed through the EQ. Plus getting rid of PulseAudio and setting up ALSA correctly might be cumbersome and/or introduce new issues to the user. Still using PulseAudio as an abstraction layer for the JACK connections enables you to throw any audio application at your config and it still gets routed through JACK and your EQ settings. 

# Setup
## Requirements
At least, the following packages are required:

    calf (aka calf-plugins), jack2 (aka jackd2), pulseaudio-module-jack

Create the necessary config dir: `mkdir -p ~/.config/jack`

## Enabling realtime scheduling for your user (optional)
- `sudo nano .jack/pulse-pre-jack-start.sh` and append the following to the end of the file

    ```
    @audio-rt       -       nice            -11
    @audio-rt       -       rtprio          99
    @audio-rt       -       memlock         unlimited
    ```
- `sudo useradd -G audio-rt user` (replace user with your user name)
- log out and back in


## Preparing the EQ

run `calfjackhost`

- choose 'Add plugin' > 'EQ' > 'Equalizer 5 Band' (a 5 band EQ will be added to the window, which we will configure later)
- IMPORTANT: don't close the 'Calf JACK Host' main window!

## Preparing PulseAudio

### Startup scripts
The following scripts are to be executed before and after JACK starts, respectively. They modify the running PulseAudio server to adjust to JACK. This enables us to leave the PulseAudio config as it is, only temporarily modifying it on demand.

- `nano ~/.config/jack/pulse-pre-jack-start.sh`

    ```
    #!/bin/bash
    pacmd suspend true
    calfjackhost --load ~/.jack/calf.conf &

    ```
    The `calfjackhost --load ~/.jack/calf.conf &` line will startup the EQ module window before JACK starts. Without this module running, you will get no sound as JACK routes everything through it.
- `nano ~/.config/jack/pulse-post-jack-start.sh`

    ```
    #!/bin/bash
    pactl load-module module-jack-sink channels=2 connect=0
    pacmd set-default-sink jack_out
    ```
    The `connect=0` parameter is crucial here! If omitted, PulseAudio will try to connect its plugs to the JACK output endpoint. In our setup this would circumvent the EQ and lead to doubled sound, so make sure this doesn't happen.
- `chmod +x .jack/*.sh`

## Setting up JACK
### General config
- open up QJackCtl
- go into settings
    - Tab 'Settings'
        -  under parameter, beneath 'server prefix' make sure that 'name' is set to 'default' (without quotes) and choose 'alsa' as 'driver'
        -  select your primary sound card/chip for 'interface'
        -  check 'realtime' if you enabled realtime scheduling as instructed above
        -  use the save button at the top
    -  Tab 'Options'
        - choose the previously created 'pulse-pre-jack-start.sh' script to be executed at startup
        - choose the previously created 'pulse-post-jack-start.sh' script to be executed after startup
    - Tab 'Misc'
        - check 'Start JACK audio server on application startup'
        - check 'Enable system tray icon'
        - check 'Start minimized to system tray'
- close the settings window

### Setting up the Patchbay
- prepare PulseAudio JACK output to make its plugs visible to JACK
    - in terminal execute `pacmd suspend true`
    - open up QJackCtl and click start, wait for JACK to be started
    - in terminal execute execute `pactl load-module module-jack-sink channels=2`
    - in terminal execute execute `pacmd set-default-sink jack_out`
- in QJackCtl open up the Patchbay and configure it:

    #### Configure output plugs
    - add a PulseAudio output plug
        - click 'Add' on the left hand side
        - select 'PulseAudio JACK sink' as 'Client'
        - add both of its output sockets via the 'Add Plug' button
        - Choose 'PulseAudio' as name and hit 'OK'
    - add an EQ output plug
        - click 'Add' on the left hand side
        - select 'Calf Studio Gear' as 'Client'
        - add both of its 'eq5' output sockets via the 'Add Plug' button
        - Choose 'Calf EQ' as name and hit 'OK'
    
    #### Configure input plugs
    - add an EQ input plug
        - click 'Add' on the right hand side
        - select 'Calf Studio Gear' as 'Client'
        - add both of its 'eq5' input sockets via the 'Add Plug' button
        - Choose 'Calf EQ' as name and hit 'OK'
    - add a master input plug
        - click 'Add' on the right hand side
        - select 'system' as 'Client'
        - add both of its output sockets via the 'Add Plug' button
        - Choose 'Master' as name and hit 'OK'
    
    #### Connect the plugs
    - select 'PulseAudio' on left side and 'Calf EQ' from on right side
    - click 'Connect' at the bottom
    - select 'Calf EQ' on the left side and 'Master' on the right side
    - click 'Connect' at the bottom
    - save your configuration using the button at the top
    - click on 'Activate' at the top right

## Finalizing
If everything worked out correctly, you should be able to hear sound from PulseAudio applications through JACK now. If so, it's time to complete the setup following the instructions below.

### Tweak the EQ and make it permanent
You may now go into the Calf JACK Host window again and manipulate the EQ to your liking, it should immediately affect your audio. If you are satisfied with your configuration:
- go back to the 'Calf JACK Host' main window and select 'File' > 'Save as...'
- save the configuration, e.g. to `~/.config/jack/calf.conf` (make sure the path matches to that in `~/.config/jack/pulse-pre-jack-start.sh`)
- add the Calf Host to your startup applications like this:
    - `calfjackhost --load ~/.config/jack/calf.conf &`

### Add JACK to your startup
Either add `qjackctl` to your autostart or start it manually after login when you need it. QJackCtl will automatically restore the Patchbay config and will connect the plugs when they become available.

## Extending your config
Once you are familiar with how the JACK routing works, you can create more Calf modules and route them together using the Patchbay just like you would with real audio rack. This way you can build more complex setups for your system's audio to suit your needs.