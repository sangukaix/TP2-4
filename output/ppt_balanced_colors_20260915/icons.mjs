import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
const require=createRequire('C:/Users/Admin/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/package.json');
const sharp=require('sharp');
const dir='C:/Users/Admin/mbca/TP2-3/ai_server/assets/proposal_icons';
const tones={ocean:'27649B',jade:'187C70',violet:'7556A5',ochre:'A96924',slate:'495565'};
const icons=[['users','ocean'],['coins','jade'],['map-pinned','ocean'],['search-check','violet'],
 ['mouse-pointer-click','slate'],['git-compare-arrows','ocean'],['notebook-pen','ochre'],
 ['shield-check','jade'],['files','slate'],['database','ocean']];
for(const [kind,tone] of icons){
 const svg=(await fs.readFile(path.join(dir,kind+'.svg'),'utf8')).replaceAll('currentColor','#'+tones[tone]);
 await sharp(Buffer.from(svg)).resize(240,240).png().toFile(path.join(dir,`${kind}-${tone}.png`));
}
console.log(`Prepared ${icons.length} color variants from existing Lucide SVGs`);
