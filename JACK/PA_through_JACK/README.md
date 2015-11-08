# Preface
This is a detailed guide about routing PulseAudio through JACK for better sound performance and system-wide enhancements (like Equalizer etc.).

## This is a WIP
This is guide is a rough guideline that sums up the steps I have done for my systems. It has only been tested on Debian 8 (Jessie) so far, thus YMMV!
If you succeed or fail using this guide, you can drop a feedback in the 'Issues' section of my GitHub repo if you want.

The following section will give a short overview of the goals and approaches of this guide. If you are not interested skip to chapter 'Setup' below.

## Who is this guide intended for
This is for audiophiles and perfectionists alike.

You should have at least a basic understanding of your Linux system and be familiar with the command line. Some command names or paths in this guide might differ for your Linux system, don't expect this to work by blindly copying the commands. It's up to you making appropriate adjustments where necessary.

### You might find this guide handy if:

- you want a professional, system-wide equalizer (and/or other audio manipulation modules) with as low impact on latency as possible
- you want to get rid of audio crackling when changing the volume in your applications that use PulseAudio
- you want to get rid of audio crackling that occurs when starting/quitting applications that use PulseAudio
- you want to fix audio skipping that occurs while using PulseAudio-based equalizer modules (e.g. FFT sink)


## What this guide will try to achieve

We will place JACK in between ALSA and PulseAudio. JACK will provide a professional, low-latency interface and control of your sound card/chip through ALSA. This attempts to solve many issues that emerge from PulseAudio being bloatware in regards of audio control. Additionally JACK can route the audio signals through any JACK-compatible modification software (e.g. EQ) before handing it to the ALSA output, without causing latency problems or disturbances in your audio.
When successful, your system will still run PulseAudio but let JACK handle the audio control. This is extremely user-friendly as you don't have to change anything for your audio applications.
To sum it up:

- you can keep using PulseAudio for your applications
- you will get a system-wide EQ and other audio manipulation tools for limitless tweaking of your system's sound
- you will get rid of most audio imperfections caused by PulseAudio's latency
- you will achieve a setup that doesn't touch your standard PulseAudio config until JACK is explicitly started


## Why not use JACK directly and ALSA as fallback?

Using JACK from your audio applications directly is the standard approach for professional audio production in Linux. However there are several consumer applications which don't provide a JACK output module. To name a few: TeamSpeak (multi-user VoIP), Adobe Flash, wine or games in general.
Sure one could use ALSA for those directly, however this would mean those applications will not get routed through the EQ. Plus getting rid of PulseAudio and setting up ALSA correctly might be cumbersome and/or introduce new issues to the user. Still using PulseAudio as an abstraction layer for the JACK connections enables you to throw any audio application at your config and it still gets routed through JACK and your EQ settings. 

# Setup
## Requirements
At least, the following packages are required:

    calf (aka calf-plugins), jack2 (aka jackd2), pulseaudio-module-jack

Create the necessary config dir: `mkdir -p ~/.config/jack`

## Enabling realtime scheduling for your user (optional)
- edit `/etc/security/limits.conf` (as root) and append the following to the end of the file

    ```
    @audio-rt       -       nice            -11
    @audio-rt       -       rtprio          99
    @audio-rt       -       memlock         unlimited
    ```
- `sudo groupadd audio-rt`
- `sudo usermod -a -G audio-rt user` (replace user with your user name)
- log out and back in


## Preparing the EQ

run `calfjackhost`

- choose 'Add plugin' > 'EQ' > 'Equalizer 5 Band'

![Screenshot of the Calf deck](./calf.png?raw=true)

(a 5 band EQ will be added to the window, which we will configure later)
- IMPORTANT: don't close the 'Calf JACK Host' main window!

## Preparing PulseAudio

### Startup scripts
The following scripts are to be executed before and after JACK starts, respectively (which we will configure later). They modify the running PulseAudio server to adjust to JACK. This enables us to leave the PulseAudio config as it is, only temporarily modifying it on demand.

