use pyo3::prelude::*;
use regex::Regex;
use serde::Deserialize;
use std::collections::{HashMap, HashSet};

const STOP_WORDS: &[&str] = &[
    // English
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "but",
    "by",
    "for",
    "if",
    "in",
    "into",
    "is",
    "it",
    "no",
    "not",
    "of",
    "on",
    "or",
    "such",
    "that",
    "the",
    "their",
    "then",
    "there",
    "these",
    "they",
    "this",
    "to",
    "was",
    "will",
    "with",
    "about",
    "above",
    "after",
    "again",
    "against",
    "all",
    "am",
    "any",
    "because",
    "been",
    "before",
    "being",
    "between",
    "both",
    "did",
    "do",
    "does",
    "doing",
    "down",
    "during",
    "each",
    "few",
    "from",
    "further",
    "had",
    "has",
    "have",
    "having",
    "he",
    "her",
    "here",
    "hers",
    "him",
    "his",
    "how",
    "i",
    "if",
    "into",
    "itself",
    "just",
    "me",
    "more",
    "most",
    "my",
    "myself",
    "now",
    "off",
    "once",
    "only",
    "other",
    "our",
    "ours",
    "ourselves",
    "out",
    "over",
    "own",
    "same",
    "she",
    "should",
    "some",
    "such",
    "than",
    "that",
    "theirs",
    "them",
    "themselves",
    "then",
    "there",
    "these",
    "they",
    "this",
    "those",
    "through",
    "under",
    "until",
    "up",
    "very",
    "we",
    "were",
    "what",
    "when",
    "where",
    "which",
    "while",
    "who",
    "whom",
    "why",
    "you",
    "your",
    "yours",
    "yourself",
    "yourselves",
    // French
    "le",
    "la",
    "les",
    "un",
    "une",
    "des",
    "de",
    "du",
    "et",
    "ou",
    "ne",
    "pas",
    "il",
    "elle",
    "on",
    "nous",
    "vous",
    "ils",
    "elles",
    "ce",
    "ces",
    "à",
    "au",
    "aux",
    "en",
    "dans",
    "sur",
    "par",
    "pour",
    "avec",
    "sans",
    "mais",
    "où",
    "quand",
    "comment",
    "que",
    "qui",
    "quoi",
    "dont",
    "mon",
    "ton",
    "son",
    "ma",
    "ta",
    "sa",
    "mes",
    "tes",
    "ses",
    "notre",
    "votre",
    "leur",
    "nos",
    "vos",
    "je",
    "tu",
    "se",
    "me",
    "te",
    "lui",
    "y",
    "tout",
    "tous",
    "toute",
    "toutes",
    "chaque",
    "plus",
    "moins",
    "aussi",
    "très",
    "bien",
    "mal",
    "si",
    "donc",
    "car",
    "parce",
    "comme",
    "lorsque",
    "depuis",
    "avant",
    "après",
    "pendant",
    "vers",
    "chez",
    "entre",
    "parmi",
    "sous",
    "devant",
    "derrière",
    "contre",
    "malgré",
    "hormis",
    "sauf",
    "selon",
    "voici",
    "voilà",
    "afin",
    "quoique",
    "tandis",
    "alors",
    "jusqu'à",
    "pourvu",
    "à condition",
    "en cas",
    "au lieu de",
    "plutôt",
    "soit",
    "ni",
    "non",
    "seulement",
    "d'ailleurs",
    "outre",
    "enfin",
    "bref",
    "en somme",
    "ainsi",
    "par conséquent",
    "c'est",
    "pourquoi",
    "c'est-à-dire",
    "autrement",
    "dit",
    "par exemple",
    "notamment",
    "surtout",
    "en particulier",
    "quant à",
    "ici",
    "là",
    "même",
    "toujours",
    "jamais",
    "souvent",
    "trop",
    "peut-être",
    "plusieurs",
    "aucun",
    "certains",
    "chacun",
    "quelque",
    "toutefois",
    "néanmoins",
    "or",
    "alors que",
    "depuis que",
    "avant que",
    "après que",
    // French contractions
    "l'",
    "d'",
    "c'",
    "j'",
    "n'",
    "s'",
    "t'",
    "qu'",
];

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

#[pyfunction]
fn extract_keywords(notes_json: &str, top_n: usize) -> PyResult<String> {
    let notes: Vec<Note> = serde_json::from_str(notes_json).map_err(|e| {
        PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Failed to parse JSON: {}", e))
    })?;

    let mut word_counts: HashMap<String, usize> = HashMap::new();
    let re = Regex::new(r"[^a-zA-ZÀ-ÿ\s]").map_err(|e| {
        PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Failed to compile regex: {}", e))
    })?;

    let stop_words_set: HashSet<&str> = STOP_WORDS.iter().cloned().collect();

    for note in notes {
        let lowercased_content = note.content.to_lowercase();
        let contraction_re = Regex::new(r"\b[dlcjntsqu]'").unwrap();
        let without_contractions = contraction_re.replace_all(&lowercased_content, "");
        let cleaned_content = re.replace_all(&without_contractions, "");
        for word in cleaned_content.split_whitespace() {
            if !stop_words_set.contains(word) && word.len() > 1 {
                // Ignore single-character words
                *word_counts.entry(word.to_string()).or_insert(0) += 1;
            }
        }
    }

    let mut sorted_keywords: Vec<(&String, &usize)> = word_counts.iter().collect();
    sorted_keywords.sort_by(|a, b| b.1.cmp(a.1)); // Sort by count, descending

    let top_keywords: Vec<String> = sorted_keywords
        .into_iter()
        .take(top_n)
        .map(|(word, count)| format!("\"{}\": {}", word, count))
        .collect();

    Ok(format!("{{{}}}", top_keywords.join(", ")))
}

#[pymodule]
fn notia_analyzer(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(analyze_notes_content, m)?)?;
    m.add_function(wrap_pyfunction!(extract_keywords, m)?)?;
    Ok(())
}
