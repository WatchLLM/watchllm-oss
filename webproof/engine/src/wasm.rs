//! WebAssembly bindings. JSON is accepted as text so integers are never first
//! rounded by JavaScript; callers control the exact cross-language value.

use wasm_bindgen::prelude::*;

use crate::core::{canonical_bytes, hex, parse_json, JsonValue, MerkleAccumulator};

fn object_from_json(input: &str) -> Result<JsonValue, JsError> {
    let value = parse_json(input).map_err(|error| JsError::new(&error))?;
    if !matches!(value, JsonValue::Object(_)) {
        return Err(JsError::new("record must be a JSON object"));
    }
    Ok(value)
}

#[wasm_bindgen]
pub fn canonical_leaf_json(record_json: &str) -> Result<String, JsError> {
    let value = object_from_json(record_json)?;
    String::from_utf8(canonical_bytes(&value)).map_err(|error| JsError::new(&error.to_string()))
}

#[wasm_bindgen]
pub struct WasmAccumulator {
    inner: MerkleAccumulator,
}

#[wasm_bindgen]
impl WasmAccumulator {
    #[wasm_bindgen(constructor)]
    pub fn new() -> Self {
        Self {
            inner: MerkleAccumulator::new(),
        }
    }

    pub fn append_json(&mut self, record_json: &str) -> Result<(), JsError> {
        let value = object_from_json(record_json)?;
        self.inner.append_canonical(&canonical_bytes(&value));
        Ok(())
    }

    pub fn root_hex(&self) -> String {
        hex(&self.inner.root())
    }

    pub fn leaf_count(&self) -> u64 {
        self.inner.leaf_count()
    }
}

impl Default for WasmAccumulator {
    fn default() -> Self {
        Self::new()
    }
}
