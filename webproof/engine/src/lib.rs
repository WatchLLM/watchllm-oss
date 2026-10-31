//! Deterministic local commitment engine for WatchLLM WebProof.
//!
//! The pure commitment implementation lives in [`core`]. Platform adapters do
//! input conversion only. This crate does not produce TLS proofs, prove remote
//! data, or attest to any server response.

pub mod core;

#[cfg(feature = "python")]
mod python {
    use std::collections::HashSet;
    use std::sync::{Mutex, MutexGuard};

    use pyo3::exceptions::{PyRuntimeError, PyTypeError, PyValueError};
    use pyo3::prelude::*;
    use pyo3::types::{PyBool, PyDict, PyInt, PyList, PyString, PyTuple};

    use crate::core::{canonical_bytes, hex, JsonValue, MerkleAccumulator};

    const MAX_COMMITMENT_DEPTH: usize = 128;

    fn from_python(value: &Bound<'_, PyAny>, path: &str) -> PyResult<JsonValue> {
        from_python_inner(value, path, 0, &mut HashSet::new())
    }

    fn from_python_inner(
        value: &Bound<'_, PyAny>,
        path: &str,
        depth: usize,
        active_containers: &mut HashSet<usize>,
    ) -> PyResult<JsonValue> {
        if depth > MAX_COMMITMENT_DEPTH {
            return Err(PyValueError::new_err(format!(
                "{path}: nesting exceeds the maximum commitment depth of {MAX_COMMITMENT_DEPTH}"
            )));
        }
        if value.is_none() {
            return Ok(JsonValue::Null);
        }
        if value.is_instance_of::<PyBool>() {
            return Ok(JsonValue::Bool(value.extract()?));
        }
        if value.is_instance_of::<PyInt>() {
            return Ok(JsonValue::Integer(value.str()?.to_str()?.to_owned()));
        }
        if value.is_instance_of::<PyString>() {
            return value
                .extract::<String>()
                .map(JsonValue::String)
                .map_err(|_| {
                    PyValueError::new_err(format!(
                        "{path}: strings may not contain lone surrogates"
                    ))
                });
        }
        if let Ok(dict) = value.downcast::<PyDict>() {
            let identity = dict.as_ptr() as usize;
            if !active_containers.insert(identity) {
                return Err(PyValueError::new_err(format!(
                    "{path}: circular references are not supported"
                )));
            }
            let result = (|| {
                let mut entries = Vec::with_capacity(dict.len());
                for (key, child) in dict.iter() {
                    let key = key.downcast::<PyString>().map_err(|_| {
                        PyTypeError::new_err(format!("{path}: object keys must be strings"))
                    })?;
                    let key = key.extract::<String>().map_err(|_| {
                        PyValueError::new_err(format!(
                            "{path}: object keys may not contain lone surrogates"
                        ))
                    })?;
                    let child_path = format!("{path}.{key}");
                    entries.push((
                        key,
                        from_python_inner(&child, &child_path, depth + 1, active_containers)?,
                    ));
                }
                Ok(JsonValue::Object(entries))
            })();
            active_containers.remove(&identity);
            return result;
        }
        if let Ok(list) = value.downcast::<PyList>() {
            return from_sequence(
                value,
                list.iter(),
                list.len(),
                path,
                depth,
                active_containers,
            );
        }
        if let Ok(tuple) = value.downcast::<PyTuple>() {
            return from_sequence(
                value,
                tuple.iter(),
                tuple.len(),
                path,
                depth,
                active_containers,
            );
        }

        Err(PyTypeError::new_err(format!(
            "{path}: unsupported value type {}; expected JSON-safe null, bool, int, str, list, tuple, or string-keyed dict",
            value.get_type().name()?
        )))
    }

    fn from_sequence<'py>(
        value: &Bound<'py, PyAny>,
        children: impl Iterator<Item = Bound<'py, PyAny>>,
        len: usize,
        path: &str,
        depth: usize,
        active_containers: &mut HashSet<usize>,
    ) -> PyResult<JsonValue> {
        let identity = value.as_ptr() as usize;
        if !active_containers.insert(identity) {
            return Err(PyValueError::new_err(format!(
                "{path}: circular references are not supported"
            )));
        }
        let result = children
            .enumerate()
            .map(|(index, child)| {
                from_python_inner(
                    &child,
                    &format!("{path}[{index}]"),
                    depth + 1,
                    active_containers,
                )
            })
            .collect::<PyResult<Vec<_>>>()
            .map(JsonValue::Array);
        active_containers.remove(&identity);
        debug_assert!(result.as_ref().map_or(true, |values| match values {
            JsonValue::Array(values) => values.len() == len,
            _ => false,
        }));
        result
    }

    #[derive(Default)]
    struct State {
        accumulator: MerkleAccumulator,
        records: Vec<Vec<u8>>,
    }

    #[pyclass(module = "watchllm_webproof._native")]
    struct NativeAccumulator {
        state: Mutex<State>,
    }

    impl NativeAccumulator {
        fn locked(&self) -> PyResult<MutexGuard<'_, State>> {
            self.state
                .lock()
                .map_err(|_| PyRuntimeError::new_err("native accumulator lock poisoned"))
        }
    }

    #[pymethods]
    impl NativeAccumulator {
        #[new]
        fn new() -> Self {
            Self {
                state: Mutex::new(State::default()),
            }
        }

        fn record(&self, record: &Bound<'_, PyAny>) -> PyResult<()> {
            let value = from_python(record, "$record")?;
            if !matches!(value, JsonValue::Object(_)) {
                return Err(PyTypeError::new_err(
                    "$record: record must be a mapping/dict",
                ));
            }
            let canonical = canonical_bytes(&value);
            let mut state = self.locked()?;
            state.accumulator.append_canonical(&canonical);
            state.records.push(canonical);
            Ok(())
        }

        fn records_json(&self) -> PyResult<Vec<Vec<u8>>> {
            Ok(self.locked()?.records.clone())
        }

        fn proof<'py>(&self, py: Python<'py>, session_id: &str) -> PyResult<Bound<'py, PyDict>> {
            let state = self.locked()?;
            let result = PyDict::new(py);
            result.set_item("proof_type", "local_merkle_stub")?;
            result.set_item("proof_version", "1.0.0")?;
            result.set_item("attestation", false)?;
            result.set_item("algorithm", "sha256-local-merkle-v1")?;
            result.set_item("aggregation_enabled", true)?;
            result.set_item("merkle_root", hex(&state.accumulator.root()))?;
            result.set_item("leaf_count", state.accumulator.leaf_count())?;
            result.set_item("session_id", session_id)?;
            Ok(result)
        }
    }

    #[pyfunction]
    fn canonical_leaf(record: &Bound<'_, PyAny>) -> PyResult<Vec<u8>> {
        Ok(canonical_bytes(&from_python(record, "$record")?))
    }

    #[pymodule]
    fn _native(module: &Bound<'_, PyModule>) -> PyResult<()> {
        module.add_class::<NativeAccumulator>()?;
        module.add_function(wrap_pyfunction!(canonical_leaf, module)?)?;
        Ok(())
    }
}

#[cfg(feature = "wasm")]
mod wasm;
