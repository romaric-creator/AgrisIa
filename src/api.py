from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from enum import Enum
import numpy as np
import pandas as pd
import joblib
from pathlib import Path

# Chemins
BASE_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = BASE_DIR / "models"

# Charger les modèles et objets de preprocessing
rf = joblib.load(MODELS_DIR / "random_forest.joblib")
xgb = joblib.load(MODELS_DIR / "xgboost.joblib")
scaler = joblib.load(MODELS_DIR / "scaler.joblib")
label_encoders = joblib.load(MODELS_DIR / "label_encoders.joblib")
feature_cols = joblib.load(MODELS_DIR / "feature_cols.joblib")

# Charger les données de référence
data = pd.read_csv(BASE_DIR / "data" / "processed" / "dataset_preprocessed.csv")
raw_data = pd.read_csv(BASE_DIR / "data" / "raw" / "CMR DS10 ML training set.csv")

# Pré-calculer les moyennes par région + saison (pour auto-remplissage)
AUTO_COLS = ['temperature_C', 'precipitations_mm', 'humidite_pct', 'rayonnement_MJm2',
             'etp_mmd', 'usage_terres_pct', 'stress_ecologique_idx', 'altitude_m']
region_saison_defaults = raw_data.groupby(['region', 'saison'])[AUTO_COLS].median()


# === ENUMS ===

CultureEnum = Enum('CultureEnum', {c: c for c in sorted(label_encoders['culture'].classes_)})
RegionEnum = Enum('RegionEnum', {r: r for r in sorted(label_encoders['region'].classes_)})
SaisonEnum = Enum('SaisonEnum', {s: s for s in sorted(label_encoders['saison'].classes_)})
TypeSolEnum = Enum('TypeSolEnum', {t: t for t in sorted(label_encoders['type_sol'].classes_)})
IrrigationEnum = Enum('IrrigationEnum', {i: i for i in sorted(label_encoders['irrigation'].classes_)})
PratiqueEnum = Enum('PratiqueEnum', {p: p for p in sorted(label_encoders['pratique_agricole'].classes_)})


# === MODÈLES DE DONNÉES ===

class PredictionInput(BaseModel):
    """
    Paramètres d'entrée pour prédire le rendement.

    Seuls les champs obligatoires sont nécessaires.
    Les paramètres climatiques (température, pluie, humidité, etc.) sont
    auto-remplis à partir des données historiques de la région + saison si non fournis.
    """

    # === OBLIGATOIRES (ce que l'agriculteur connaît) ===
    culture: CultureEnum = Field(
        ..., description="Culture à planter"
    )
    region: RegionEnum = Field(
        ..., description="Région du Cameroun"
    )
    saison: SaisonEnum = Field(
        ..., description="Saison de plantation"
    )
    type_sol: TypeSolEnum = Field(
        ..., description="Type de sol"
    )
    ph_sol: float = Field(
        ..., ge=3.5, le=9.0,
        description="pH du sol (mesure d'acidité : 3.5=très acide, 7=neutre, 9=basique)",
        json_schema_extra={"example": 5.8}
    )
    N_kgha: float = Field(
        ..., ge=0, le=400,
        description="Azote dans le sol (kg/ha) — résultat d'analyse de sol",
        json_schema_extra={"example": 80.0}
    )
    P_kgha: float = Field(
        ..., ge=0, le=200,
        description="Phosphore dans le sol (kg/ha) — résultat d'analyse de sol",
        json_schema_extra={"example": 40.0}
    )
    K_kgha: float = Field(
        ..., ge=0, le=500,
        description="Potassium dans le sol (kg/ha) — résultat d'analyse de sol",
        json_schema_extra={"example": 100.0}
    )
    irrigation: IrrigationEnum = Field(
        ..., description="Méthode d'irrigation prévue"
    )
    pratique_agricole: PratiqueEnum = Field(
        ..., description="Type de pratique agricole"
    )
    superficie_ha: float = Field(
        ..., ge=0.1, le=100,
        description="Superficie de la parcelle (hectares)",
        json_schema_extra={"example": 2.0}
    )

    # === OPTIONNELS (auto-remplis si non fournis) ===
    matiere_organique_pct: float | None = Field(
        default=None, ge=0, le=15,
        description="Matière organique du sol (%). Laissez vide si inconnu.",
        json_schema_extra={"example": None}
    )
    temperature_C: float | None = Field(
        default=None, ge=5, le=50,
        description="Température moyenne (°C). Auto-rempli selon la région si vide.",
        json_schema_extra={"example": None}
    )
    precipitations_mm: float | None = Field(
        default=None, ge=0, le=5000,
        description="Précipitations (mm). Auto-rempli selon la région si vide.",
        json_schema_extra={"example": None}
    )
    humidite_pct: float | None = Field(
        default=None, ge=0, le=100,
        description="Humidité relative (%). Auto-rempli selon la région si vide.",
        json_schema_extra={"example": None}
    )
    altitude_m: float | None = Field(
        default=None, ge=0, le=4000,
        description="Altitude (mètres). Auto-rempli selon la région si vide.",
        json_schema_extra={"example": None}
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "culture": "tomate",
                    "region": "Centre",
                    "saison": "grande_saison_pluies",
                    "type_sol": "ferrallitique",
                    "ph_sol": 5.8,
                    "N_kgha": 80.0,
                    "P_kgha": 40.0,
                    "K_kgha": 100.0,
                    "irrigation": "goutte-à-goutte",
                    "pratique_agricole": "améliorée",
                    "superficie_ha": 2.0
                }
            ]
        }
    }


