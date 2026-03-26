# HOPrS — Human Oriented Proof System

An open system for proving the originality of, and modifications made to, photographic and video media. HOPrS uses a combination of Merkle trees, QuadTrees, and Perceptual hashing (MQP) to fingerprint images at multiple levels of granularity — making it possible to detect, localise, and characterise edits even across crops, resizes, and partial modifications.

This repository contains the standard specification, tooling, schemas, documentation, and a working web-based POC.

---

## POC Web Service

A Flask web application that lets you encode images into quadtree fingerprints and compare them visually.

### Prerequisites

- Python 3.10+
- `pip`

### Setup

```bash
# 1. Navigate to the web service directory
cd POC/web_service

# 2. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate       # macOS / Linux
# venv\Scripts\activate        # Windows

# 3. Install dependencies
pip install -r requirements.txt
```

### Running

```bash
python main.py
```

Then open [http://localhost:5000](http://localhost:5000) in your browser.

### Optional: Astra DB

The service can store quadtrees in a [DataStax Astra](https://astra.datastax.com) vector database, but this is entirely optional — the app runs fine without it.

To enable it, set these environment variables before starting the server:

```bash
export ASTRA_DB_API_ENDPOINT="https://your-astra-endpoint"
export ASTRA_DB_APPLICATION_TOKEN="AstraCS:your-token-here"
```

Without these, DB Search and DB Management will be unavailable, but Encode, Compare, and Side by Side all work normally.

---

## Using the POC

| Tab | What it does |
|-----|-------------|
| **Encode** | Upload an image to generate its quadtree fingerprint. Downloads a `.qt` file and optionally stores it in the DB. |
| **Side by Side** | Upload two images and compare them directly — no need to generate a quadtree file first. |
| **Compare** | Upload a `.qt` file from a previous encode alongside a new image to compare them. |
| **DB Search** | Search the Astra database for images similar to an uploaded one *(requires Astra DB)*. |
| **DB Management** | List, download, or delete stored quadtrees *(requires Astra DB)*. |

### Suggested starting parameters

| Parameter | Suggested value | Notes |
|-----------|----------------|-------|
| Quadtree depth | `8` | Good for ~4000×3000 (iPhone) images; use `5` for quick tests |
| Threshold (Hamming distance) | `5` | Increase to catch more aggressive edits |

---

## Repository Structure

```
HOPrS/
├── POC/
│   ├── web_service/     # Flask POC application
│   └── README           # POC-specific notes
├── examples/            # Early (abandoned) approach using reversible transforms
└── README.md            # This file
```

---

## Contributing

Algorithmic efficiency, code quality, and storage optimisation have intentionally not been priorities in the POC — there are straightforward orders-of-magnitude improvements available. Contributions are very welcome.