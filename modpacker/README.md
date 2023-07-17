# modpacker
These packers / depackers I wrote are for your ordinary MOD files. S3M support not available, but it ~~shouldn't~~ should take a lot of effort (and possibly a new LMF2 format just to support it)

The magic is "LMFx", where x is a number between 0 and 1. The only difference between the (older) LMF0 format and the (newer) LMF1 format is that there are no sample names.

The files start, of course, with the already described magic. Read this if you want to add support for this file format in some way (all values are big-endian here):

| offset | length | description |
| ------ | ------ | ----------- |
| 0 | 4 | "LMFx" |
| 4 | 20 | song name |
| ------ | ------ | ----------- |
| 24 | 22 | sample finetune |
| 24 (24) | 2 | sample length (this structure is repeated 31 times) |
| 26 (26) | 1 | sample finetune |
| 27 (27) | 1 | sample default volume |
| 28 (28) | 2 | sample **repeat** start |
| 30 (30) | 2 | sample **repeat** length |
| ------ | ------ | ----------- |
| ??? | 1 | song length in orders |
| ??? | 1 | restart position |
| ??? | 128 | order info |
| ??? | 1 | number of channels |
| ------ | ------ | ----------- |
| ??? | 7 bits | note (0 is no note, 1 is C-2 in Modplug and derivatives) |
| ??? | 5 bits | instrument |
| ??? | 4 bits | fx type; all fx are the same as plain ol' MOD |
| ??? | 8 bits | fx param |
