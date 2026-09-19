import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
const skill='C:/Users/Admin/.codex/plugins/cache/openai-primary-runtime/presentations/26.909.12148/skills/presentations';
const root='C:/Users/Admin/mbca/TP2-3/output/ppt_soft_cover_20260915';
process.env.RUNTIME_NODE_MODULES='C:/Users/Admin/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules';
const {finalizePresentation}=await import(pathToFileURL(path.join(skill,'container_tools/artifact_tool_utils.mjs')).href);
await fs.mkdir(path.join(root,'deliverables'),{recursive:true});
const result=await finalizePresentation({
  workspaceDir:root,
  candidatePath:path.join(root,'제주시_기획서_디자인최종.pptx'),
  finalPath:path.join(root,'deliverables/제주시_기획서_최종.pptx'),
  pythonExecutable:'C:/Users/Admin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe',
  integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),
  layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),
  layoutArgs:['--expected-slide-size-emu','15240000,8572500','--validate-bullet-geometry','--validate-heading-fit',
              ...[10,12,13].flatMap(n=>['--require-native-table-slide',String(n)])],
  requiredNativeChartOwnerSlides:[3,6,9],
  requiredNativeTableOwnerSlides:[10,12,13],
  verifyArtifactToolImport:true,
  receiptPath:path.join(root,'validation.json'),
});
console.log(JSON.stringify(result));













