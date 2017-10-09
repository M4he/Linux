The following software patches are specific for Debian 9 (stretch):

Patch file | Software | Description
--- | --- | ---
`albert_plugins_blurry_icons_fix.patch` | [Albert (Plugins)](https://github.com/albertlauncher/plugins) | Fixes icons of some SVG-only icon themes being displayed blurry in the icon list, see [this issue](https://github.com/albertlauncher/albert/issues/530). This affects Debian 9 due to its Qt5 version.
`xfdesktop4_wallpaper_selection_fix_unselectable_folders.patch`* | Xfdesktop4 | Fixes folders being unselectable (greyed out) in the wallpaper selection dialog.
`thunar_freeze_fix.patch`* | Thunar | Fixes freezing of Thunar when contents of folders update rapidly.
`thunar_consistent_icon_spacing.patch` | Thunar | Introduces globally consistent spacing/padding between icons in icon view.
`thunar_truncate_filenames.patch` | Thunar | Allows filename labels to be truncated in icon view.

*Patches marked with an asterisk are not mine. They are cherry-picked from upstream updates that didn't land in Debian 9.