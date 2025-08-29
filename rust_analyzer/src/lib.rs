use pyo3::prelude::*;
use serde::Deserialize;
use std::collections::HashSet;

#[derive(Deserialize, Debug)]
struct Note {
    id: String,
    content: String,
    project: String,
}

#[pyfunction]
fn analyze_notes_content(notes_json: &str) -> PyResult<String> {
    let notes: Vec<Note> = serde_json::from_str(notes_json).map_err(|e| {
        PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Failed to parse JSON: {}", e))
    })?;

    let mut total_words = 0;
    let mut unique_projects = HashSet::new();

    for note in &notes {
        total_words += note.content.split_whitespace().count();
        if !note.project.is_empty() {
            unique_projects.insert(&note.project);
        }
        let _ = &note.id;
    }

    let analysis_result = format!(
        "Analyzed {} notes. Total word count: {}. Found {} unique projects.",
        notes.len(),
        total_words,
        unique_projects.len()
    );

    Ok(analysis_result)
}

#[pymodule]
fn notia_analyzer(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(analyze_notes_content, m)?)?;
    Ok(())
}