- edit `~/.config/jack/pulse-pre-jack-start.sh`

    ```
    #!/bin/bash
    pacmd suspend true
    calfjackhost --load ~/.jack/calf.conf &

    ```
    The `calfjackhost --load ~/.jack/calf.conf &` line will startup the EQ module window before JACK starts. Without this module running, you will get no sound as JACK routes everything through it.
- edit `~/.config/jack/pulse-post-jack-start.sh`

    ```
    #!/bin/bash
    pactl load-module module-jack-sink channels=2 connect=0
    pactl set-sink-volume jack_out 75%
    pacmd set-default-sink jack_out
    ```
    The `connect=0` parameter is crucial here! If omitted, PulseAudio will try to connect its plugs to the JACK output endpoint. In our setup this would circumvent the EQ and lead to doubled sound, so make sure this doesn't happen.  
    Adjust the `set-sink-volume` to your liking. From my experience, using 100% can lead to audio clipping in JACK when PulseAudio is outputting at a too high volume.
- execute `chmod +x ~/.config/jack/*.sh`

## Setting up JACK
### General config
- open up QJackCtl
- Adjust at least the following settings:
    - Tab 'Settings'
        - under parameter, beneath 'server prefix' make sure that 'name' is set to 'default' (without quotes) and choose 'alsa' as 'driver'
        - select your primary sound card/chip for 'interface'
        - check 'realtime' if you enabled realtime scheduling as instructed above
        - use the save button at the top
    -  Tab 'Options'
        - choose the previously created 'pulse-pre-jack-start.sh' script to be executed at startup
        - choose the previously created 'pulse-post-jack-start.sh' script to be executed after startup
        ![Screenshot of the script configuration](./scripts.png?raw=true)
    - Tab 'Misc'
        - check 'Start JACK audio server on application startup'
        - check 'Enable system tray icon'
        - check 'Start minimized to system tray'
- close the settings window

### Setting up the Patchbay
The following is a onetime procedure that sets up all the necessary connections for JACK. Once saved, they will be automatically loaded by QJackCtl on each start.
- prepare PulseAudio JACK output to make its plugs visible to JACK
    - execute `pacmd suspend true`
    - open up QJackCtl and click start, wait for JACK to be started
    - execute `pactl load-module module-jack-sink channels=2 connect=0`
    - execute `pacmd set-default-sink jack_out`
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

![Screenshot of the resulting Patchbay](./patchbay.png?raw=true)

(notice the thin lines between the sockets, those indicate the virtual plug connections within JACK)

## Finalizing
If everything worked out correctly, you should be able to hear sound from PulseAudio applications through JACK now. If so, it's time to complete the setup following the instructions below.

### Tweak the EQ and make it permanent
You may now go into the Calf JACK Host window again and manipulate the EQ to your liking, it should immediately affect your audio.

![Screenshot of the EQ](./eq.png?raw=true)

If you are satisfied with your configuration:
- go back to the 'Calf JACK Host' main window and select 'File' > 'Save as...'
- save the configuration, e.g. to `~/.config/jack/calf.conf` (make sure the path matches to that in `~/.config/jack/pulse-pre-jack-start.sh`)

### Add JACK to your startup
Either add `qjackctl` to your autostart or start it manually after login when you need it. QJackCtl will automatically restore the Patchbay config and will connect the plugs when they become available. As long as you don't start QJackCtl, you will run your standard PulseAudio configuration.

### Tame PulseAudio
PulseAudio likes to load an absurd amount of modules at startup. When using JACK for device control, you might want to get rid of some unnecessary modules.  
Open up `/etc/pulse/default.pa` (as root) and look for `load-module` lines that don't have a `#` in front of them (lines with a `#` in front are ignored by PulseAudio).  
If you find an offending module, put a `#` in front of that line. Some guesses are:
    module-role-cork
    module-bluetooth-*
    module-jackdbus-detect


## Extending your config
Once you are familiar with how the JACK routing works, you can create more Calf modules and route them together using the Patchbay just like you would with real audio rack. This way you can build more complex setups for your system's audio to suit your needs.