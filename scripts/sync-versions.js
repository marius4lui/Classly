#!/usr/bin/env node
'use strict';

/**
 * Sync versioned docs from /versions/<version>/README.md into /docs/<version>/index.md
 * and update VitePress nav dropdown ("Versionen") in docs/.vitepress/config.mts.
 *
 * Design goals:
 * - deterministic output for CI
 * - no extra dependencies
 * - only imports README.md (ignores everything else)
 */

const fs = require('fs/promises');
const path = require('path');

const REPO_ROOT = path.resolve(__dirname, '..');
const VERSIONS_DIR = path.join(REPO_ROOT, 'versions');
const DOCS_DIR = path.join(REPO_ROOT, 'docs');
const VITEPRESS_CONFIG = path.join(DOCS_DIR, '.vitepress', 'config.mts');
const DOCS_VERSIONS_DIR = path.join(DOCS_DIR, 'versions');

// "versions/<dirName>/README.md" is treated as a published version snapshot.

function parseSemverLoose(v) {
  // v: "v1.2.3" or "v1.2.3-rc.1"
  const s = v.startsWith('v') ? v.slice(1) : v;
  const m = s.match(/^(\d+)\.(\d+)\.(\d+)(?:[-+].*)?$/);
  if (!m) return null;
  return { major: Number(m[1]), minor: Number(m[2]), patch: Number(m[3]) };
}

function compareVersionsDesc(a, b) {
  const pa = parseSemverLoose(a);
  const pb = parseSemverLoose(b);
  if (!pa || !pb) return a < b ? 1 : a > b ? -1 : 0;
  if (pa.major !== pb.major) return pb.major - pa.major;
  if (pa.minor !== pb.minor) return pb.minor - pa.minor;
  if (pa.patch !== pb.patch) return pb.patch - pa.patch;
  // Fallback: stable sort by string (descending) for pre-release build metadata
  return a < b ? 1 : a > b ? -1 : 0;
}

async function fileExists(p) {
  try {
    await fs.access(p);
    return true;
  } catch {
    return false;
  }
}

async function ensureDir(p) {
  await fs.mkdir(p, { recursive: true });
}

function findMatchingBracket(str, openIdx, openChar, closeChar) {
  let depth = 0;
  let inSingle = false;
  let inDouble = false;
  let inTemplate = false;
  let inLineComment = false;
  let inBlockComment = false;

  for (let i = openIdx; i < str.length; i++) {
    const ch = str[i];
    const next = i + 1 < str.length ? str[i + 1] : '';

    if (inLineComment) {
      if (ch === '\n') inLineComment = false;
      continue;
    }
    if (inBlockComment) {
      if (ch === '*' && next === '/') {
        inBlockComment = false;
        i++;
      }
      continue;
    }

    if (!inSingle && !inDouble && !inTemplate) {
      if (ch === '/' && next === '/') {
        inLineComment = true;
        i++;
        continue;
      }
      if (ch === '/' && next === '*') {
        inBlockComment = true;
        i++;
        continue;
      }
    }

    if (!inDouble && !inTemplate && ch === "'" && str[i - 1] !== '\\') {
      inSingle = !inSingle;
      continue;
    }
    if (!inSingle && !inTemplate && ch === '"' && str[i - 1] !== '\\') {
      inDouble = !inDouble;
      continue;
    }
    if (!inSingle && !inDouble && ch === '`' && str[i - 1] !== '\\') {
      inTemplate = !inTemplate;
      continue;
    }

    if (inSingle || inDouble || inTemplate) continue;

    if (ch === openChar) depth++;
    if (ch === closeChar) {
      depth--;
      if (depth === 0) return i;
    }
  }

  return -1;
}

function extractArrayLiteral(source, key) {
  const keyIdx = source.indexOf(key);
  if (keyIdx === -1) return null;
  const bracketIdx = source.indexOf('[', keyIdx);
  if (bracketIdx === -1) return null;
  const closeIdx = findMatchingBracket(source, bracketIdx, '[', ']');
  if (closeIdx === -1) return null;
  return { start: bracketIdx, end: closeIdx, text: source.slice(bracketIdx, closeIdx + 1) };
}

