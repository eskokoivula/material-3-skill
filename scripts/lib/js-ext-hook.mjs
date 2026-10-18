// Node resolve hook. The color library's npm build (0.4.0) imports two of its own files without the ".js"
// ending, which plain Node cannot resolve; retry such relative imports with ".js".
export async function resolve(specifier, context, nextResolve) {
  try {
    return await nextResolve(specifier, context);
  } catch (err) {
    if (err?.code === 'ERR_MODULE_NOT_FOUND' && /^\.\.?\//.test(specifier) && !specifier.endsWith('.js')) {
      return nextResolve(`${specifier}.js`, context);
    }
    throw err;
  }
}
