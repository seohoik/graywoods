import { spawnSync } from "node:child_process";
import { randomUUID } from "node:crypto";
import { access, readFile, readdir, rm, stat, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const runId = `${process.pid}-${randomUUID().slice(0, 12)}`;
const slug = `draft-safety-check-${runId}`;
const sentinel = `DRAFT_SAFETY_SENTINEL_${runId}`;
const fixturePath = path.join(root, "src", "content", "posts", `${slug}.md`);
const routePath = path.join(root, "dist", "posts", slug, "index.html");
const distPath = path.join(root, "dist");

async function exists(target) {
  try {
    await access(target);
    return true;
  } catch {
    return false;
  }
}

async function walk(directory) {
  const files = [];
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    const target = path.join(directory, entry.name);
    if (entry.isDirectory()) files.push(...(await walk(target)));
    if (entry.isFile()) files.push(target);
  }
  return files;
}

let fixtureCreated = false;
try {
  await writeFile(
    fixturePath,
    `---\ntitle: ${sentinel}\npubDate: 2099-01-01\ndescription: ${sentinel}\ndraft: true\ntags:\n  - ${slug}\n---\n\n${sentinel}\n`,
    { encoding: "utf8", flag: "wx" },
  );
  fixtureCreated = true;

  const build = spawnSync(process.platform === "win32" ? "npm.cmd" : "npm", ["run", "build"], {
    cwd: root,
    env: { ...process.env, ASTRO_TELEMETRY_DISABLED: "1" },
    stdio: "inherit",
  });

  if (build.status !== 0) {
    throw new Error(`Build failed with exit code ${build.status ?? "unknown"}.`);
  }

  const leaks = [];
  if (await exists(routePath)) leaks.push(path.relative(root, routePath));

  for (const file of await walk(distPath)) {
    const metadata = await stat(file);
    if (metadata.size > 20 * 1024 * 1024) continue;
    const contents = await readFile(file);
    if (contents.includes(Buffer.from(sentinel)) || contents.includes(Buffer.from(slug))) {
      leaks.push(path.relative(root, file));
    }
  }

  const uniqueLeaks = [...new Set(leaks)].sort();
  if (uniqueLeaks.length > 0) {
    throw new Error(`Draft content leaked into build output:\n${uniqueLeaks.map((file) => `- ${file}`).join("\n")}`);
  }

  console.log("Draft safety verified: no draft route, tag, RSS, sitemap, or search output was generated.");
} finally {
  if (fixtureCreated) await rm(fixturePath);
}
