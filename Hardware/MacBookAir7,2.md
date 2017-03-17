# MacBook Air 7,2 (2015) with Linux

Below explanations concentrate on my experience using Debian 8 (Jessie) on a MacBook Air 7,2 (2015 model) and explain necessary tweaks.

## Installation

- albeit rEFInd works, it will not boot non-EFI bootloaders
- you can ditch rEFInd, grab an EFI-compatible boot disk and install regularly
- for Debian 8, the Live CDs won't boot as they don't include EFI, use the general installation discs!
- Debian will install in such fashion that it boots GRUB per default, in order to boot OSX hold down the alt key at powerup

## Suspend-related problems

### Problem #1: instant wakeup on suspend

Almost everytime after entering suspend, the device will automatically wakeup itself after a second or two.

- **cause:** LID switch triggering regardless of its state or XHCI firing wakeup signals for no reason

- **solution:** scripts for disabling various hardware-based wakeups

- create `/lib/systemd/system-sleep/lid_wakeup_disable`:
```
#!/bin/sh

# /lib/systemd/system-sleep/lid_wakeup_disable
#
# Avoids that system wakes up immediately after suspend or hibernate
# with lid open (e.g. suspend/hibernate through menu entry)
#
# Tested on MacBookPro12,1 & MacBookAir7,2

case $1 in
  pre)
    if cat /proc/acpi/wakeup | grep -qE '^LID0.*enabled'; then
        echo LID0 > /proc/acpi/wakeup
    fi
    ;;
esac
```
- make it executable `chmod +x /lib/systemd/system-sleep/lid_wakeup_disable`
- this script will disable wakeup on lid open completely, simply press any keyboard key to wake up the device

- create `/lib/systemd/system-sleep/xhc_wakeup_disable`:
```
#!/bin/sh

# /lib/systemd/system-sleep/xhc_wakeup_disable
#
# Avoids that system wakes up immediately after suspend or hibernate
# due to XHC triggering (e.g. suspend/hibernate through KDE menu entry)
#
# Tested on MacBookAir7,2

case $1 in
  pre)
    if cat /proc/acpi/wakeup | grep -qE '^XHC1.*enabled'; then
        echo XHC1 > /proc/acpi/wakeup
    fi
    ;;
esac
```
- make it executable `chmod +x /lib/systemd/system-sleep/xhc_wakeup_disable`
- **WARNING**: this script disabled keypress wakeup *except* for the power button, you may only wake up the device from suspend by pressing the power button!
- the XHCI wakeups are not that common and may only happen after a prolonged uptime

### Problem #2: failed wakeup after suspend

Sometimes the wakeup after suspend fails. The screen simply stays black, no reaction to key presses and needs to be hard reset via holding down the power button.

- **cause:** default backlight driver

- **solution:** install mba6x_bl kernel module
```
git clone git://github.com/patjak/mba6x_bl
cd mba6x_bl
make
sudo make install
sudo depmod -a
sudo reboot
```
- **warning:** manual install of this kernel module might need recompilation and reinstallation after every kernel update!
    - it is better to create a dkms package out of it, see its GitHub page for details

- use a suitable script to control brightness via `/sys/class/backlight/mba6x_backlight/brightness` value
    - for example see `Display/mba6x_backlight_control` of this repository

## Intel Graphics (HD 6000 Broadwell)

- in contrast to older chips UXA is not an option anymore, it is far too slow/sluggish from my experience, this chip *needs* SNA to perform
- requires a recent Intel driver to perform, the standard Debian 8 one doesn't cut it - you'll need the one from the backports

### xorg.conf

(usually located at `/usr/share/X11/xorg.conf.d/20-intel.conf` for Debian systems, at `/etc/X11/...` for others)

```
Section "Device"
   Identifier  "Intel Graphics"
   Driver      "intel"
   Option      "AccelMethod" "sna"
   Option      "DRI" "3"
   Option      "TearFree" "true"
EndSection
```

### compton.conf

- use compton with GLX backend, latest git version is preferred

- put to `~/.config/compton.conf`
```
backend = "glx";
paint-on-overlay = true;
glx-no-stencil = true;
glx-no-rebind-pixmap = true;
glx-swap-method = "buffer-age";
xrender-sync = true;
xrender-sync-fence = true;
```
- this config is tweaked specifically for above `xorg.conf`
- `glx-no-stencil` prevents corrupted graphics on popups
- `xrender-sync` prevents tearing in e.g. Firefox
- adjust other non-backend related options to your liking

### Font rendering

- use `hintslight` for `hintstyle`
- *do not* use RGB hinting
- for Sublime Text 3's settings use
```
"font_options":
[
    "subpixel_antialias"
],
```
(do not use `gray_antialias` here!)

- sample `~/.config/fontconfig/fonts.conf`
```
<?xml version="1.0"?>
<!DOCTYPE fontconfig SYSTEM "fonts.dtd">
<!-- created by lxqt-config-appearance (DO NOT EDIT!) -->
<fontconfig>
  <match target="font">
    <edit name="antialias" mode="assign">
      <bool>true</bool>
    </edit>
  </match>
  <match target="font">
    <edit name="rgba" mode="assign">
      <const>none</const>
    </edit>
  </match>
  <match target="font">
    <edit name="lcdfilter" mode="assign">
      <const>lcddefault</const>
    </edit>
  </match>
  <match target="font">
    <edit name="hinting" mode="assign">
      <bool>true</bool>
    </edit>
  </match>
  <match target="font">
    <edit name="hintstyle" mode="assign">
      <const>hintslight</const>
    </edit>
  </match>
  <match target="font">
    <edit name="autohint" mode="assign">
      <bool>false</bool>
    </edit>
  </match>
  <match target="pattern">
    <edit name="dpi" mode="assign">
      <double>96</double>
    </edit>
  </match>
</fontconfig>
```

## WiFi (WLAN)

- uses a **Broadcom BCM4360 43A0** chip
- not supported by `brcmsmac`
- needs `broadcom-sta` driver to work

### Broadcom STA

- although `broadcom-sta` is said to have better power management, it is horrible in terms of stability from my experience
- expect a lot of connection drops and frequent WiFi password dialogs disrupting your work!
- `broadcom-sta` has always been sh*tty on previous MBAs in the same fashion but at least `brcmsmac` was available as an alternative for their chips which isn't the case with this model

## Kernel parameters

### Limiting CState

- this is something I grabbed from a wiki entry saying it is to prevent freezes
- although I've been using this entry without issues, *I do not know whether it is still necessary*

- add `intel_idle.max_cstate=1` to `GRUB_CMDLINE_LINUX_DEFAULT`, e.g.
```
GRUB_CMDLINE_LINUX_DEFAULT="quiet intel_idle.max_cstate=1"
```
- run `sudo update-grub`
