from PIL import Image, ImageOps, ImageDraw
from pathlib import Path
r=Path(__file__).parent/'reference'
files=sorted(r.glob('slide-*.png'))
for n in range(2):
    im=Image.new('RGB',(1280,1000),'white')
    for i,p in enumerate(files[n*16:(n+1)*16]):
        im.paste(ImageOps.contain(Image.open(p),(320,225)),((i%4)*320,(i//4)*250))
        ImageDraw.Draw(im).text(((i%4)*320+8,(i//4)*250+227),str(n*16+i+1),fill='black')
    im.save(r/f'contact-{n+1}.png')
