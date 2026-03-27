from PIL import Image
import os

# Remove background for merchant and archer images
NPCS = [
    ('assets/npcs/merchant.jpeg', 'assets/npcs/merchant.png'),
]
ENEMIES = [
    ('assets/enemies/archer_walk_01.jpeg', 'assets/enemies/archer_walk_01.png'),
    ('assets/enemies/archer_walk_02.jpeg', 'assets/enemies/archer_walk_02.png'),
    ('assets/enemies/archer_shoot_01.jpeg', 'assets/enemies/archer_shoot_01.png'),
    ('assets/enemies/archer_hurt.jpeg', 'assets/enemies/archer_hurt.png'),
    ('assets/enemies/archer_death.jpeg', 'assets/enemies/archer_death.png'),
]

def remove_bg(src, dst):
    img = Image.open(src).convert('RGBA')
    datas = img.getdata()
    newData = []
    for item in datas:
        # Remove white or black backgrounds
        if (item[0] > 240 and item[1] > 240 and item[2] > 240) or (item[0] < 15 and item[1] < 15 and item[2] < 15):
            newData.append((255, 255, 255, 0))
        else:
            newData.append(item)
    img.putdata(newData)
    img.save(dst)
    print(f"Processed {src} -> {dst}")

for src, dst in NPCS + ENEMIES:
    if os.path.exists(src):
        remove_bg(src, dst)
