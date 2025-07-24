# 🧹 FileCleanUP

**FileCleanUP** est un script Python conçu pour nettoyer et vérifier des fichiers de contacts issus du secteur pharmaceutique.  
Il identifie les doublons, vérifie la qualité des données (ex: absence d'email, prénom, etc.) et détecte les anomalies.

---

## 🚀 Fonctionnalités principales

- 🧠 Détection des **prénoms inconnus** (basé sur une base de référence, merci le gouvernement https://www.data.gouv.fr/datasets/fichier-des-prenoms-depuis-1900/)
- ✅ Vérification de la **qualité des données** avec motifs (colonnes manquantes, numéros mal formés…)
- 📊 Agrégation de colonnes (`Prénom`, `Nom`, `Portable formaté`) pour reconstituer un contact complet
- 🔍 Affichage de diagnostics sur les données manquantes
- 📁 Lecture de fichiers `.csv` et `.xlsx`

---

## 🛠️ Stack technique

- **Langage** : Python 3.11+
- **Librairies** : `pandas`, `openpyxl`
- **Environnement virtuel** : `.venv`
- **IDE recommandé** : Visual Studio Code

---

## 📂 Structure du projet

```
FileCleanUP/
├── main.py                # Script principal
├── Contacts_Cleaned.csv   # Fichier de sortie (exemple)
├── Prenoms.csv            # Base de prénoms pour validation
├── testfile.xlsx          # Fichier source de test
├── .gitignore
└── README.md
```

---

## ▶️ Lancer le script

1. Crée ton environnement virtuel :

```bash
python -m venv .venv
.venv\Scripts\activate  # Sur Windows
```

2. Installe les dépendances :

```bash
pip install pandas openpyxl
```

3. Lance le script :

```bash
python main.py
```

---

## 🧠 À venir

- Interface web légère
- Export des erreurs dans un fichier Excel
- Intégration HubSpot ou Salesforce API

---

## 👨‍💻 Auteur

Projet créé par [Tarek Aghenda](https://github.com/Tarekivida) — pour simplifier la vie des équipes marketing et CRM 💊

---

## 📜 Licence

Ce projet est sous licence MIT — voir le fichier `LICENSE` pour plus d'infos.
