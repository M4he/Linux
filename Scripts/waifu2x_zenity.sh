#!/bin/bash

# This script uses zenity (you gotta have it installed!) to display a minimal GUI
# for the waifu2x upscaling binary. It uses check boxes and radio buttons to help
# you choose the desired options for upscaling and/or noise reduction.
# This script is meant to be called from your favorite file manager. For example
# in Thunar you can make a 'Custom Action' from the 'Edit' menu for image files.
#
# The first argument passed to this script has to be the path to the input image.
#
# The output file is named like <input_file>_waifu2x_<options>.png
# e.g.
#	'/some/path/best-gril.jpg'
# becomes
#   '/some/path/best-gril_waifu2x_scale2.0_noiseLevel1.png'
#
# REQUIREMENTS
#
# - zenity
# - waifu2x binary (e.g. waifu2x-converter-cpp)
#
# select your waifu2x binary below
WAIFU2X_CMD="waifu2x-converter-cpp"


## INPUT FILE VALIDATION

infile="$1"

if [ ! -f "$1" ]; then
	zenity --error --text "Specified input file does not exist!"
	exit 1
fi

cmd=$WAIFU2X_CMD


## MODE SELECTION

mode=$(zenity --width=240 --height=130 --list --title="Waifu2x - Mode" \
	--text="Choose the options to apply:" --checklist \
	--column "Use" --column "Mode" \
	TRUE "Upscaling" \
	FALSE "Noise Reduction" \
	--separator=':');

# abort if nothing was selected or cancel was pressed
if [ -z "$mode" ] ; then
   exit 1
fi

use_upscale=FALSE
use_denoise=FALSE
fname_apx=""

IFS=":" ; for mod in $mode ; do 
   case $mod in
      "Upscaling") use_upscale=TRUE ;;
      "Noise Reduction") use_denoise=TRUE ;;
   esac
done


## UPSCALE CHOICES

if [ "$use_upscale" = "TRUE" ] ; then

ups=$(zenity --width=240 --height=170 --list --title="Waifu2x - Upscale" \
	--text="Choose size scale:" --radiolist \
	--column "Use" --column="Size Ratio" \
	TRUE "2.0" \
	FALSE "1.75" \
	FALSE "1.5");

if [ -z "$ups" ] ; then
   exit 1
fi


# command line arg
cmd=$cmd' --scale_ratio '$ups
# filename appendix
fname_apx=$fname_apx'_scale'$ups
fi


## NOISE REDUCTION CHOICES

if [ "$use_denoise" = "TRUE" ] ; then

nos=$(zenity --width=240 --height=130 --list --title="Waifu2x - Denoise" \
	--text="Noise reduction:" --radiolist \
	--column "Use" --column="Level" \
	TRUE "1" \
	FALSE "2");

if [ -z "$nos" ] ; then
   exit 1
fi

# command line arg
cmd=$cmd' --noise_level '$nos
# filename appendix
fname_apx=$fname_apx'_noiseLevel'$nos
fi

base=$(basename "$infile")
pardir=$(dirname "$infile")
fname="${base%.*}"


## OUTPUT FILE NAMING

outfile=${pardir}/${fname}'_waifu2x'$fname_apx'.png'

if [ -f "$outfile" ]; then
	zenity --error --text "Output file does already exist:\n'$outfile'!"
	exit 1
fi


## EXECUTION

cmd=$cmd' -i "'$infile'" -o "'$outfile'"'
eval $cmd | zenity --progress --title="Waifu2x - Working..." --pulsate --auto-close --auto-kill