function findObjectLiteralRangeContainingText(source, arrayStartIdx, arrayEndIdx, needleRe) {
  const slice = source.slice(arrayStartIdx, arrayEndIdx + 1);
  const m = slice.match(needleRe);
  if (!m || typeof m.index !== 'number') return null;
  const absoluteIdx = arrayStartIdx + m.index;

  // Walk backwards to nearest '{' that starts this object (best-effort).
  let openIdx = -1;
  for (let i = absoluteIdx; i >= arrayStartIdx; i--) {
    if (source[i] === '{') {
      openIdx = i;
      break;
    }
  }
  if (openIdx === -1) return null;
  const closeIdx = findMatchingBracket(source, openIdx, '{', '}');
  if (closeIdx === -1 || closeIdx > arrayEndIdx) return null;
  // Include leading indentation so we can normalize formatting when rewriting.
  const lineStart = source.lastIndexOf('\n', openIdx);
  const start = lineStart === -1 ? openIdx : lineStart + 1;
  return { start, end: closeIdx };
}

function buildVersionsNavItem(versions) {
  const items = versions
    .map((v) => {
      // Folder names may include spaces/parentheses etc.; VitePress routes are URL paths.
      const link = encodeURI(`/versions/${v}/`);
      return `                    { text: '${v}', link: '${link}' }`;
    })
    .join(',\n');
  return [
    "            {",
    "                text: 'Versionen',",
    "                items: [",
    items || "                    // (keine Versionen gefunden)",
    "                ]",
    "            }",
  ].join('\n');
}

async function syncReadmes() {
  if (!(await fileExists(VERSIONS_DIR))) {
    console.warn(`[sync-versions] Skip: missing directory ${path.relative(REPO_ROOT, VERSIONS_DIR)}`);
    return [];
  }

  const entries = await fs.readdir(VERSIONS_DIR, { withFileTypes: true });
  const versions = [];

  for (const ent of entries) {
    if (!ent.isDirectory()) continue;
    const dirName = ent.name;

    const readme = path.join(VERSIONS_DIR, dirName, 'README.md');
    if (!(await fileExists(readme))) continue;

    const outDir = path.join(DOCS_VERSIONS_DIR, dirName);
    const outFile = path.join(outDir, 'index.md');

    await ensureDir(outDir);
    await fs.copyFile(readme, outFile);

    versions.push(dirName);
  }

  versions.sort(compareVersionsDesc);
  return versions;
}

async function updateVitepressNav(versions) {
  if (!(await fileExists(VITEPRESS_CONFIG))) {
    console.warn(`[sync-versions] Skip: missing ${path.relative(REPO_ROOT, VITEPRESS_CONFIG)}`);
    return;
  }

  const original = await fs.readFile(VITEPRESS_CONFIG, 'utf8');
  const navArr = extractArrayLiteral(original, 'nav:');
  if (!navArr) {
    console.warn(`[sync-versions] Skip: could not locate themeConfig.nav array in ${path.relative(REPO_ROOT, VITEPRESS_CONFIG)}`);
    return;
  }

  const versionItem = buildVersionsNavItem(versions);
  const existingRange = findObjectLiteralRangeContainingText(
    original,
    navArr.start,
    navArr.end,
    /text\s*:\s*['"]Versionen['"]/
  );

  let updated = original;
  if (existingRange) {
    updated =
      original.slice(0, existingRange.start) +
      versionItem +
      original.slice(existingRange.end + 1);
  } else {
    // Insert before the closing bracket of nav array.
    const insertPos = navArr.end; // right before ']'
    const insertion = ',\n' + versionItem + '\n';

    updated = original.slice(0, insertPos) + insertion + original.slice(insertPos);
  }

  if (updated !== original) {
    await fs.writeFile(VITEPRESS_CONFIG, updated, 'utf8');
  }
}

async function main() {
  const versions = await syncReadmes();
  await updateVitepressNav(versions);

  process.stdout.write(
    `[sync-versions] Synced versions: ${versions.length ? versions.join(', ') : '(none)'}\n`
  );
}

main().catch((err) => {
  console.error('[sync-versions] Failed:', err && err.stack ? err.stack : err);
  process.exitCode = 1;
});
