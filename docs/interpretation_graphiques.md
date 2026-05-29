# Interprétation des Graphiques EDA

## 1. Distribution du rendement (`target_distribution.png`)

### Ce que montre le graphique
Deux graphiques côte à côte :
- **À gauche (histogramme)** : combien d'observations tombent dans chaque tranche de rendement
- **À droite (boxplot)** : résumé visuel avec la médiane, les quartiles et les outliers

### Ce qu'on observe
- La majorité des cultures ont un **rendement faible** (0–5 t/ha) — le pic est autour de 1 t/ha
- Très peu de cultures dépassent 25 t/ha
- La distribution est **asymétrique à droite** (skewée) — beaucoup de petites valeurs, peu de grandes
- Les **cercles** dans le boxplot = outliers (valeurs extrêmes mais pas forcément erreurs — ce sont les cultures à haut rendement comme l'ananas)

### Ce que ça implique pour le modèle
- On devra appliquer une **transformation logarithmique** (log) sur le rendement avant l'entraînement pour que le modèle ne soit pas biaisé vers les petites valeurs
- Les outliers ne sont pas des erreurs : ananas à 17 t/ha c'est normal

---

## 2. Matrice de corrélation (`correlation_matrix.png`)

### Ce que montre le graphique
Un tableau coloré qui montre **la force de la relation linéaire** entre chaque paire de variables numériques :
- **Rouge foncé (+1)** = quand l'une augmente, l'autre augmente aussi (relation positive forte)
- **Bleu foncé (-1)** = quand l'une augmente, l'autre diminue (relation négative forte)
- **Blanc (0)** = aucune relation linéaire

### Ce qu'on observe

| Relation | Corrélation | Signification |
|----------|-------------|---------------|
| K (potassium) → rendement | **+0.68** | Plus y'a de potassium, plus le rendement est élevé |
| N (azote) → rendement | **+0.42** | Plus y'a d'azote, plus ça pousse |
| Humidité → rendement | **+0.33** | Les zones humides produisent plus |
| Précipitations ↔ humidité | **+0.70** | Normal : plus il pleut, plus c'est humide (colinéarité) |
| CO2 ↔ année | **+0.97** | Le CO2 augmente chaque année — ces deux variables disent la même chose |
| pH → rendement | **-0.24** | Les sols trop basiques (pH élevé) donnent moins de rendement |
| Altitude → rendement | **-0.19** | Plus c'est haut, moins ça produit |

### Ce que ça implique pour le modèle
- **K et N** sont les meilleurs prédicteurs → ce seront nos principales recommandations
- On peut **supprimer `co2_ppm`** car elle est identique à `annee`
- Attention à la **colinéarité** humidité/précipitations — il faudra peut-être n'en garder qu'une

---

## 3. Rendement par culture et par région (`rendement_culture_region.png`)

### Ce que montre le graphique
Deux barplots :
- **En haut** : rendement moyen pour chaque culture (trié du plus haut au plus bas)
- **En bas** : rendement moyen pour chaque région

### Ce qu'on observe

**Par culture :**
- **Ananas (17 t/ha), bananier (15.5 t/ha), palmier à huile (14.3 t/ha)** dominent largement
- C'est normal : ces plantes produisent beaucoup de biomasse par hectare
- Les **céréales** (mil, sorgho, maïs) et les **cultures de rente** (café, cacao) produisent peu par hectare (<1.5 t/ha) — c'est leur nature
- L'écart est énorme (x30 entre ananas et cacaotier)

**Par région :**
- **Sud, Centre, Littoral** (zone forestière, humide) : 8–10 t/ha
- **Nord, Extrême-Nord** (zone sahélienne, sèche) : 1.4–2.5 t/ha
- Logique : plus d'eau et de fertilité naturelle au sud

### Ce que ça implique pour le modèle
- La variable **`culture`** est cruciale — le modèle doit savoir quelle culture on parle, sinon il ne peut pas prédire
- Il serait pertinent de faire des **prédictions par groupe de cultures** (vivrières, rente, maraîchage) car les échelles de rendement sont très différentes

---

## 4. Scatter plots des top features (`scatter_top_features.png`)

### Ce que montre le graphique
6 nuages de points : chaque point = une observation. L'axe X = la variable explicative, l'axe Y = le rendement.

### Ce qu'on observe

| Variable | Pattern visible |
|----------|----------------|
| **K_kgha** (potassium) | Relation linéaire claire ↗ — plus de K = plus de rendement. C'est la variable la plus prédictive |
| **N_kgha** (azote) | Tendance positive aussi, mais plus dispersée que K |
| **humidite_pct** | Les bons rendements (>15 t/ha) arrivent presque uniquement au-dessus de **70% d'humidité** |
| **precipitations_mm** | Tendance légère : plus de pluie = un peu plus de rendement, mais beaucoup de dispersion |
| **altitude_m** | Les meilleurs rendements sont en **basse altitude** (<1000m). Au-dessus de 1500m, presque tout est en dessous de 5 t/ha |
| **ph_sol** | Zone optimale entre **5.0 et 6.5**. Au-dessus de 6.5, le rendement chute |

### Ce que ça implique pour le modèle
- **K et N** : relations quasi-linéaires → le modèle pourra facilement les utiliser pour les recommandations ("ajoutez X kg/ha de potassium")
- **Humidité et altitude** : il y a des **seuils** (70% humidité, 1000m altitude) → les modèles à arbres (XGBoost, Random Forest) captent très bien ce type de pattern
- **pH** : il y a une **zone optimale** (ni trop acide, ni trop basique) → le modèle devra capter cette non-linéarité

---

## Résumé visuel des insights

```
                    FACTEURS QUI AUGMENTENT LE RENDEMENT
                    ====================================

    Potassium (K) ████████████████████████████████████  (+0.68)
    Azote (N)     ██████████████████████               (+0.42)
    Humidité      ████████████████                     (+0.33)
    Pluie         ██████████                           (+0.21)

                    FACTEURS QUI DIMINUENT LE RENDEMENT
                    ====================================

    pH élevé      ████████████                         (-0.24)
    Altitude      █████████                            (-0.19)
```
