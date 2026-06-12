# v1.0 — Banner Converter for GCRebuilder

First release. 🎉

Converts common images into the 16-bit BMP banner format that **GCRebuilder**
requires when importing into `opening.bnr` (the banner shown in the GameCube
menu / Swiss / Dolphin).

## Features
- Batch-converts all `.png`, `.jpg`, `.jpeg`, `.webp` in the folder.
- Auto-resizes to the standard **96×32** banner size (Lanczos).
- Outputs a GCRebuilder-ready **16-bit BMP** (40-byte BITMAPINFOHEADER, BI_RGB, R5 G5 B5).
- Saves to `output/`, keeping original filenames.
- Includes an editable SVG template (`template disc banner-gc.svg`) with `Disc 1` / `Disc 2` examples.

## Why it just works
GCRebuilder has `ignoreBannerAlpha` hardcoded on, and overflows when a pixel's
alpha bit is set — turning the banner into colored noise. This tool clears bit 15
so GCRebuilder forces opacity correctly. Verified end-to-end against GCRebuilder's
own code and Dolphin's RGB5A3 decoding.

## Usage
```
pip install Pillow
python run.py
```
Then import the files from `output/` in GCRebuilder (**Banner details → Import...**).

## Requirements
- Python 3
- Pillow