class Recommendation(BaseModel):
    parametre: str = Field(..., description="Paramètre à ajuster")
    valeur_actuelle: str = Field(..., description="Votre valeur actuelle")
    valeur_recommandee: str = Field(..., description="Valeur optimale recommandée")
    impact_estime: str = Field(..., description="Impact estimé sur le rendement")


class PredictionOutput(BaseModel):
    rendement_predit_tha: float = Field(..., description="Rendement prédit (tonnes/hectare)")
    production_estimee_tonnes: float = Field(..., description="Production totale = rendement × superficie")
    rendement_min_tha: float = Field(..., description="Estimation basse")
    rendement_max_tha: float = Field(..., description="Estimation haute")
    modele_utilise: str = Field(..., description="Modèle ML utilisé")
    parametres_auto_remplis: dict = Field(..., description="Paramètres qui ont été auto-remplis (non fournis par l'utilisateur)")
    recommandations: list[Recommendation] = Field(..., description="Recommandations pour améliorer le rendement")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "rendement_predit_tha": 3.43,
                    "production_estimee_tonnes": 6.86,
                    "rendement_min_tha": 2.86,
                    "rendement_max_tha": 4.04,
                    "modele_utilise": "Ensemble (Random Forest + XGBoost)",
                    "parametres_auto_remplis": {
                        "temperature_C": 23.39,
                        "precipitations_mm": 1581.64,
                        "humidite_pct": 80.59,
                        "altitude_m": 698.0
                    },
                    "recommandations": [
                        {
                            "parametre": "Potassium (K)",
                            "valeur_actuelle": "100 kg/ha",
                            "valeur_recommandee": "179 kg/ha",
                            "impact_estime": "+13% rendement estimé"
                        }
                    ]
                }
            ]
        }
    }


# === APPLICATION ===

