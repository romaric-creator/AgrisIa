# 🌾 Prédiction et Optimisation du Rendement Agricole au Cameroun

Système intelligent basé sur le Machine Learning qui prédit le rendement agricole (tonnes/hectare) et recommande des améliorations pour maximiser la production.

## Objectif

Développer un outil d'aide à la décision pour les agriculteurs camerounais :

1. **Prédiction** — L'utilisateur saisit une culture (ex: tomate), les paramètres du sol (pH, N, P, K) et les conditions climatiques → le modèle prédit combien de tonnes par hectare il peut espérer produire.
2. **Recommandation** — Le système analyse les écarts avec les rendements optimaux et suggère des améliorations concrètes (ajuster la fertilisation, changer le type d'irrigation, adapter la saison de plantation, etc.)

### Exemple d'utilisation

> *"Je veux planter de la tomate sur un sol ferrallitique, pH 5.8, 80 kg/ha d'azote, température moyenne 24°C, 1500mm de pluie."*
>
> → **Prédiction** : 8.2 t/ha
>
> → **Recommandations** : Augmenter N à 120 kg/ha (+25% rendement attendu), passer en irrigation goutte-à-goutte, privilégier la grande saison des pluies.

## Algorithmes

| Modèle | Rôle |
|--------|------|
| **Random Forest** | Baseline robuste, feature importance |
| **XGBoost** | Modèle principal de prédiction |
| **CNN-LSTM** | Capture des patterns temporels et spatiaux |

## Données

- **10 datasets** couvrant toutes les régions du Cameroun (2000-2024)
- **~43 000 observations**
- **22 variables** : climat, sol, pratiques agricoles
- **Variable cible** : rendement en tonnes par hectare

### Variables d'entrée (features)

| Catégorie | Variables |
|-----------|-----------|
| **Climat** | température, précipitations, humidité, rayonnement, ETP, CO2 |
| **Sol** | type de sol, pH, matière organique, N, P, K (kg/ha) |
| **Pratiques** | irrigation, pratique agricole, altitude, superficie |
| **Contexte** | région, culture, saison, année |

## Structure du projet

```
├── data/
│   ├── raw/              # Données brutes (non versionnées)
│   └── processed/        # Données nettoyées
├── notebooks/
│   ├── 01_EDA.ipynb                # Analyse exploratoire
│   ├── 02_preprocessing.ipynb      # Nettoyage et feature engineering
│   ├── 03_modeling.ipynb           # Entraînement des modèles
│   └── 04_evaluation.ipynb         # Évaluation et interprétabilité
├── src/                  # Code source réutilisable
├── models/               # Modèles sauvegardés
├── reports/figures/      # Visualisations
└── requirements.txt
```

## Installation

```bash
git clone https://github.com/<ton-username>/cameroon-crop-yield-prediction.git
cd cameroon-crop-yield-prediction
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Stack technique

- **Analyse** : Pandas, Seaborn, Plotly
- **Modélisation** : Scikit-learn, XGBoost
- **Interprétabilité** : SHAP
- **Tracking** : MLflow
- **Déploiement** : FastAPI, Streamlit

## Pipeline du projet

```
[Entrée utilisateur] → [Preprocessing] → [Modèle XGBoost/CNN-LSTM] → [Prédiction rendement t/ha]
                                                                     → [Module de recommandation]
                                                                     → [Suggestions d'amélioration]
```

## Résultats

*(À compléter après la modélisation)*

## Auteur

*(Ton nom)*

## Licence

MIT
