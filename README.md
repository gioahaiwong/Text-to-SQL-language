<p align="left">
    <br>
    <img src="resdsql.png" width="700"/>
    <br>
<p>

# RESDSQL: Decoupling Schema Linking and Skeleton Parsing for Text-to-SQL

This is a modified implementation for **Local Interactive Demo** based on the official paper "RESDSQL: Decoupling Schema Linking and Skeleton Parsing for Text-to-SQL" (AAAI 2023). 

This version specifically uses the **NatSQL** enhanced checkpoints for better performance and efficiency.

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

1.  **Database Folder**: Create a `database/` folder in the root and fill it with SQLite databases.
2.  **Classifier Model**: Download and place in `models/classifier/`.
3.  **T5-Large Model**: Download and place in `text2natsql-t5-large/`.

### How to Run
On Windows, simply double-click:
👉 **`run_demo.bat`**

Or run via terminal:
```sh
streamlit run main_streamlit.py
```

### 💡 Example Questions (`q.txt`)
The demo automatically detects example questions for each database. To add your own examples, create a `q.txt` file inside the specific database folder (e.g., `database/car_1/q.txt`) with one question per line.

---

## Evaluation Results (Spider)
| Model | Dev EM | Dev EX |
|-------|--------|--------|
| **RESDSQL-Large+NatSQL (Used in this Demo)** | **76.7%** | **81.9%** |

---

## Download Resources
To run this demo, please download the specific NatSQL-enabled checkpoints and datasets:

### 1. Dataset & Databases
*   **Spider Databases**: [Download Link](https://drive.google.com/file/d/1s4ItreFlTa8rUdzwVRmUR2Q9AHnxbNjo/view?usp=share_link)
*   **Spider Data (Json)**: [Download Link](https://drive.google.com/file/d/19tsgBGAxpagULSl9r85IFKIZb4kyBGGu/view?usp=sharing)

### 2. Checkpoints (NatSQL Version)
| Checkpoint Type | Model Name | Download Link |
|-----------------|------------|---------------|
| **Classifier** | `text2natsql_schema_item_classifier` | [Google Drive](https://drive.google.com/file/d/1UWNj1ZADfKa1G5I4gBYCJeEQO6piMg4G/view?usp=share_link) |
| **Generator** | `text2natsql-t5-large` | [Google Drive](https://drive.google.com/file/d/1ZwFsH24_qKC3xwYdedPi6T_8argguWHe/view?usp=sharing) |

---
*Disclaimer: This repository has been optimized for local demonstration. Large binary files are excluded via `.gitignore`.*
