# Banner Converter for GameCube

Python script that turns ordinary images into GameCube banner artwork — the image shown in
the GameCube menu, Swiss, cubiboot and Dolphin. Any size, any of the common formats.

It can build two things, picked from a menu when you run it:

| | Output | Use it for |
|---|---|---|
| **1** | `.bmp` | Importing into an existing `opening.bnr` with **GCRebuilder** |
| **2** | `opening.bnr` | A complete banner file, for a homebrew app folder that ships its own |

## What it does

1. Scans the folder where `run.py` lives for images.
2. Resizes each one to **96×32** (standard banner size) using a Lanczos filter.
3. Encodes it for the option you picked.
4. Saves the result in `output/`.
   
Example:

<img width="96" height="32" alt="bk-1" src="https://github.com/user-attachments/assets/cd9d0f59-f614-4010-bf4d-e594da12b29e" />
<img width="96" height="32" alt="bk-2" src="https://github.com/user-attachments/assets/70289cc4-a292-4f6e-9f69-46ca827f409e" />
<img width="96" height="32" alt="bk-orig-1" src="https://github.com/user-attachments/assets/47bc57ba-e3f6-4e04-af24-2c37cfb53561" />
<img width="96" height="32" alt="bk-orig-2" src="https://github.com/user-attachments/assets/9041ed8f-d5c7-471c-895d-b161789a8cbb" />
<img width="96" height="32" alt="symph-2" src="https://github.com/user-attachments/assets/83ff7da7-8430-4458-9b86-1f498a46a1b6" />
<img width="96" height="32" alt="symph-1" src="https://github.com/user-attachments/assets/3ecab72c-fe93-4f49-aa2d-56734fd43496" />
<img width="96" height="32" alt="mgs-1" src="https://github.com/user-attachments/assets/bf4c9df9-e6a6-4e44-b6f7-42bfddc6934e" />
<img width="96" height="32" alt="mgs-2" src="https://github.com/user-attachments/assets/4f80a3bd-686a-41f6-a4ec-6a21a15239d7" />


## Usage

1. Install the dependency:
   ```
   pip install Pillow
   ```
2. Put your images in the **same folder** as `run.py`.
3. Run:
   ```
   python run.py
   ```
   and pick option **1** (BMP) or **2** (`opening.bnr`).
4. **Option 1** — take the `.bmp` files from `output/` and import them in GCRebuilder
   (**Banner details → Import...**).

   **Option 2** — each image becomes `output/<name>/opening.bnr`. You are asked for a title,
   an author and a description, which are written into the banner. Drop the app's
   `default.dol` next to the `opening.bnr` and the folder is ready to copy to the SD card.

### Non-interactive

Both modes can skip the prompts, which is handy for scripting a whole catalog:

```
python run.py --mode bmp
python run.py --mode bnr --title "My App" --author "Me" --description "Does a thing"
```

## Disc number template

The folder includes [template disc banner-gc.svg](template%20disc%20banner-gc.svg), an SVG
template for adding the disc number to a banner. It ships with `Disc 1` and `Disc 2` text
examples already placed — edit the text to whatever you need, export the artwork as a PNG,
drop it in this folder, and run the script to turn it into the GCRebuilder BMP.

## Output format (technical details)

### opening.bnr (option 2)

The file is `BNR1`: a 4-byte magic, 0x1C bytes of padding, 0x1800 bytes of pixel data and one
320-byte block of text fields (short and long name, short and long author, description). The
whole file is 6496 bytes. `BNR2` is the same thing with six text blocks, one per language;
homebrew has a single set of strings, so `BNR1` is what gets written and every reader accepts
it.

The pixels are **RGB5A3, big-endian, and tiled**. GC textures are not stored as scanlines: a
16-bit texture is cut into 4×4 pixel tiles, each tile written row by row, and the tiles
themselves written left to right, top to bottom. Writing plain scanlines instead produces a
banner shredded into diagonal blocks — it is the easiest thing to get wrong here.

Each pixel uses bit 15 to pick its own interpretation: set means opaque `R5 G5 B5`, clear
means `A3 R4 G4 B4`. Fully opaque pixels therefore keep more colour precision, and unlike the
GCRebuilder path below, **transparency actually works**.

### BMP for GCRebuilder (option 1)

GCRebuilder is picky. The BMP must be exactly:

- **96×32 pixels**, **16 bits per pixel**.
- Classic 40-byte `BITMAPINFOHEADER` (pixel data starts at offset 54).
- **`biCompression = 0` (BI_RGB)** — *no* `BI_BITFIELDS`, *no* color masks.
- Pixels in **R5 G5 B5** with the **alpha bit (bit 15) set to 0**.

### Why the alpha bit is 0

GCRebuilder has `ignoreBannerAlpha` **hardcoded to `TRUE`** (there is no way to turn it off).
On import it computes `(low_byte | 0x8000) + (high_byte << 8)`. If a pixel already has
bit 15 = 1, that addition **overflows** and ends up **clearing** bit 15 — the pixel is then
read as `A3R4G4B4` and the image turns into colored noise.

By keeping bit 15 = 0, the addition doesn't overflow and GCRebuilder itself forces the pixel
to opaque correctly. Result: a correct banner in GCRebuilder **and** in Dolphin.

> Note: since this GCRebuilder always ignores alpha and forces everything opaque,
> banners with transparency are not possible with it.
>
> GCRebuilder did not open .dol or else, only game cube game files.

## Requirements

- Python 3
- [Pillow](https://pypi.org/project/Pillow/)
