# Placeholder icon for player info button (32x32 px)
from PIL import Image, ImageDraw
img = Image.new('RGBA', (32, 32), (0,0,0,0))
draw = ImageDraw.Draw(img)
draw.ellipse((4,4,28,28), fill=(200,200,200,255), outline=(80,80,80,255), width=2)
draw.ellipse((10,10,22,22), fill=(120,120,120,255))
draw.rectangle((8,20,24,28), fill=(180,180,180,255))
img.save('assets/images/player_info_icon.png')