app = FastAPI(
    title="API Prédiction Rendement Agricole - Cameroun",
    description="""
## Description

API qui prédit le **rendement agricole** (tonnes/hectare) au Cameroun et génère des **recommandations** pour l'améliorer.

## Comment utiliser

**Étape 1** : Entrez les paramètres que vous connaissez (culture, sol, NPK, irrigation)

**Étape 2** : Les paramètres climatiques (température, pluie, humidité) sont **auto-remplis** à partir des données historiques de votre région et saison. Vous pouvez les overrider si vous les connaissez.

**Étape 3** : Recevez votre prédiction + des recommandations concrètes

## Exemple

**Entrée minimale :**
```json
{
  "culture": "tomate",
  "region": "Centre",
  "saison": "grande_saison_pluies",
  "type_sol": "ferrallitique",
  "ph_sol": 5.8,
  "N_kgha": 80,
  "P_kgha": 40,
  "K_kgha": 100,
  "irrigation": "goutte-à-goutte",
  "pratique_agricole": "améliorée",
  "superficie_ha": 2
}
```

**Réponse :**
- Rendement prédit : **3.43 t/ha**
- Production estimée : **6.86 tonnes**
- Recommandation : Augmenter K à 179 kg/ha → +13% rendement

## Modèles ML

| Modèle | R² | Erreur moyenne |
|--------|-----|----------------|
| Random Forest | 0.82 | ±1.63 t/ha |
| XGBoost | 0.81 | ±1.71 t/ha |
| **Ensemble (utilisé)** | **0.82** | **±1.63 t/ha** |
    """,
    version="1.0.0"
)


# === FONCTIONS ===

def get_defaults(region: str, saison: str) -> dict:
    """Récupère les valeurs moyennes historiques pour une région + saison."""
    try:
        defaults = region_saison_defaults.loc[(region, saison)]
        return defaults.to_dict()
    except KeyError:
        global_defaults = raw_data[AUTO_COLS].median()
        return global_defaults.to_dict()


def encode_input(input_data: PredictionInput, defaults: dict) -> pd.DataFrame:
    row = {
        'annee': 2024,
        'temperature_C': input_data.temperature_C if input_data.temperature_C is not None else defaults['temperature_C'],
        'precipitations_mm': input_data.precipitations_mm if input_data.precipitations_mm is not None else defaults['precipitations_mm'],
        'humidite_pct': input_data.humidite_pct if input_data.humidite_pct is not None else defaults['humidite_pct'],
        'rayonnement_MJm2': defaults['rayonnement_MJm2'],
        'etp_mmd': defaults['etp_mmd'],
        'usage_terres_pct': defaults['usage_terres_pct'],
        'stress_ecologique_idx': defaults['stress_ecologique_idx'],
        'ph_sol': input_data.ph_sol,
        'matiere_organique_pct': input_data.matiere_organique_pct if input_data.matiere_organique_pct is not None else raw_data['matiere_organique_pct'].median(),
        'N_kgha': input_data.N_kgha,
        'P_kgha': input_data.P_kgha,
        'K_kgha': input_data.K_kgha,
        'altitude_m': input_data.altitude_m if input_data.altitude_m is not None else defaults['altitude_m'],
        'superficie_ha': input_data.superficie_ha,
    }

    # Feature engineering
    row['NK_ratio'] = row['N_kgha'] / (row['K_kgha'] + 1)
    row['NP_ratio'] = row['N_kgha'] / (row['P_kgha'] + 1)
    row['NPK_total'] = row['N_kgha'] + row['P_kgha'] + row['K_kgha']
    row['indice_aridite'] = (row['etp_mmd'] * 365) / (row['precipitations_mm'] + 1)
    row['bilan_hydrique'] = row['precipitations_mm'] - (row['etp_mmd'] * 365)
    row['temp_x_humidite'] = row['temperature_C'] * row['humidite_pct'] / 100

    # Encodage catégorielles
    cat_mapping = {
        'region': input_data.region.value,
        'culture': input_data.culture.value,
        'saison': input_data.saison.value,
        'type_sol': input_data.type_sol.value,
        'irrigation': input_data.irrigation.value,
        'pratique_agricole': input_data.pratique_agricole.value,
    }

    for col, value in cat_mapping.items():
        le = label_encoders[col]
        if value not in le.classes_:
            raise HTTPException(
                status_code=400,
                detail=f"Valeur '{value}' inconnue pour '{col}'. Valeurs possibles: {list(le.classes_)}"
            )
        row[f'{col}_encoded'] = le.transform([value])[0]

    df = pd.DataFrame([row])[feature_cols]
    return df


