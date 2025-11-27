# NormGenesis

This repo provides the dataset introduced by our EMNLP 2025 paper "NormGenesis: Multicultural Dialogue Generation via Exemplar-Guided Social Norm Modeling and Violation Recovery".

<div align="center">

[![Project Page](https://img.shields.io/badge/Project-Page-blue)](https://bk123477.github.io/NormGenesis/)
[![arXiv](https://img.shields.io/badge/arXiv-2509.18395-b31b1b.svg)](https://arxiv.org/abs/2509.18395)
[![License: CC BY-SA 4.0](https://img.shields.io/badge/License-CC%20BY--SA%204.0-lightgrey.svg)](http://creativecommons.org/licenses/by-sa/4.0/)

</div>

---

## 🗓️ Update History

- **🚀 November 2025:** **Code**, **Dataset**, and **Project Page** have been released!
- **🏆 November 2025:** We received the SAC Highlights Award at EMNLP 2025!
- **🏆 October 2025:** Nominated for **Outstanding Paper**, **SAC Highlight**, and **Resource Paper Award** at EMNLP 2025.  
- **📘 September 2025:** Our paper was released on [arXiv](https://arxiv.org/abs/2509.18395).  
- **🎤 August 2025:** Selected for **Main Conference (Oral Presentation)** at EMNLP 2025.  

---

## 🎯 Project Overview

NormGenesis introduces a framework for multicultural dialogue generation that models social norms and recovers from violations using exemplar-guided methods.

### Key Components
- **Dataset**: Multicultural social norm datasets (American, Chinese, Korean).
- **Generation**: Pipelines for generating dialogues that adhere to or violate social norms.
- **Evaluation**: Comprehensive evaluation of dialogue quality including consistency, naturalness, relevance, and norm appropriateness.

---

## 📁 Repository Structure

```
NormGenesis/
├── 📊 dataset/                 # Dataset files
│   ├── American/               # American culture dataset
│   ├── Chinese/                # Chinese culture dataset
│   └── Korean/                 # Korean culture dataset
├── 🔬 evaluation_code/         # Evaluation scripts
│   ├── evaluation_dialogue_quality.py    # Dialogue quality evaluation
│   └── evaluation_refinement_quality.py  # Refinement quality evaluation
├── 🏭 generation_code/         # Generation pipelines
│   ├── American/               # American generation scripts
│   ├── Chinese/                # Chinese generation scripts
│   ├── Korean/                 # Korean generation scripts
│   └── refine_situation.py     # Situation refinement script
├── 📄 labeling_dialogue.py     # Dialogue labeling script
└── 📄 README.md
```

---

## 🚀 Quick Start

### Prerequisites

Ensure you have Python installed and the following dependencies:

```bash
pip install openai pandas tenacity tqdm
```

### Setup

Set your OpenAI API key as an environment variable:

```bash
export OPENAI_API_KEY="your-api-key"
```

### Usage

1. **Generation**: Navigate to `generation_code` and use the scripts for specific cultures or `refine_situation.py` to refine scenarios.
   *Note: You may need to update input/output paths in the scripts.*

2. **Evaluation**: Use `evaluation_code/evaluation_dialogue_quality.py` to assess generated dialogues.
   *Note: Ensure you configure the evaluation parameters in the script.*

---

## 🌍 Evaluation Scope

### Cultures Covered
- 🇺🇸 American
- 🇨🇳 Chinese
- 🇰🇷 Korean

### Evaluation Metrics
- **Consistency**: Logical and contextual consistency.
- **Naturalness**: Fluency and native-like expression.
- **Relevance**: Alignment with the scenario and situation.
- **Coherence**: Logical flow from scenario to dialogue.
- **Emotion Appropriateness**: Matching emotional tone.
- **Social Norm Appropriateness**: Adherence to social norms.

---

## 🚀 Release Plan
We plan to release both the **code** and **dataset** after the EMNLP 2025 conference.

- [✅] **Code**  
- [✅] **Dataset**
- [✅] **Project Page**

---

## 📄 Paper
You can find our paper at the following link:  
👉 [https://arxiv.org/abs/2509.18395](https://arxiv.org/abs/2509.18395)

---

## 📚 Citation
If you use this dataset or code in your research, please cite our paper:

```bibtex
@inproceedings{hong2025normgenesis,
  title={NormGenesis: Multicultural Dialogue Generation via Exemplar-Guided Social Norm Modeling and Violation Recovery},
  author={Hong, Minki and Choi, Jangho and Kim, Jihie},
  booktitle={Proceedings of the 2025 Conference on Empirical Methods in Natural Language Processing},
  pages={33781--33819},
  year={2025}
}
```