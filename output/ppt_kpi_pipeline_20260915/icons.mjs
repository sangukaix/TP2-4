import fs from 'node:fs/promises';
import {createRequire} from 'node:module';
const require=createRequire('C:/Users/Admin/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/__icons.cjs');
const sharp=require('sharp');
const root='C:/Users/Admin/mbca/TP2-3/ai_server/assets/proposal_icons';
for(const file of await fs.readdir(root)) {
  if(!file.endsWith('.svg')) continue;
  const source=await fs.readFile(`${root}/${file}`,'utf8');
  for(const [name,color] of [['blue','#004EA2'],['orange','#FF6B00'],['white','#FFFFFF']]) {
    const svg=source.replaceAll('currentColor',color).replace('stroke-width="2"','stroke-width="1.65"');
    await sharp(Buffer.from(svg),{density:384}).resize(256,256).png().toFile(`${root}/${file.slice(0,-4)}-${name}.png`);
  }
}
console.log('Lucide icons prepared locally.');
