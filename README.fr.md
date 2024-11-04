# TENKAWS (10K-AWS) : Plateforme d'Analyse des Rapports Annuels Propulsée par l'IA

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.9%20ou%20plus-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![AWS](https://img.shields.io/badge/Propulsé%20par-AWS-orange?style=for-the-badge&logo=amazon-aws)](https://aws.amazon.com/)
[![Claude](https://img.shields.io/badge/IA-Claude%203-pink?style=for-the-badge)](https://www.anthropic.com/)
[![SEC](https://img.shields.io/badge/Données-SEC%20EDGAR-green?style=for-the-badge)](https://www.sec.gov/edgar)
[![ChromaDB](https://img.shields.io/badge/Base%20de%20données-ChromaDB-red?style=for-the-badge)](https://www.trychroma.com/)

</div>

## 🏆 Équipe 28

| Membre          | Profil GitHub |
|-----------------|----------------|
| Anthony Boileau | [anthony-boileau](https://github.com/anthony-boileau) |
| Guillaume Collin | [Guillaume1208](https://github.com/Guillaume1208) |
| Minh Huynh      | [vibqetowi](https://github.com/vibqetowi) |

## 🎯 Aperçu du Projet

TENKAWS révolutionne l'analyse financière en transformant les rapports annuels américains complexes (formulaire SEC 10-K) en insights actionnables grâce à la puissance de l'IA générative. Notre plateforme simplifie l'analyse des documents 10-K en offrant :

- Analyse automatisée des documents et structuration
- Comparaisons historiques complètes
- Analyses techniques approfondies
- Interface de questions-réponses en langage naturel

Grâce à ces fonctionnalités, nous rendons l'analyse financière plus accessible et efficace pour les investisseurs, analystes et décideurs.

### Démonstration de la Plateforme

<div align="center">

![Démonstration de la Plateforme](./img/showcase.gif)

</div>

#### Insights IA avec Citations Sources
![Génération d'Insights IA](./img/1730737242023.png)

#### Interface de Discussion avec Base de Connaissances
![Interface de Chat](img/chat-interface.png)

#### Analyse Financière Complète
![Tableau de Bord d'Analyse Technique](img/screenshot-ta.png)

### 🌟 Fonctionnalités Clés

#### Analyse Automatisée des Rapports

Notre solution offre un accès gratuit aux composants textuels analysés des formulaires 10-K, extrayant les informations clés des documents SEC EDGAR dans un format JSON structuré :

```json
{
  "ticker": "MA",
  "year": 2018,
  "items": [
    {
      "item": "Item 3.",
      "description": "Legal Proceedings",
      "content": ["ITEM 3. LEGAL PROCEEDINGS Refer to Notes 10 (Accrued Expenses and Accrued Litigation) and 18 (Legal and Regulatory Proceedings) to the consolidated financial statements included in Part II, Item 8."]
    },
    {
      "item": "Item 4.",
      "description": "Mine Safety Disclosures",
      "content": ["ITEM 4. MINE SAFETY DISCLOSURES Not applicable."]
    }
  ]
}
```

#### Suite d'Analyses Avancées

Notre package d'analyses complet inclut :

- **Analyse Historique** : Comparaison des métriques quantitatives et aspects qualitatifs sur plusieurs années via LLM et recherche dans la base de données vectorielle
- **Q&R Interactif** : Requêtes en langage naturel propulsées par Claude 3
- **Analytics Complet** : Insights approfondis, des finances à la gouvernance
- **Données de Marché en Temps Réel** : Contexte de marché en direct via yfinance

## 🏗️ Architecture

### Stack Technologique

Conformément aux exigences du défi, chaque composant fonctionne ou est conçu pour fonctionner sur AWS. Malgré les contraintes de permissions, l'architecture a été conçue pour un déploiement AWS transparent :

- **Modèle IA** : Claude 3 par Anthropic, déployé sur AWS
  - Exploite les capacités robustes et l'accès gratuit (3.5 Sonnet)
  - Permet une ingénierie sophistiquée d'auto-prompting

- **Base de Données** : ChromaDB
  - Base de données vectorielle open-source avec support de déploiement AWS
  - Actuellement en local dû aux problèmes de permissions AWS
  - Stack AWS créé avec succès (voir [notre template](./json/reference/chroma-template.json))
  - Code prêt pour l'adaptation cloud
    ![Configuration Stack AWS](img/aws-stack.png)

- **Frontend/API** : Streamlit
  - Optimisé pour l'intégration Python
  - Capacités de développement rapide

- **Sources de Données** : SEC EDGAR et yfinance
  - Accès fiable et gratuit aux données financières

### Architecture Système

Les diagrammes suivants ont été générés avec PlantUML et suivent librement la syntaxe UML :

![Diagramme de Déploiement UML](img/uml-deployment.png)
![Flux de Génération de Rapport](img/uml-sequence-generate-report.png)

## 📊 Composants du Rapport

### Analyse Financière
- Métriques et fondamentaux de l'entreprise
- Suivi de performance historique
- Comparaisons sectorielles
- Surveillance des KPI
- Analyse du positionnement marché

### Leadership & Gouvernance
- Aperçu de la composition du conseil
- Profils des dirigeants
- Évaluation de la structure des comités
- Analyse des rémunérations
- Métriques DE&I

### Évaluation des Risques
- Identification et suivi des facteurs de risque
- Évolution des modèles de risque
- Évaluation des stratégies d'atténuation
- Analyse d'impact

## 🚀 Démarrage

```bash
# Installation des dépendances
pip install -r requirements.txt

# Configuration des identifiants AWS
aws configure

# Lancement de l'application
streamlit run 👋_Landing_Page.py
```

## Explicabilité de l'IA

Nous visons à garantir la précision grâce à un suivi méticuleux des sources. Chaque extrait de texte dans la base de données vectorielle inclut des métadonnées sources. Le LLM est invité à fournir des citations précises, renforçant les garde-fous naturels de Claude 3 contre les hallucinations.

Bien que l'optimisation de l'utilisation des tokens reste à améliorer, notre système de citation précise surpasse de nombreuses solutions commerciales qui peinent avec l'hallucination des sources.

Structure de la base de données exemple :

```json
[
    {
        "metadata": {
            "year": 2020,
            "ticker": "JAMEIL",
            "item": "Item 1."
        },
        "content": "Jameil is a food business, we sell breakfast cereal in Algeria"
    },
    {
        "metadata": {
            "year": 2021,
            "ticker": "JAMEIL",
            "item": "Item 1A."
        },
        "content": "The company expanded operations to Morocco and Tunisia. Revenue grew 25% year over year."
    }
]
```

Exemple de Q&R :

```
Q : Que vend Jameil ?
R : Jameil est une entreprise alimentaire qui vend des céréales pour le petit-déjeuner. Elle se concentre sur la fourniture d'options de petit-déjeuner abordables sur les marchés d'Afrique du Nord, spécifiquement en Algérie (rapport annuel 2020, Item 1).

Q : Qui est le PDG de Jameil ?
R : La source fournie ne mentionne pas le PDG de Jameil. Elle indique uniquement que Jameil est une entreprise alimentaire qui vend des céréales en Algérie, se concentrant sur la fourniture d'options de petit-déjeuner abordables aux marchés d'Afrique du Nord. Aucune information n'est donnée sur la direction ou le PDG de l'entreprise.
```

Notre base de données vectorielle stocke environ 32 mots par vecteur selon la longueur de la dernière phrase stockée. Le critère de séparation actuel est un simple comptage de mots.

## 📈 Métriques de Performance

Testé sur un MacBook Air, utilisant le module time de Python pour mesurer les temps de requête sur un échantillon aléatoire de 10 éléments :

| Métrique | Performance |
|----------|-------------|
| Temps d'analyse du rapport annuel vers JSON | $\hat{\mu} = 3,635s, \hat{\sigma} = 1,418s$ |
| Intégration du rapport annuel dans ChromaDB local | $\hat{\mu} = 131,03s, \hat{\sigma} = 65,62s$ |
| Récupération du contexte et réponse LLM | $\hat{\mu} = 4,69s, \hat{\sigma} = 1,28s$ |

## 🛣️ Feuille de Route

- Implémentation de l'analyse de sentiment des médias sociaux/actualités
- Conversion des appels bloquants restants en opérations asynchrones
- Déploiement d'instances de base de données hébergées et optimisation des performances d'intégration
- Analyse des formulaires 10-k par signification pour stocker des idées complètes dans les vecteurs
- Implémentation de la persistance dans les sessions d'application (actuellement, la navigation réinitialise les sections générées par l'IA)
- Ajout de la capacité de comparaison entre entreprises

## 📜 Licence

Ce projet est sous licence GPL - voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

<div align="center">

*Développé avec ❤️ pendant le Datathon Polyfinance 2024*

</div>