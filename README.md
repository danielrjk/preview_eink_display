# E-Ink Display Previewer

A browser-based simulator for e-ink displays. Write [GxEPD2](https://github.com/ZinggJM/GxEPD2)-compatible code in the editor and see a live pixel-accurate preview without needing physical hardware.

**Live demo:** https://kielma.dev.br/eink_visualizer

## Features

- Live preview of a 296x128 pixel e-ink display
- Code editor with syntax highlighting (CodeMirror)
- C-style syntax support (`for` loops with `i++`, `i--`, `i+=n`)
- Drawing primitives: lines, rectangles, circles, triangles
- 200+ BDF bitmap fonts from the [u8g2](https://github.com/olikraus/u8g2) library
- Barcode rendering: EAN-13, EAN-8, UPC-A, UPC-E (based on [BarcodeGFX](https://github.com/wallysalami/BarcodeGFX))
- QR code generation (based on [QRCodeGFX](https://github.com/wallysalami/QRCodeGFX))
- 4 display rotation modes (0°, 90°, 180°, 270°)

## Installation

```bash
git clone https://github.com/danielrjk/preview_eink_display.git
cd preview_eink_display
pip install -r requirements.txt
python manage.py runserver
```

Open http://localhost:8000/eink_visualizer in your browser.

## Usage

Write your display code in the left panel using the API below. The preview updates on each run. Use `GxEPD_BLACK` and `GxEPD_WHITE` as color constants.

```python
display.fillScreen(GxEPD_WHITE)
fonts.setFont("u8g2_font_ncenB14_tr")
fonts.setFontMode(1)
fonts.setCursor(10, 40)
fonts.print("Hello, world!")
```

## API Reference

### Display (`display`)

| Method | Description |
|---|---|
| `fillScreen(color)` | Fill the entire screen with a color |
| `drawLine(x1, y1, x2, y2, color)` | Draw a line |
| `drawRect(x, y, w, h, color)` | Draw a rectangle outline |
| `fillRect(x, y, w, h, color)` | Draw a filled rectangle |
| `drawCircle(x, y, r, color)` | Draw a circle outline |
| `fillCircle(x, y, r, color)` | Draw a filled circle |
| `drawTriangle(x1,y1, x2,y2, x3,y3, color)` | Draw a triangle outline |
| `fillTriangle(x1,y1, x2,y2, x3,y3, color)` | Draw a filled triangle |

### Fonts (`fonts`)

| Method | Description |
|---|---|
| `setFont("u8g2_font_<name>_<style>")` | Set the active font |
| `setCursor(x, y)` | Set text cursor position |
| `print("text")` | Render a string at the cursor |
| `drawGlyph(x, y, encoding)` | Render a single character by Unicode code point |

Font names follow the u8g2 convention, e.g. `u8g2_font_ncenB14_tr`, `u8g2_font_6x10_tr`. See the full font list at the [u8g2 wiki](https://github.com/olikraus/u8g2/wiki/fntlistall).

### Barcode (`barcode`)

```python
barcode.setScale(2)
barcode.setShowDigits(True)
barcode.draw("5901234123457", x, y, height)
```

| Method | Description |
|---|---|
| `draw(code, x, y, height)` | Draw a barcode (type auto-detected) |
| `setScale(n)` | Set scale factor (1–20) |
| `setShowDigits(bool)` | Show/hide digit labels |
| `setColors(background, bars)` | Set background and bar colors |

Supported formats: EAN-13, EAN-8, UPC-A, UPC-E.

### QR Code (`qrcode`)

```python
qr.setScale(2)
qr.draw("https://example.com", x, y)
```

| Method | Description |
|---|---|
| `draw(text, x, y)` | Draw a QR code |
| `setScale(n)` | Set scale factor (1–20) |

## Dependencies

- [Django](https://www.djangoproject.com/) 5.1
- [NumPy](https://numpy.org/) 2.2
- [Pillow](https://python-pillow.org/) 11.1
- [bdfparser](https://github.com/tomchen/bdfparser) 2.2
- [qrcodegen](https://github.com/nayuki/QR-Code-generator) 1.8
- u8g2 BDF fonts by [Olikraus](https://github.com/olikraus/u8g2)
- [GxEPD2](https://github.com/ZinggJM/GxEPD2) - the e-ink display library this tool is designed to simulate
- [BarcodeGFX](https://github.com/wallysalami/BarcodeGFX) - barcode rendering API
- [QRCodeGFX](https://github.com/wallysalami/QRCodeGFX) - QR code rendering API

## License

MIT — see [LICENSE](LICENSE).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).
