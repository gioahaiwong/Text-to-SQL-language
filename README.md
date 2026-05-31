<p align="left">
    <br>
    <img src="https://raw.githubusercontent.com/RUCKBReasoning/RESDSQL/main/resdsql.png" width="700"/>
    <br>
</p>

# RESDSQL Text-to-SQL Implementation (80.00% Accuracy)

This project is a localized and optimized implementation of **RESDSQL** (AAAI 2023), focusing on high-accuracy Text-to-SQL conversion using T5-Large and Execution-guided Decoding.

## Quick Start (Streamlit Demo)
1. Install dependencies: `pip install -r requirements.txt`
2. Download models and data (see links below).
3. Run the explorer: `streamlit run streamlit_demo.py`

## Download Links
To run this project, you need to download the models and data from the official RESDSQL release:

| Resource | Description | Link |
|----------|-------------|------|
| **Classifier** | `text2natsql_schema_item_classifier` | [Google Drive](https://drive.google.com/file/d/1UWNj1ZADfKa1G5I4gBYCJeEQO6piMg4G/view?usp=share_link) |
| **T5 Model** | `text2natsql-t5-large` | [Google Drive](https://drive.google.com/file/d/1ZwFsH24_qKC3xwYdedPi6T_8argguWHe/view?usp=sharing) |
| **Data** | Spider Dataset | [data](https://drive.google.com/file/d/19tsgBGAxpagULSl9r85IFKIZb4kyBGGu/view?usp=sharing) |
| **Database** | SQLite Databases | [database](https://drive.google.com/file/d/1s4ItreFlTa8rUdzwVRmUR2Q9AHnxbNjo/view?usp=share_link) |

### Setup Instructions:
1. Place the **Classifier** weights in `models/classifier/`.
2. Place the **T5 Model** weights in `text2natsql-t5-large/`.
3. Unzip **Data** into `data/`.
4. Unzip **Database** into `database/`.

---

## Features
- **High Accuracy**: Reached **80.00%** on Spider Dev set.
- **Execution-guided Decoding**: Uses Beam Search (8 candidates) and picks the first syntactically valid SQL.
- **Localized Logic**: No external repository dependencies.
- **Streamlit UI**: Interactive database explorer and SQL generator.

## Evaluation
To verify the accuracy on the Spider benchmark:
```bash
$env:PYTHONPATH="."; python evaluation/official_natsql_eval.py
```

## Acknowledgements
Original implementation from the paper:
```
@inproceedings{li2022resdsql,
  author = {Haoyang Li and Jing Zhang and Cuiping Li and Hong Chen},
  title = "RESDSQL: Decoupling Schema Linking and Skeleton Parsing for Text-to-SQL",
  booktitle = "AAAI",
  year = "2023"
}
```
Special thanks to the authors for open-sourcing their code and checkpoints.
