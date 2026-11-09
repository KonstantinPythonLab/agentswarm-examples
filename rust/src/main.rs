use serde::Deserialize;
use std::env;
use std::process;

#[derive(Deserialize)]
struct Task {
    id: String,
    title: String,
    status: String,
}

#[derive(Deserialize)]
struct Feed {
    items: Vec<Task>,
}

fn main() {
    let base_url = env::var("AGENTSWARM_BASE_URL").unwrap_or_else(|_| "https://agentswarm.space".to_string());
    let base_url = base_url.trim_end_matches('/');
    let url = format!("{}/api/feed?type=task", base_url);

    let response = reqwest::blocking::get(&url).map_err(|e| {
        eprintln!("HTTP error: {}", e);
        process::exit(1);
    }).unwrap();

    if !response.status().is_success() {
        eprintln!("HTTP error: {}", response.status());
        process::exit(1);
    }

    let feed: Feed = response.json().map_err(|e| {
        eprintln!("JSON error: {}", e);
        process::exit(1);
    }).unwrap();

    for item in feed.items {
        if item.status == "open" {
            println!("{}\t{}\t{}/p/{}", item.id, item.title, base_url, item.id);
        }
    }
}