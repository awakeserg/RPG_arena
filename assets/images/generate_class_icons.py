import os
from PIL import Image, ImageDraw


SIZE = 256
CENTER = SIZE // 2
OUTPUT_DIR = os.path.dirname(__file__)


def make_canvas(bg_color, ring_color):
	image = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
	draw = ImageDraw.Draw(image)
	draw.ellipse((10, 10, 246, 246), fill=bg_color, outline=ring_color, width=10)
	draw.ellipse((34, 26, 190, 182), fill=(255, 255, 255, 20))
	return image, draw


def draw_warrior():
	image, draw = make_canvas((55, 80, 130, 255), (210, 225, 255, 255))
	draw.polygon([(128, 36), (72, 72), (92, 176), (164, 176), (184, 72)], fill=(180, 195, 220, 255))
	draw.polygon([(128, 54), (92, 78), (105, 160), (151, 160), (164, 78)], fill=(120, 140, 170, 255))
	draw.rounded_rectangle((121, 76, 135, 196), radius=5, fill=(115, 80, 45, 255))
	draw.rounded_rectangle((111, 58, 145, 88), radius=4, fill=(220, 225, 235, 255))
	draw.rounded_rectangle((116, 38, 140, 64), radius=4, fill=(220, 225, 235, 255))
	draw.ellipse((118, 114, 138, 134), fill=(235, 240, 245, 255))
	return image


def draw_barbarian():
	image, draw = make_canvas((128, 58, 42, 255), (255, 215, 185, 255))
	draw.rounded_rectangle((88, 92, 100, 192), radius=4, fill=(120, 78, 42, 255))
	draw.rounded_rectangle((156, 92, 168, 192), radius=4, fill=(120, 78, 42, 255))
	draw.polygon([(78, 85), (116, 97), (92, 132), (62, 118)], fill=(230, 230, 230, 255))
	draw.polygon([(178, 85), (140, 97), (164, 132), (194, 118)], fill=(230, 230, 230, 255))
	draw.polygon([(128, 52), (90, 108), (108, 108), (84, 166), (128, 124), (172, 166), (148, 108), (166, 108)], fill=(245, 170, 70, 255))
	draw.ellipse((120, 56, 136, 72), fill=(255, 230, 110, 255))
	return image


def draw_assassin():
	image, draw = make_canvas((70, 58, 108, 255), (220, 200, 255, 255))
	draw.polygon([(68, 170), (100, 88), (128, 62), (156, 88), (188, 170), (164, 196), (92, 196)], fill=(38, 38, 50, 255))
	draw.polygon([(94, 168), (110, 116), (128, 98), (146, 116), (162, 168), (128, 190)], fill=(65, 65, 84, 255))
	draw.rounded_rectangle((104, 118, 152, 136), radius=9, fill=(235, 235, 245, 255))
	draw.ellipse((114, 123, 122, 131), fill=(60, 210, 220, 255))
	draw.ellipse((134, 123, 142, 131), fill=(60, 210, 220, 255))
	draw.polygon([(70, 186), (110, 164), (104, 178), (74, 198)], fill=(210, 215, 230, 255))
	draw.polygon([(186, 186), (146, 164), (152, 178), (182, 198)], fill=(210, 215, 230, 255))
	return image


def draw_spearman():
	image, draw = make_canvas((52, 118, 102, 255), (215, 245, 220, 255))
	draw.rounded_rectangle((124, 36, 132, 212), radius=4, fill=(123, 84, 50, 255))
	draw.polygon([(128, 24), (112, 58), (128, 80), (144, 58)], fill=(225, 235, 235, 255))
	draw.ellipse((48, 102, 132, 186), fill=(175, 188, 206, 255))
	draw.ellipse((58, 112, 122, 176), fill=(105, 120, 145, 255))
	draw.line((90, 106, 90, 182), fill=(225, 235, 235, 255), width=4)
	draw.line((52, 144, 128, 144), fill=(225, 235, 235, 255), width=4)
	return image


def save_icon(filename, image):
	image.save(os.path.join(OUTPUT_DIR, filename))


def main():
	icons = {
		"warrior.png": draw_warrior(),
		"barbarian.png": draw_barbarian(),
		"assassin.png": draw_assassin(),
		"spearman.png": draw_spearman(),
	}

	for filename, surface in icons.items():
		save_icon(filename, surface)
		print(f"Создано: {filename}")


if __name__ == "__main__":
	main()
