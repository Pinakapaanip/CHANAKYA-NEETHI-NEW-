from PIL import Image
import os

SRC_DIR = os.path.join('assets', 'player')
DST_DIR = os.path.join('assets', 'player', 'processed')

os.makedirs(DST_DIR, exist_ok=True)

for fname in os.listdir(SRC_DIR):
    if fname.endswith('.jpeg'):
        src_path = os.path.join(SRC_DIR, fname)
        dst_path = os.path.join(DST_DIR, fname.replace('.jpeg', '.png'))
        img = Image.open(src_path).convert('RGBA')
        datas = img.getdata()
        newData = []
        for item in datas:
            # Remove white or black backgrounds
            if (item[0] > 240 and item[1] > 240 and item[2] > 240) or (item[0] < 15 and item[1] < 15 and item[2] < 15):
                newData.append((255, 255, 255, 0))
            else:
                newData.append(item)
        img.putdata(newData)
        img.save(dst_path)
        print(f"Processed {fname} -> {dst_path}")