def generate_recommendations(input_data: PredictionInput) -> list[Recommendation]:
    recommendations = []

    culture_value = input_data.culture.value
    culture_data = data[data['culture'] == culture_value]
    if culture_data.empty:
        return recommendations

    top_yields = culture_data.nlargest(int(len(culture_data) * 0.2), 'rendement_tha')

    # Potassium (K)
    optimal_K = top_yields['K_kgha'].median()
    if input_data.K_kgha < optimal_K * 0.7:
        recommendations.append(Recommendation(
            parametre="Potassium (K)",
            valeur_actuelle=f"{input_data.K_kgha:.0f} kg/ha",
            valeur_recommandee=f"{optimal_K:.0f} kg/ha",
            impact_estime=f"+{((optimal_K - input_data.K_kgha) / optimal_K * 30):.0f}% rendement estimé"
        ))

    # Azote (N)
    optimal_N = top_yields['N_kgha'].median()
    if input_data.N_kgha < optimal_N * 0.7:
        recommendations.append(Recommendation(
            parametre="Azote (N)",
            valeur_actuelle=f"{input_data.N_kgha:.0f} kg/ha",
            valeur_recommandee=f"{optimal_N:.0f} kg/ha",
            impact_estime=f"+{((optimal_N - input_data.N_kgha) / optimal_N * 20):.0f}% rendement estimé"
        ))

    # Phosphore (P)
    optimal_P = top_yields['P_kgha'].median()
    if input_data.P_kgha < optimal_P * 0.7:
        recommendations.append(Recommendation(
            parametre="Phosphore (P)",
            valeur_actuelle=f"{input_data.P_kgha:.0f} kg/ha",
            valeur_recommandee=f"{optimal_P:.0f} kg/ha",
            impact_estime=f"+{((optimal_P - input_data.P_kgha) / optimal_P * 10):.0f}% rendement estimé"
        ))

    # pH
    optimal_ph = top_yields['ph_sol'].median()
    if abs(input_data.ph_sol - optimal_ph) > 0.5:
        direction = "Augmenter" if input_data.ph_sol < optimal_ph else "Diminuer"
        recommendations.append(Recommendation(
            parametre="pH du sol",
            valeur_actuelle=f"{input_data.ph_sol:.1f}",
            valeur_recommandee=f"{optimal_ph:.1f}",
            impact_estime=f"{direction} le pH améliore l'absorption des nutriments"
        ))

    # Irrigation
    optimal_irrigation = top_yields['irrigation'].mode().iloc[0] if not top_yields['irrigation'].mode().empty else None
    if optimal_irrigation and input_data.irrigation.value != optimal_irrigation:
        recommendations.append(Recommendation(
            parametre="Irrigation",
            valeur_actuelle=input_data.irrigation.value,
            valeur_recommandee=optimal_irrigation,
            impact_estime="Meilleure efficacité hydrique pour cette culture"
        ))

    # Pratique agricole
    optimal_pratique = top_yields['pratique_agricole'].mode().iloc[0] if not top_yields['pratique_agricole'].mode().empty else None
    if optimal_pratique and input_data.pratique_agricole.value != optimal_pratique:
        recommendations.append(Recommendation(
            parametre="Pratique agricole",
            valeur_actuelle=input_data.pratique_agricole.value,
            valeur_recommandee=optimal_pratique,
            impact_estime="Pratique la plus performante pour cette culture"
        ))

    return recommendations


# === ENDPOINTS ===

@app.get("/", tags=["Informations"], summary="Accueil")
def root():
    """Informations sur l'API."""
    return {
        "message": "API Prédiction Rendement Agricole - Cameroun",
        "version": "1.0.0",
        "documentation": "/docs",
        "usage": "POST /predict avec les paramètres de votre parcelle"
    }


@app.get("/cultures", tags=["Références"], summary="24 cultures disponibles")
def get_cultures():
    """Liste des cultures reconnues par le modèle."""
    return {"cultures": sorted(list(label_encoders['culture'].classes_))}


