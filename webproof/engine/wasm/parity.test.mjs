import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

import wasm from "./pkg/_native.js";

const vectors = JSON.parse(
  await readFile(new URL("../../tests/vectors/commitment-v1.json", import.meta.url)),
);

for (const vector of vectors.vectors) {
  test(`native/Python/WASM vector parity: ${vector.name}`, () => {
    const accumulator = new wasm.WasmAccumulator();
    assert.equal(accumulator.root_hex(), vectors.vectors[0].merkle_root);
    vector.canonical.forEach((source) => {
      assert.equal(wasm.canonical_leaf_json(source), source);
      accumulator.append_json(source);
    });
    assert.equal(Number(accumulator.leaf_count()), vector.records.length);
    assert.equal(accumulator.root_hex(), vector.merkle_root);
    accumulator.free();
  });
}

test("WASM preserves integers beyond JavaScript's safe numeric range from JSON text", () => {
  const source = '{"integer":9007199254740993}';
  assert.equal(wasm.canonical_leaf_json(source), source);
});

test("WASM rejects floating-point records", () => {
  assert.throws(() => wasm.canonical_leaf_json('{"value":1.5}'), /floating-point/);
});
