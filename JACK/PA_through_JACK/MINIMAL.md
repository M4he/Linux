# Preface
This is a quick followup to [my other guide](README.md) where I explained how to route PulseAudio through JACK using the QJackCtl GUI. 
The following walkthrough is intended for those who wish to permanently use their PulseAudio-through-JACK configuration as created in the original guide without having to rely on the QJackCtl GUI.  
It will introduce a minimalistic approach based on config files and command line tools mostly and is targeted at advanced users.

# Setup
## Package requirements
The following requirements of the original guide still apply:

    jack2 (aka jackd2), calf (aka calf-plugins), pulseaudio-module-jack

Additonally, we need the command line tool `jack-plumbing`. For Debian systems this is part of the package:

    jack-tools

## Realtime scheduling
See the [corresponding section in the original guide](README.md#enable-realtime-scheduling-for-your-user-optional).  
If you decide to omit adding realtime scheduling, you will need to add a `-r` flag to the `jackd` command in the startup script illustrated at the end of this guide!

## Required config files
### 1. Calf config
You should have [set up an EQ](README.md#prepare-the-eq) as instructed in the original guide and have your Calf rack [configuration saved](README.md#save-the-configuration) in `~/.config/jack/calf.conf`

### 2. Plumbing config
Instead of using the Patchbay GUI, we will set up the JACK connections via command line this time.  
We will make use of a rules file for the tool `jack-plumbing`:
- create `~/.config/jack/rules` with the following content:

    ```
    (connect "PulseAudio JACK Sink:front-left" "Calf Studio Gear:eq5 In #1")
    (connect "PulseAudio JACK Sink:front-right" "Calf Studio Gear:eq5 In #2")
    (connect "Calf Studio Gear:eq5 Out #1" "system:playback_1")
    (connect "Calf Studio Gear:eq5 Out #2" "system:playback_2")
    ```
    The brackets have to be included!  
    You can get the names of the plugs by using the **Connect** button of the Calf EQ module and having a look at the list of the available ports.

## Startup script
Finally, this script is to be added to autostart:
```
#!/bin/bash

# startup JACK if it isn't running
if [ -z `pidof jackd` ]
then
    pulseaudio --kill
    jackd -ndefault -dalsa -dhw:0 -r44100 -p1024 -n2 &
    # wait for JACK to be up and running
    jack_wait -w
    pulseaudio --start
fi

# connect PulseAudio to JACK
pactl load-module module-jack-sink channels=2 connect=0
pactl set-sink-volume jack_out 75%
pactl set-default-sink jack_out

# start EQ and Connector if not already running
[ -z `pidof calfjackhost` ] && calfjackhost --load ~/.config/jack/calf.conf &
[ -z `pidof jack-plumbing` ] && jack-plumbing -o ~/.config/jack/rules &
exit
```
Don't forget to `chmod +x` on the script!  
The `jackd` startup command is the same as in `~/.jackdrc` created by QJackCtl when  configured using the GUI. Ḿake sure the `-dhw` flag matches your hardware.

# Final remarks
The [things mentioned in the original guide](README.md#final-remarks) still apply.