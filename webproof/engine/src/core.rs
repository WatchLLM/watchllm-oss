//! Pure, platform-independent commitment primitives.

use std::fmt::Write as _;

use sha2::{Digest, Sha256};

pub const LEAF_DOMAIN: &[u8] = b"watchllm-webproof-local-leaf-v1\0";
pub const NODE_DOMAIN: &[u8] = b"watchllm-webproof-local-node-v1\0";
pub const EMPTY_ROOT: [u8; 32] = [
    0xe3, 0xb0, 0xc4, 0x42, 0x98, 0xfc, 0x1c, 0x14, 0x9a, 0xfb, 0xf4, 0xc8, 0x99, 0x6f, 0xb9, 0x24,
    0x27, 0xae, 0x41, 0xe4, 0x64, 0x9b, 0x93, 0x4c, 0xa4, 0x95, 0x99, 0x1b, 0x78, 0x52, 0xb8, 0x55,
];

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum JsonValue {
    Null,
    Bool(bool),
    Integer(String),
    String(String),
    Array(Vec<JsonValue>),
    Object(Vec<(String, JsonValue)>),
}

pub fn write_json_string(value: &str, output: &mut String) {
    output.push('"');
    for character in value.chars() {
        match character {
            '"' => output.push_str("\\\""),
            '\\' => output.push_str("\\\\"),
            '\u{08}' => output.push_str("\\b"),
            '\u{0c}' => output.push_str("\\f"),
            '\n' => output.push_str("\\n"),
            '\r' => output.push_str("\\r"),
            '\t' => output.push_str("\\t"),
            character if character <= '\u{1f}' => {
                write!(output, "\\u{:04x}", character as u32)
                    .expect("writing to String cannot fail");
            }
            character if character.is_ascii() => output.push(character),
            character if (character as u32) <= 0xffff => {
                write!(output, "\\u{:04x}", character as u32)
                    .expect("writing to String cannot fail");
            }
            character => {
                let scalar = character as u32 - 0x1_0000;
                let high = 0xd800 + (scalar >> 10);
                let low = 0xdc00 + (scalar & 0x3ff);
                write!(output, "\\u{high:04x}\\u{low:04x}").expect("writing to String cannot fail");
            }
        }
    }
    output.push('"');
}

pub fn canonical_bytes(value: &JsonValue) -> Vec<u8> {
    fn write_value(value: &JsonValue, output: &mut String) {
        match value {
            JsonValue::Null => output.push_str("null"),
            JsonValue::Bool(value) => output.push_str(if *value { "true" } else { "false" }),
            JsonValue::Integer(value) => output.push_str(value),
            JsonValue::String(value) => write_json_string(value, output),
            JsonValue::Array(values) => {
                output.push('[');
                for (index, value) in values.iter().enumerate() {
                    if index != 0 {
                        output.push(',');
                    }
                    write_value(value, output);
                }
                output.push(']');
            }
            JsonValue::Object(entries) => {
                output.push('{');
                let mut sorted: Vec<_> = entries.iter().collect();
                sorted.sort_by(|left, right| left.0.cmp(&right.0));
                for (index, (key, value)) in sorted.into_iter().enumerate() {
                    if index != 0 {
                        output.push(',');
                    }
                    write_json_string(key, output);
                    output.push(':');
                    write_value(value, output);
                }
                output.push('}');
            }
        }
    }

    let mut output = String::new();
    write_value(value, &mut output);
    output.into_bytes()
}

pub fn leaf_hash(canonical: &[u8]) -> [u8; 32] {
    Sha256::new()
        .chain_update(LEAF_DOMAIN)
        .chain_update(canonical)
        .finalize()
        .into()
}

pub fn node_hash(left: [u8; 32], right: [u8; 32]) -> [u8; 32] {
    Sha256::new()
        .chain_update(NODE_DOMAIN)
        .chain_update(left)
        .chain_update(right)
        .finalize()
        .into()
}

pub fn hex(bytes: &[u8]) -> String {
    let mut output = String::with_capacity(bytes.len() * 2);
    for byte in bytes {
        write!(output, "{byte:02x}").expect("writing to String cannot fail");
    }
    output
}

/// Incremental representation of the historical level-by-level Merkle tree.
///
/// `frontier[level]` is the complete rightmost subtree of `2^level` leaves
/// represented by that set bit in `leaf_count`. Append is binary carry. Root
/// folds right-to-left, self-hashing the incomplete right subtree at each
/// missing level; this is exactly the historical odd-node duplication rule.
#[derive(Debug, Clone, Default)]
pub struct MerkleAccumulator {
    frontier: Vec<Option<[u8; 32]>>,
    leaf_count: u64,
}

impl MerkleAccumulator {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn append_canonical(&mut self, canonical: &[u8]) {
        self.append_hash(leaf_hash(canonical));
    }

    pub fn append_hash(&mut self, mut carry: [u8; 32]) {
        let mut level = 0;
        loop {
            if level == self.frontier.len() {
                self.frontier.push(Some(carry));
                break;
            }
            match self.frontier[level].take() {
                None => {
                    self.frontier[level] = Some(carry);
                    break;
                }
                Some(left) => carry = node_hash(left, carry),
            }
            level += 1;
        }
        self.leaf_count = self
            .leaf_count
            .checked_add(1)
            .expect("Merkle leaf count exceeds u64::MAX");
    }

    pub fn leaf_count(&self) -> u64 {
        self.leaf_count
    }

    pub fn root(&self) -> [u8; 32] {
        let mut right: Option<([u8; 32], usize)> = None;
        for (level, left) in self.frontier.iter().enumerate() {
            let Some(left) = left else { continue };
            right = Some(match right {
                None => (*left, level),
                Some((mut hash, mut height)) => {
                    while height < level {
                        hash = node_hash(hash, hash);
                        height += 1;
                    }
                    (node_hash(*left, hash), level + 1)
                }
            });
        }
        right.map_or(EMPTY_ROOT, |(hash, _)| hash)
    }
}

#[cfg(feature = "json")]
pub fn parse_json(input: &str) -> Result<JsonValue, String> {
    fn convert(value: serde_json::Value) -> Result<JsonValue, String> {
        match value {
            serde_json::Value::Null => Ok(JsonValue::Null),
            serde_json::Value::Bool(value) => Ok(JsonValue::Bool(value)),
            serde_json::Value::Number(value) => {
                let decimal = value.to_string();
                if decimal
                    .bytes()
                    .all(|byte| byte == b'-' || byte.is_ascii_digit())
                {
                    Ok(JsonValue::Integer(decimal))
                } else {
                    Err("floating-point numbers are outside the commitment contract".into())
                }
            }
            serde_json::Value::String(value) => Ok(JsonValue::String(value)),
            serde_json::Value::Array(values) => values
                .into_iter()
                .map(convert)
                .collect::<Result<_, _>>()
                .map(JsonValue::Array),
            serde_json::Value::Object(entries) => entries
                .into_iter()
                .map(|(key, value)| Ok((key, convert(value)?)))
                .collect::<Result<_, String>>()
                .map(JsonValue::Object),
        }
    }

    let value = serde_json::from_str(input).map_err(|error| error.to_string())?;
    convert(value)
}
