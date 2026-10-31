use _native::core::{
    canonical_bytes, hex, leaf_hash, node_hash, JsonValue, MerkleAccumulator, NODE_DOMAIN,
};
use proptest::prelude::*;
use serde_json::Value;
use sha2::{Digest, Sha256};

fn reference_root(leaves: &[[u8; 32]]) -> [u8; 32] {
    if leaves.is_empty() {
        return Sha256::digest([]).into();
    }
    let mut level = leaves.to_vec();
    while level.len() > 1 {
        if level.len() % 2 == 1 {
            level.push(*level.last().unwrap());
        }
        level = level
            .chunks_exact(2)
            .map(|pair| node_hash(pair[0], pair[1]))
            .collect();
    }
    level[0]
}

#[test]
fn canonicalizes_python_compatible_ascii_json() {
    let value = JsonValue::Object(vec![
        ("z".into(), JsonValue::Null),
        (
            "a".into(),
            JsonValue::Array(vec![
                JsonValue::Bool(true),
                JsonValue::Integer("-2".into()),
                JsonValue::String("é😀\n".into()),
            ]),
        ),
    ]);
    assert_eq!(
        String::from_utf8(canonical_bytes(&value)).unwrap(),
        r#"{"a":[true,-2,"\u00e9\ud83d\ude00\n"],"z":null}"#
    );
}

#[test]
fn odd_levels_duplicate_the_last_node() {
    let leaves = [leaf_hash(b"a"), leaf_hash(b"b"), leaf_hash(b"c")];
    let first: [u8; 32] = Sha256::new()
        .chain_update(NODE_DOMAIN)
        .chain_update(leaves[0])
        .chain_update(leaves[1])
        .finalize()
        .into();
    let second = node_hash(leaves[2], leaves[2]);
    assert_eq!(reference_root(&leaves), node_hash(first, second));
}

#[test]
fn odd_duplication_matches_historical_rebuild_across_multiple_levels() {
    let mut accumulator = MerkleAccumulator::new();
    let mut leaves = Vec::new();
    for index in 0..65 {
        let record = format!("record-{index}");
        accumulator.append_canonical(record.as_bytes());
        leaves.push(leaf_hash(record.as_bytes()));
        assert_eq!(accumulator.root(), reference_root(&leaves));
    }
}

#[test]
fn deterministic_vectors_match_at_every_incremental_prefix() {
    let vectors: Value =
        serde_json::from_str(include_str!("../../tests/vectors/commitment-v1.json")).unwrap();
    for vector in vectors["vectors"].as_array().unwrap() {
        let canonical = vector["canonical"].as_array().unwrap();
        let mut accumulator = MerkleAccumulator::new();
        let mut leaves = Vec::new();
        for record in canonical {
            let bytes = record.as_str().unwrap().as_bytes();
            accumulator.append_canonical(bytes);
            leaves.push(leaf_hash(bytes));
            assert_eq!(accumulator.root(), reference_root(&leaves));
        }
        assert_eq!(
            hex(&accumulator.root()),
            vector["merkle_root"].as_str().unwrap()
        );
    }
}

proptest! {
    #[test]
    fn incremental_root_matches_historical_rebuild(
        records in prop::collection::vec(prop::collection::vec(any::<u8>(), 0..128), 0..256)
    ) {
        let mut accumulator = MerkleAccumulator::new();
        let mut leaves = Vec::new();
        for record in records {
            accumulator.append_canonical(&record);
            leaves.push(leaf_hash(&record));
        }
        prop_assert_eq!(accumulator.root(), reference_root(&leaves));
        prop_assert_eq!(accumulator.leaf_count() as usize, leaves.len());
    }

    #[test]
    fn canonical_object_order_is_deterministic(
        mut entries in prop::collection::vec(("[a-z]{1,8}", any::<i64>()), 0..30)
    ) {
        entries.sort_by(|left, right| left.0.cmp(&right.0));
        entries.dedup_by(|left, right| left.0 == right.0);
        let forward = JsonValue::Object(entries.iter().map(|(key, value)| {
            (key.clone(), JsonValue::Integer(value.to_string()))
        }).collect());
        let reverse = JsonValue::Object(entries.iter().rev().map(|(key, value)| {
            (key.clone(), JsonValue::Integer(value.to_string()))
        }).collect());
        prop_assert_eq!(canonical_bytes(&forward), canonical_bytes(&reverse));
    }
}
