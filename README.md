# modthings
A bunch of things related to tracker module / tracker music formats.

This repository contains only two sets of files:

## dss2mod
This piece of code converts files from the Digital Sound Studio format to the MOD format. Every file I have tested works so far (apart from some missing effects).

## modpacker
The packers pack MOD files by using only three bytes per pattern event rather than the regular four. The unpackers convert those files back into regular MODs.
