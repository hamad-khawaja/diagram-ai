import sys
import os
import base64
import re

# Usage: python fix_svg_icons.py input.svg output.svg

def embed_images(svg_path, output_path):
    with open(svg_path, 'r', encoding='utf-8') as f:
        svg = f.read()

    def replace_img(match):
        img_path = match.group(1)
        # Only handle local absolute paths
        if not os.path.isfile(img_path):
            print(f"[WARN] Icon not found: {img_path}")
            return match.group(0)
        ext = os.path.splitext(img_path)[1][1:]
        with open(img_path, 'rb') as imgf:
            b64 = base64.b64encode(imgf.read()).decode('utf-8')
        return f'<image xlink:href="data:image/{ext};base64,{b64}"'

    # Replace all <image xlink:href="..."> with embedded base64
    fixed_svg = re.sub(r'<image xlink:href="([^"]+)"', replace_img, svg)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(fixed_svg)
    print(f"[INFO] Wrote fixed SVG to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python fix_svg_icons.py input.svg output.svg")
        sys.exit(1)
    embed_images(sys.argv[1], sys.argv[2])
