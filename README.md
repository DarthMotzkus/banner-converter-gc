# Banner Converter for GCRebuilder Import

Python script that converts common images (`.png`, `.jpg`, `.jpeg`, `.webp`) into the
BMP banner format that **GCRebuilder** accepts when importing into `opening.bnr`
(the image shown in the GameCube menu / Swiss / Dolphin).

## What it does

1. Scans the folder where `run.py` lives for images.
2. Resizes each one to **96×32** (standard banner size) using a Lanczos filter.
3. Converts it to a **16-bit BMP** in the exact format GCRebuilder expects.
4. Saves the result in `output/`, keeping the original name (only the extension changes to `.bmp`).
   
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
4. Take the generated files from `output/` and import them in GCRebuilder
   (**Banner details → Import...**).

## Disc number template

The folder includes [template disc banner-gc.svg](template%20disc%20banner-gc.svg), an SVG
template for adding the disc number to a banner. It ships with `Disc 1` and `Disc 2` text
examples already placed — edit the text to whatever you need, export the artwork as a PNG,
drop it in this folder, and run the script to turn it into the GCRebuilder BMP.

## Output format (technical details)

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

## Requirements

- Python 3
- [Pillow](https://pypi.org/project/Pillow/)