@app.get("/regions", tags=["Références"], summary="10 régions du Cameroun")
def get_regions():
    """Liste des régions."""
    return {"regions": sorted(list(label_encoders['region'].classes_))}


@app.get("/types-sol", tags=["Références"], summary="16 types de sol")
def get_types_sol():
    """Liste des types de sol."""
    return {"types_sol": sorted(list(label_encoders['type_sol'].classes_))}


@app.get("/irrigations", tags=["Références"], summary="5 méthodes d'irrigation")
def get_irrigations():
    """Liste des méthodes d'irrigation."""
    return {"irrigations": sorted(list(label_encoders['irrigation'].classes_))}


@app.get("/pratiques", tags=["Références"], summary="5 pratiques agricoles")
def get_pratiques():
    """Liste des pratiques agricoles."""
    return {"pratiques": sorted(list(label_encoders['pratique_agricole'].classes_))}


@app.get("/saisons", tags=["Références"], summary="4 saisons")
def get_saisons():
    """Liste des saisons de plantation."""
    return {"saisons": sorted(list(label_encoders['saison'].classes_))}


@app.post("/predict", tags=["Prédiction"], summary="Prédire le rendement",
          response_model=PredictionOutput)
def predict(input_data: PredictionInput):
    """
    ## Prédire le rendement agricole

    Entrez les paramètres de votre parcelle. Les champs climatiques
    (température, pluie, humidité, altitude) sont **optionnels** — ils seront
    auto-remplis à partir des données historiques de votre région + saison.

    ### Champs obligatoires
    - Culture, région, saison, type de sol
    - pH du sol, N, P, K (kg/ha)
    - Irrigation, pratique agricole, superficie

    ### Champs optionnels (auto-remplis si vides)
    - Température, précipitations, humidité, altitude, matière organique
    """

    region = input_data.region.value
    saison = input_data.saison.value

    # Auto-remplir les valeurs manquantes
    defaults = get_defaults(region, saison)
    auto_filled = {}

    if input_data.temperature_C is None:
        auto_filled['temperature_C'] = round(defaults['temperature_C'], 1)
    if input_data.precipitations_mm is None:
        auto_filled['precipitations_mm'] = round(defaults['precipitations_mm'], 0)
    if input_data.humidite_pct is None:
        auto_filled['humidite_pct'] = round(defaults['humidite_pct'], 1)
    if input_data.altitude_m is None:
        auto_filled['altitude_m'] = round(defaults['altitude_m'], 0)
    if input_data.matiere_organique_pct is None:
        auto_filled['matiere_organique_pct'] = round(float(raw_data['matiere_organique_pct'].median()), 1)

    auto_filled['rayonnement_MJm2'] = round(defaults['rayonnement_MJm2'], 1)
    auto_filled['etp_mmd'] = round(defaults['etp_mmd'], 2)

    # Encoder
    X = encode_input(input_data, defaults)

    # Prédiction
    pred_rf_log = rf.predict(X)[0]
    pred_xgb_log = xgb.predict(X)[0]
    pred_log = 0.55 * pred_rf_log + 0.45 * pred_xgb_log
    rendement = float(np.expm1(pred_log))

    pred_min = float(np.expm1(min(pred_rf_log, pred_xgb_log)) * 0.85)
    pred_max = float(np.expm1(max(pred_rf_log, pred_xgb_log)) * 1.15)

    production = rendement * input_data.superficie_ha

    # Recommandations
    recommendations = generate_recommendations(input_data)

    return PredictionOutput(
        rendement_predit_tha=round(rendement, 2),
        production_estimee_tonnes=round(production, 2),
        rendement_min_tha=round(max(0, pred_min), 2),
        rendement_max_tha=round(pred_max, 2),
        modele_utilise="Ensemble (Random Forest + XGBoost)",
        parametres_auto_remplis=auto_filled,
        recommandations=recommendations
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
