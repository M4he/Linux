# General Tips & Tricks

This is a random collection of useful tricks and troubleshooting tips around Linux desktop systems mostly.

## Compton

### double shadow on GTK3 client side decorations

Fix it by adding `_GTK_FRAME_EXTENTS@:c` to the `shadow-exclude` list in your `~/.config/compton.conf`:

```
shadow-exclude = [ "_GTK_FRAME_EXTENTS@:c" ]
```

### glitched shadows on screenshots take with xfce4-screenshooter

Fix it by adding `i:e:xfce4-screenshooter` to the `shadow-exclude` list in your `~/.config/compton.conf`:

```
shadow-exclude = [ "i:e:xfce4-screenshooter" ]
```

## Wake On LAN

To enable WOL, add this to your `/etc/rc.local`:
```
ethtool -s eth0 wol g
```
(install `ethtool` and change `eth0` to your adapter)


## Disable Hibernate or Suspend in Xfce's menus

To remove the suspend button:
```
xfconf-query -c xfce4-session -np '/shutdown/ShowSuspend' -t 'bool' -s 'false'
```

To remove the hibernate button:
```
xfconf-query -c xfce4-session -np '/shutdown/ShowHibernate' -t 'bool' -s 'false'
```

## Fix GIMP font anti-alias rendering

Create `/etc/gimp/2.0/fonts.conf` and add:

```
<fontconfig>
  <match target="font">
    <edit name="rgba" mode="assign">
      <const>none</const>
    </edit>
  </match>
</fontconfig>
```

## Extract Japanese ZIP files

Either use `unzip` codepage (not available on all systems):
```
UNZIP="-O cp932" unzip -x archive.zip
```

Or first extract with JP locale:
```
LANG=ja_JP 7z x archive.zip
```

and convert the broken characters:
```
convmv --notest -f shift-jis -t utf8 */*
```

## Xfce: set cursor theme globally

**IMPORTANT:** LightDM is broken and will not let you set the global cursor everywhere, resetting it on reboot. Use another display manager!

Let's say you want the `Breeze` theme to be your default cursor:
- first, setup the cursor in the Xfce settings
- then, do the following:

```
sudo update-alternatives --install /usr/share/icons/default/index.theme x-cursor-theme /usr/share/icons/Breeze/cursor.theme 91

nano ~/.Xdefaults

	Xcursor.theme: Breeze 
	Xcursor.size: 32
```

## Xfce: fix 'open folder' opening wrong application

e.g. in Firefox download window clicking on 'open target directory' will open up some other random application that is able to handle directories.

- open up `xfce4-mime-settings`
- search for `inode/directory`
- click the default application entry on the right and choose your file browser

## Use xwinwrap and MPV to use a video wallpaper

- get `mpv`
- get `xwinwrap`
- run command:
```
xwinwrap -ov -st -sp -b -ni -fs -nf -- mpv -no-audio -quiet -vo xv -wid WID <video>
```
(you may need to kill/turn off any desktop drawing process, e.g. `xfdesktop`)

## Listen to an audio input using PulseAudio loopback or pass-through

### simple high-latency loopback device

- get your input device names:
```
pacmd list sources | grep "name:.*input"
```

- add to your `/etc/pulse/default.pa`*
```
load-module module-loopback source=alsa_input.pci-0000_01_02.0.analog-stereo
```

(adjust the source according to above names)

- you can toggle mute by:
```
pactl set-source-mute alsa_input.pci-0000_01_02.0.analog-stereo toggle
```

(again, name has to match)

(* you may also use your `~/.config/pulse/default.pa` but it has to include the necessary commands of the `/etc/pulse/default.pa`, since it will replace it)

### advanced low-latency pass-through

- install `pacat` (usually part of `pulseaudio-utils`)
- get your input device names:
```
pacmd list sources | grep "name:.*input"
```
- get your output device names:
```
pacmd list sinks | grep "name:.*output"
```
- execute
```
pacat -r --latency-msec=1 -d <source_name> | pacat -p --latency-msec=1 -d <sink_name>

# e.g.
pacat -r --latency-msec=1 -d alsa_input.pci-0000_00_1b.0.analog-stereo | pacat -p --latency-msec=1 -d alsa_output.usb-FiiO_DigiHug_USB_Audio-01-Audio.analog-stereo
```
(replace device names as necessary)
- kill command with `[Ctrl]`+`[C]` to stop


## Fix PolicyKit (polkit) blurry icon in docks (plank, DockBarX etc.)

create a `polkit-pkexec.desktop` file in either `~/.local/share/applications` or `/usr/share/applications` with the following content:
```
[Desktop Entry]
Version=1.0
Type=Application
Name=PolicyKit Password Authentication
Icon=dialog-password
Exec=/usr/lib/policykit-1-gnome/polkit-gnome-authentication-agent-1
NoDisplay=true
StartupNotify=false
Terminal=false
```
(requires your icon theme to provide a suitable `dialog-password` icon)
