# Pasonomi VR Remote on Linux tweaks

## Preface

The Pasonomi VR Remote is a very cheap bluetooth remote controller with a small joystick and a few buttons. It works out of the box with Linux but the button mapping is subpar for presentations. It has a few different modes how the stick and buttons will be interpreted on the bluetooth receiver.

One of those modes is a mouse mode (`@`+`D` on the remote), where the joystick is used for controlling the mouse pointer. Sadly, the joystick isn't very accurate and to make matters worse the default speed is far too high. This is one of the problems we will address with the following fix.

In mouse mode the two trigger buttons at the end of device as well as the buttons "A" and "B" are mapped to "left-click" and "Escape" respectively. Buttons "C" and "D" are mapped to "Volume Up" and "Volume Down" respectively. This is subpar for holding presentations: there is no way to navigate backwards in slides and the "Escape" mapped button will always exit presentations. Furthermore I found the volume keys to be useless for normal presentations. So we will also remap the less useful buttons in the following fix.

## The changes

We will apply the following key code changes:

Button | Before | After | Reason
--- | --- | --- | ---
Lower trigger, B | Escape | Backspace | This allows navigating backwards in presentations.
C | Volume Up | Compose (context menu) | We can't map a genuine mouse right-click, so this is the closest we can get.
D | Volume Down | F5 | F5 is used for starting the presentation in most programs.

Also we will increase the DPI to `2400` in order to reduce the pointer speed, allowing for more accurate navigation.

We will be doing this on the `udev` level in order to change the mapping between the device's **scancodes** (1st level) and resulting **keycodes** (2nd level). This solution is persistent and hassle-free, the remapping is applied as soon as the device is registered.

Note: using `xkb` to change the mapping between **keycodes** (2nd level) and resulting **symbols** (3rd level) will not work for every case, since applications may already interpret keys at the 2nd level, that's why we will be intercepting at udev level.

## Instructions

### 1. udev hardware database entry

First, create a `.hwdb` file within `/etc/udev/hwdb.d/`, e.g. `/etc/udev/hwdb.d/90-vrpark.hwdb` with the following content (as root):

    evdev:name:VR-PARK*
     KEYBOARD_KEY_70029=backspace
     KEYBOARD_KEY_c00e9=compose
     KEYBOARD_KEY_c00ea=f5
     MOUSE_DPI=2400@125

- the Pasonomi VR Remote identifies itself with the name `VR-PARK` towards `udev`, so we use this string to grab the device
- for the `KEYBOARD_KEY_*` identifiers, I used the `value` from `evtest /dev/input/event5`
  - a full list of possible remapping codes for the right side can be [found here](https://hal.freedesktop.org/quirk/quirk-keymap-list.txt)
- the DPI value was just trial-and-error, so adjust as you like
    - the value after the `@` sign is supposed to be the frequency, I just copied this from other samples online and didn't change it

### 2. rebuilding udev's hardware database

Now we need `udev` to rebuild its hardware database (run as root):

    systemd-hwdb update

Finally, just reconnect your device and changes should be applied.