# 🏙️ 15-Minute Shanghai — Track C : Accessibilité & Abordabilité

### 🔗 [**▶ Ouvrir l'application interactive en ligne**](https://projet-15-min-shanghai-3u2rnygx3gwo2xfkontzpt.streamlit.app/)
> Carte hexagonale de Shanghai : accessibilité « ville du quart d'heure » croisée avec le prix du logement.

---

## 🎯 Le projet en une phrase

On mesure, pour chaque quartier de Shanghai, **combien de services essentiels de la vie quotidienne sont
atteignables en 15 minutes à pied ou à vélo**, puis on croise cette accessibilité avec le **prix du logement** pour
répondre à une question d'équité :

> **Le « 15-minute city » à Shanghai est-il un privilège réservé aux quartiers riches, ou existe-t-il des
> corridors qui offrent à la fois une forte accessibilité ET un coût abordable ?**

C'est le **Track C — Affordability** du projet *15-Minute Shanghai*.

---

## 🧭 Démarche (résumée)

Le travail suit 3 étapes, une par notebook :

| Étape | Notebook | Ce qu'on fait |
|---|---|---|
| **1. Collecte** | [`01_data_collection.ipynb`](notebooks/01_data_collection.ipynb) | Revue de littérature (≥800 mots) + chargement et nettoyage des données (POI, écoles, prix, transport), gestion du système de coordonnées chinois. |
| **2. Grille & isochrones** | [`02_grid_isochrones.ipynb`](notebooks/02_grid_isochrones.ipynb) | Découpage de Shanghai en hexagones H3, construction du réseau routier, calcul de l'accessibilité 15 min par **distance réseau réelle**. |
| **3. Scoring & abordabilité** | [`03_scoring_h3.ipynb`](notebooks/03_scoring_h3.ipynb) | Indice d'accessibilité, croisement avec le prix, typologie des quartiers, et **régression** (l'accès est-il capitalisé dans le prix ?). |

---

## 📥 Données utilisées

| Donnée | Source | Rôle |
|---|---|---|
| Points d'intérêt (POI) par catégorie | Gaode / AMap (SHP 2024) | les 6 besoins du quotidien |
| Écoles (maternelle → lycée) | Gaode / AMap API (2026) | besoin « éducation » |
| Prix du logement (¥/m²) | Gaode `房价数据` + Anjuke | l'axe abordabilité |
| Réseau routier, métro, bus | Gaode (SHP 2024) | calcul des trajets réels |

> ⚙️ **Détail technique** : les données chinoises mélangent deux systèmes de coordonnées (WGS84 et GCJ-02, décalé
> d'environ 500 m). Tout a été réaligné en WGS84 avant analyse.

---

## 🔬 Méthode d'accessibilité

- **Unité spatiale** : hexagones **Uber H3 résolution 7** (~5 km² chacun, ≈ la taille d'un quartier de 15 min) →
  **1 869 hexagones habités** analysés.
- **Trajets réels** : un graphe routier de **~597 000 nœuds** est construit à partir des rues de Shanghai. On calcule
  la distance **le long des rues** (pas à vol d'oiseau) — méthode recommandée par la littérature.
- **Seuils 15 min** : marche = 4,8 km/h → **1,2 km** ; vélo = 15 km/h → **3,75 km**.
- **6 critères précis** (atteignables ≤ 15 min) :

| Critère | Ce qu'on compte |
|---|---|
| 🛒 Courses alimentaires | supermarché, supérette, marché (pas les restaurants) |
| 🏥 Santé de proximité | hôpital, clinique, pharmacie |
| 🏫 École | crèche, école, collège, lycée |
| 🚉 Transport en commun | métro, bus |
| 🏦 Services essentiels | banque, poste, équipement public |
| 🌳 Parc / sport | parc, terrain, salle de sport |

Un **7ᵉ critère** s'ajoute pour Track C : 🏠 **logement abordable** (prix sous la médiane de la ville).

---

## 📊 Résultats clés

- **À vélo, Shanghai est largement une ville du quart d'heure** (score moyen 5,2 / 6) — mais **à pied, c'est bien
  plus inégal** : seuls **23 % des quartiers** atteignent les 6 besoins à pied, et l'**école n'est accessible à pied que
  dans 26 % des cas**.
- **L'accessibilité est capitalisée dans le prix.** La régression (sur ~9 700 logements) montre que, à distance du
  métro égale, un meilleur indice d'accessibilité fait **monter le prix de façon significative** (coefficient positif,
  t ≈ 17). → l'accès se paie : c'est le cœur du problème d'équité.
- **Mais des corridors « accessibles ET abordables » existent** : **234 hexagones** combinent forte accessibilité et
  prix sous la médiane (surtout dans l'anneau intermédiaire, pas l'hyper-centre).

**Réponse à la question** : le 15-minute city à Shanghai n'est *pas seulement* un privilège de riches — le centre l'est,
mais il existe de vrais quartiers accessibles et abordables, que l'application aide à localiser.

---

## 🖥️ L'application

[**Application Streamlit en ligne**](https://projet-15-min-shanghai-3u2rnygx3gwo2xfkontzpt.streamlit.app/) — fonctionnalités :

- Carte hexagonale interactive de Shanghai (deck.gl / H3)
- Choix de l'indicateur : accessibilité, marche seule, prix, value score…
- **Survol d'un hexagone** → détail de chaque service (ex. « 🛒 Courses : ✅ supermarché, épicerie ») + prix du quartier
- **Recommandeur « Où habiter ? »** : filtre par budget + besoins → liste des meilleurs quartiers
- Panneau de transparence (sources, méthode, limites)

---

## 📂 Structure du dépôt

```
notebooks/   01 collecte + revue littérature · 02 grille/isochrones · 03 scoring/régression
app/         application Streamlit (streamlit_app.py + données légères)
src/         utilitaires (config, conversion de coordonnées, chargement)
outputs/     export final hexes.geojson
```

## ▶️ Lancer en local

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements-dev.txt   # stack complet (notebooks)
streamlit run app/streamlit_app.py    # lancer l'application
```
> `requirements.txt` = dépendances légères de l'app (déploiement). `requirements-dev.txt` = stack complet des notebooks.

## 📚 Références

- Moreno, C. et al. (2021). *Introducing the "15-Minute City".* **Smart Cities, 4(1), 93–111.**
- Pozoukidou, G. & Chatziyiannaki, Z. (2021). *15-Minute City: Decomposing the New Urban Planning Eutopia.* **Sustainability, 13(2).**
- Weng, M. et al. (2019). *The 15-minute walkable neighborhoods… social inequalities…* **Journal of Transport & Health, 13.**
- Shanghai Municipal Bureau of Planning and Natural Resources (2016). *Shanghai 15-Minute Community Life Circle Planning Guidelines.*
