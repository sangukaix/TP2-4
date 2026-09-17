import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
const require=createRequire('C:/Users/Admin/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/package.json');
const sharp=require('sharp');
const dir='C:/Users/Admin/mbca/TP2-3/ai_server/assets/proposal_icons';
for(const file of await fs.readdir(dir)){
 if(!file.endsWith('.svg'))continue;
 const svg=(await fs.readFile(path.join(dir,file),'utf8')).replaceAll('currentColor','#F50045');
 await sharp(Buffer.from(svg)).resize(240,240).png().toFile(path.join(dir,file.replace('.svg','-red.png')));
}
