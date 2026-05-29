# Dictionnaire des Variables

## Variables climatiques

| Variable | Nom complet | Explication | Unité |
|----------|-------------|-------------|-------|
| `temperature_C` | Température | Température moyenne de la zone | °C (degrés Celsius) |
| `precipitations_mm` | Précipitations | Quantité de pluie tombée sur la période | mm (millimètres) |
| `humidite_pct` | Humidité relative | Pourcentage d'eau dans l'air | % (0 à 100) |
| `rayonnement_MJm2` | Rayonnement solaire | Énergie solaire reçue par le sol | MJ/m² (mégajoules par mètre carré) |
| `etp_mmd` | Évapotranspiration potentielle | Quantité d'eau qui s'évapore du sol + transpiration des plantes par jour | mm/jour |
| `co2_ppm` | Concentration de CO2 | Quantité de dioxyde de carbone dans l'air | ppm (parties par million) |

## Variables du sol

| Variable | Nom complet | Explication | Unité |
|----------|-------------|-------------|-------|
| `type_sol` | Type de sol | Classification du sol (ferrallitique, sableux, alluvial, etc.) | catégorie |
| `ph_sol` | pH du sol | Acidité du sol. < 7 = acide, 7 = neutre, > 7 = basique | échelle 0–14 |
| `matiere_organique_pct` | Matière organique | Pourcentage de matière organique (déchets végétaux décomposés) dans le sol | % |
| `N_kgha` | Azote (N) | Quantité d'azote disponible dans le sol — essentiel pour la croissance des feuilles | kg/ha (kilogrammes par hectare) |
| `P_kgha` | Phosphore (P) | Quantité de phosphore — essentiel pour les racines et la floraison | kg/ha |
| `K_kgha` | Potassium (K) | Quantité de potassium — essentiel pour les fruits et la résistance aux maladies | kg/ha |

> **N, P, K** = les 3 nutriments principaux d'un engrais (c'est ce qu'on voit sur les sacs d'engrais "NPK")

## Variables de pratiques agricoles

| Variable | Nom complet | Explication | Unité |
|----------|-------------|-------------|-------|
| `irrigation` | Type d'irrigation | Comment l'eau est apportée aux plantes | catégorie |
| | `non_irriguée` | Pas d'irrigation, la plante dépend uniquement de la pluie | |
| | `pluviale` | Agriculture qui repose sur l'eau de pluie | |
| | `gravitaire` | L'eau coule par gravité dans des canaux vers les cultures | |
| | `aspersion` | L'eau est projetée en l'air comme un arroseur de jardin | |
| | `goutte-à-goutte` | L'eau est délivrée directement à la racine via des tuyaux — la plus efficace | |
| `pratique_agricole` | Type de pratique | Méthode d'agriculture utilisée | catégorie |
| | `traditionnelle` | Méthodes ancestrales, peu d'intrants chimiques | |
| | `conventionnelle` | Agriculture moderne avec engrais chimiques et pesticides | |
| | `améliorée` | Traditionnelle + quelques techniques modernes | |
| | `biologique` | Sans produits chimiques, engrais naturels uniquement | |
| | `intégrée` | Mix optimisé de méthodes bio et conventionnelles | |

## Variables contextuelles

| Variable | Nom complet | Explication | Unité |
|----------|-------------|-------------|-------|
| `annee` | Année | Année de la récolte | année (2000–2024) |
| `region` | Région | Région administrative du Cameroun | catégorie (10 régions) |
| `culture` | Culture | Type de plante cultivée | catégorie (24 cultures) |
| `saison` | Saison | Période de l'année de la culture | catégorie |
| | `grande_saison_pluies` | Saison des pluies principale (mars–juin) | |
| | `petite_saison_pluies` | Deuxième saison des pluies (sept–nov) | |
| | `saison_sèche` | Période sèche principale (déc–fév) | |
| | `petite_saison_sèche` | Courte période sèche entre les deux saisons de pluie | |
| `altitude_m` | Altitude | Hauteur du terrain par rapport au niveau de la mer | mètres |
| `superficie_ha` | Superficie cultivée | Taille du champ | hectares (1 ha = 10 000 m²) |

## Variables environnementales

| Variable | Nom complet | Explication | Unité |
|----------|-------------|-------------|-------|
| `usage_terres_pct` | Usage des terres | Pourcentage de terres utilisées pour l'agriculture dans la zone | % |
| `stress_ecologique_idx` | Indice de stress écologique | Score de dégradation de l'environnement (déforestation, érosion, etc.) | indice 0–100 |

## Variables cibles (ce qu'on veut prédire)

| Variable | Nom complet | Explication | Unité |
|----------|-------------|-------------|-------|
| `rendement_tha` | **Rendement** | Quantité récoltée par hectare — **c'est ce que notre modèle prédit** | tonnes/hectare |
| `production_t` | Production totale | = rendement × superficie. On ne la prédit pas, elle se calcule | tonnes |

## Types de sol (les plus courants)

| Type | Description |
|------|-------------|
| `ferrallitique` | Sol rouge tropical, riche en fer — le plus courant au Cameroun |
| `ferrallitique_rouge` | Variante plus rouge, bonne rétention d'eau |
| `alluvial` | Sol déposé par les rivières — très fertile |
| `hydromorphe` | Sol gorgé d'eau, bon pour le riz |
| `vertisol` | Sol argileux noir, se fissure en saison sèche |
| `sableux` | Drainant, pauvre en nutriments |
| `andosolique` | Sol volcanique — très fertile |
| `volcanique` | Idem, riche en minéraux |
