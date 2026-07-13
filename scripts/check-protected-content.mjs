import { spawnSync } from "node:child_process";

const base = process.argv[2] ?? "origin/main";
const protectedPaths = ["src/content/posts", "public/images"];
const diff = spawnSync(
  "git",
  ["diff", "--name-status", "--find-renames", `${base}...HEAD`, "--", ...protectedPaths],
  { encoding: "utf8" },
);

if (diff.status !== 0) {
  process.stderr.write(diff.stderr || diff.stdout);
  throw new Error(`Could not compare protected content with ${base}.`);
}

const changes = diff.stdout
  .split("\n")
  .map((line) => line.trim())
  .filter(Boolean);
const blocked = changes.filter((line) => !line.startsWith("A\t"));

if (blocked.length > 0) {
  throw new Error(
    [
      "Protected historical content was modified, deleted, renamed, copied, or type-changed.",
      "A publishing pull request may add new posts and images only:",
      ...blocked.map((line) => `- ${line}`),
    ].join("\n"),
  );
}

console.log(
  changes.length === 0
    ? `Protected content verified against ${base}: no post or image changes.`
    : `Protected content verified against ${base}: ${changes.length} addition(s), no historical changes or deletions.`,
);
