<p align="left">
    <br>
    <img src="resdsql.png" width="700"/>
    <br>
<p>

# RESDSQL: Decoupling Schema Linking and Skeleton Parsing for Text-to-SQL

This is a modified implementation for **Local Interactive Demo** based on the official paper "RESDSQL: Decoupling Schema Linking and Skeleton Parsing for Text-to-SQL" (AAAI 2023).

If this repository could help you, please cite the following paper:
```
@inproceedings{li2022resdsql,
  author = {Haoyang Li and Jing Zhang and Cuiping Li and Hong Chen},
  title = "RESDSQL: Decoupling Schema Linking and Skeleton Parsing for Text-to-SQL",
  booktitle = "AAAI",
  year = "2023"
}
```

## 🚀 Interactive Local Demo (New)
We have added a **Streamlit-based web interface** to allow you to interactively test the model with your own questions or existing Spider databases.

### Prerequisites
1. **Python Environment**: Recommended Python 3.10 or 3.11.
2. **Install Dependencies**:
   ```sh
   pip install -r requirements.txt
   ```

### Prepare Data & Models
Since model weights and databases are large, they are **not included** in this git repository. You must download and place them in the following structure:
- `database/`: Folder containing SQLite databases (e.g., `concert_singer/`).
- `models/classifier/`: Cross-encoder checkpoint.
- `text2natsql-t5-large/`: T5-Large generator checkpoint.

> **Note**: You can request the full `.zip` package (including these folders) from the maintainer via Google Drive.

### How to Run
On Windows, simply double-click:
👉 **`run_demo.bat`**

Or run via terminal:
```sh
streamlit run main_streamlit.py
```

### 💡 Example Questions (`q.txt`)
The demo automatically detects example questions for each database. To add your own examples, create a `q.txt` file inside the specific database folder (e.g., `database/my_db/q.txt`) with one question per line.

---

## Original Paper Overview
We introduce a new Text-to-SQL parser, **RESDSQL** (**R**anking-enhanced **E**ncoding plus a **S**keleton-aware **D**ecoding framework for Text-to-**SQL**), which attempts to decoulpe the schema linking and the skeleton parsing to reduce the difficulty of Text-to-SQL. More details can be found in our [paper](https://arxiv.org/abs/2302.05965).

## Evaluation Results (Spider)
| Model | Dev EM | Dev EX | Test EM | Test EX |
|-------|--------|--------|---------|---------|
| RESDSQL-3B+NatSQL | **80.5%** | **84.1%** | **72.0%** | **79.9%** |
| RESDSQL-Large+NatSQL | 76.7% | 81.9% | - | - |

## Original Training & Inference
### Download Data & Models
Download [data](https://drive.google.com/file/d/19tsgBGAxpagULSl9r85IFKIZb4kyBGGu/view?usp=sharing) (Spider datasets) and [database](https://drive.google.com/file/d/1s4ItreFlTa8rUdzwVRmUR2Q9AHnxbNjo/view?usp=share_link) (SQLite files) and unzip them into the root directory.

### Checkpoints
- **Classifier**: [Google Drive Link](https://drive.google.com/file/d/1UWNj1ZADfKa1G5I4gBYCJeEQO6piMg4G/view?usp=share_link)
- **T5-Large**: [Google Drive Link](https://drive.google.com/file/d/1ZwFsH24_qKC3xwYdedPi6T_8argguWHe/view?usp=sharing)
- **T5-3B**: [OneDrive link](https://1drv.ms/u/s!Ak05bBUBFYiktcdziiE79xaeKtO6qg?e=e9424n)

Place these checkpoints in the `models/` folder as per original instructions.

---
*Disclaimer: This repository has been optimized for local demonstration. Large binary files are excluded via `.gitignore`.*
