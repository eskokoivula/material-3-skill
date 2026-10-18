// Google's material-color-utilities, loaded through the resolve hook (see js-ext-hook.mjs).
import { register } from 'node:module';

register('./js-ext-hook.mjs', import.meta.url);
const mcu = await import('@material/material-color-utilities');
export default mcu;
