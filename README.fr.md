# DualConfirm - Système d'authentification par mot de passe dynamique

<p align="center">
<a href="README.md"><img src="https://img.shields.io/badge/English-green.svg" /></a>
<a href="README.fr.md"><img src="https://img.shields.io/badge/French-fr-blue.svg" /></a>
</p>

<p align="center">
<img src="https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white" />
<img src="https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue" />
<img src="https://img.shields.io/badge/JavaScript-323330?style=for-the-badge&logo=javascript&logoColor=F7DF1E" />
<img src="https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white" />
<img src="https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white" />
<img src="https://img.shields.io/badge/redis-%23DD0031.svg?&style=for-the-badge&logo=redis&logoColor=white" />
</p>

Un système d'authentification sécurisé pour les institutions critiques qui génère des mots de passe dynamiques synchronisés et basés sur le temps, permettant aux clients et aux conseillers de vérifier mutuellement leur identité lors d'appels téléphoniques.

## 👩‍💻 Table des matières

* [Objectif](#-objectif)
* [Fonctionnalités principales](#-fonctionnalités-principales)
* [Exemple d'utilisation](#-exemple-dutilisation)
* [Architecture](#%EF%B8%8F-architecture)
* [Pour commencer](#-pour-commencer)
* [Notes de sécurité - Pour le développement uniquement](#-notes-de-sécurité---pour-le-développement-uniquement)
* [Contribution](#-contribution)

## 📔 Objectif
Suite à de récentes attaques informatiques dans le monde, en particulier en France, de nombreuses données personnelles, incluant des IBAN, ont été volées.

Les escrocs exploitent ces fuites en se faisant passer pour des conseillers, principalement bancaires, afin de gagner la confiance de leurs victimes et accéder à leurs comptes.
Face à ces menaces, il devient crucial de sécuriser les échanges entre les clients et leurs conseillers.

Ce projet propose une solution simple : permettre aux clients et conseillers de vérifier mutuellement leur identité via leur application avant tout échange sensible.

L'objectif est de remettre le conseiller et le client au cœur de l'authentification.

## 🔑 Fonctionnalités principales

- **Génération de mots de passe dynamiques**
  - Génération en temps réel de mots de passe uniques pour chaque paire client-conseiller
  - Les mots de passe changent toutes les 30 secondes pendant que les utilisateurs sont actifs
  - Utilise des mots courants du dictionnaire (min 6 - max 9 lettres) pour une meilleure mémorisation
  - Système évolutif capable de gérer des milliers de paires de mots de passe simultanément

- **Flux d'authentification double**
  - Chaque client a son propre mot de passe unique
  - Chaque conseiller voit des mots de passe distincts pour chacun de ses clients
  - Processus de vérification mutuelle pendant les appels téléphoniques
  - Synchronisation en temps réel entre les interfaces client et conseiller

- **Architecture et considérations de sécurité**
  - Isolation des infrastructures
    - Instances Redis séparées pour les mots courants, les paires de mots de passe et les sessions utilisateurs
    - Bases de données PostgreSQL séparées pour la gestion des utilisateurs et l'audit
    - Toutes les instances de base de données fonctionnent sur des conteneurs Docker isolés
  - Gestion de l'authentification et des sessions
    - Authentification basée sur JWT
    - Rotation automatique des mots de passe toutes les 30 secondes
    - Gestion complète des sessions avec timeouts automatiques
    - Journalisation complète de toutes les tentatives d'authentification et générations de mots de passe
  - Chiffrement et protection des données
    - Support HTTPS avec chiffrement SSL/TLS pour toutes les communications
    - Hachage des mots de passe avec bcrypt

- **Gestion avancée des sessions**
  - Timeout automatique des sessions après 180 secondes d'inactivité
  - Surveillance en temps réel de l'état des connexions
  - Gestion élégante des déconnexions
  - Mises à jour en temps réel basées sur WebSocket

## 📞 Exemple d'utilisation
```
Client : "Bonjour, c'est M. Dupont."
Conseiller : "Bonjour M. Dupont, c'est M. Martin de Société Fictive. Pourriez-vous me confirmer votre mot de passe client affiché sur votre interface ?"
Client : "Mon mot de passe est 'météo'. Pourriez-vous confirmer votre mot de passe conseiller ?"
Conseiller : "Mon mot de passe est 'diamant'."
```

## 🏗️ Architecture

### Schéma global

<p align="center">
<img width="1000" src="/git-img/global-scheme.png"/>
</p>

### Bases de données Redis
1. **Base de données des mots courants (Instance 1)**
   - Stocke les mots du dictionnaire pour la génération des mots de passe
   - Format des clés : `word:word_id`

2. **Base de données des paires de mots de passe (Instance 2)**
   - Stocke les mots de passe temporaires générés
   - Formats des clés :
     - Client : `password:user:<user_id>:advisor:<advisor_id>`
     - Conseiller : `password:advisor:<advisor_id>:user:<user_id>`

3. **Base de données des sessions utilisateurs (Instance 3)**
   - Gère les sessions actives et les états de connexion
   - Formats des clés :
     - État de connexion : `connection_status:<role>:<id>`
     - État d'activité : `active_status:<role>:<id>`
     - Jetons JWT : `otp:<id>`

### Bases de données PostgreSQL

1. **Base de données utilisateurs**
   - Tables :
     - `users` : Informations clients
     - `advisors` : Informations conseillers
     - `users_advisors` : Relations client-conseiller
     - `users_passwords` : Mots de passe clients hachés
     - `advisors_passwords` : Mots de passe conseillers hachés

2. **Base de données d'audit**
   - Tables :
     - `passwords_audit` : Historique de génération des mots de passe
     - `sessions_users_audit` : Suivi des sessions et événements de sécurité

## 🚀 Pour commencer

### Prérequis
- Docker et Docker Compose
- Python 3.11+
- OpenSSL (optionnel, pour la configuration HTTPS locale)

### Installation
<details>
<summary>Suivez le guide ⬇️</summary>
<br>

**1.** Clonez le dépôt :
```bash
git clone https://github.com/dnjfr/dual-confirm
cd dual-confirm
```

**2.** Créez et activez l'environnement virtuel :
```bash
python -m venv .venv
source .venv/bin/activate  # Sur Windows : .venv/Scripts/activate
```

**3.** Installez les dépendances :
```bash
pip install -r requirements.txt
```

**4.** Mettez à jour `package.json`, ajoutez la ligne :
```json
  "type": "module"
```

**5.** Créez un fichier `.env` avec les variables suivantes :

<details>
<summary>Liste des variables d'environnement utilisées ⬇️</summary>
<br>

```
GLOBAL_HOST_NETWORK=host.docker.internal

PGADMIN_DEFAULT_EMAIL=<votre_email_pour_pgadmin>
PGADMIN_DEFAULT_PASSWORD=<votre_mot_de_passe_pour_pgadmin>

POSTGRES_DB_NAME_USERS=DC_PG_USERS_ADVISORS
POSTGRES_DB_USERS_PORT=5433
POSTGRES_DB_USERS_USER=<votre_identifiant_pour_base_utilisateurs>
POSTGRES_DB_USERS_PASSWORD=<votre_mot_de_passe_pour_base_utilisateurs>
POSTGRES_DB_USERS_TABLENAME_USERS=users
POSTGRES_DB_USERS_TABLENAME_ADVISORS=advisors
POSTGRES_DB_USERS_TABLENAME_USERS_ADVISORS=users_advisors

POSTGRES_DB_NAME_USERS_PASSWORDS=DC_PG_USERS_PASSWORDS
POSTGRES_DB_USERS_PASSWORD_TABLENAME_USERS_PASSWORD=users_passwords
POSTGRES_DB_NAME_ADVISORS_PASSWORDS=DC_PG_ADVISORS_PASSWORDS
POSTGRES_DB_ADVISORS_PASSWORD_TABLENAME_ADVISORS_PASSWORD=advisors_passwords

POSTGRES_DB_NAME_AUDIT=DC_PG_AUDIT
POSTGRES_DB_AUDIT_PORT=5431
POSTGRES_DB_AUDIT_USER=<votre_identifiant_pour_base_audit>
POSTGRES_DB_AUDIT_PASSWORD=<votre_mot_de_passe_pour_base_audit>
POSTGRES_DB_AUDIT_TABLENAME_PASSWORDS_GENERATION_AUDIT=passwords_generation_audit
POSTGRES_DB_AUDIT_TABLENAME_SESSIONS_USERS_AUDIT=sessions_users_audit

REDIS_DB_WORDS_PORT=6379
REDIS_DB_WORDS_USER=<votre_identifiant_pour_base_mots_courants>
REDIS_DB_WORDS_PASSWORD=<votre_mot_de_passe_pour_base_mots_courants>

REDIS_DB_PASSWORDS_PORT=6389
REDIS_DB_PASSWORDS_USER=<votre_identifiant_pour_base_mots_de_passe_générés>
REDIS_DB_PASSWORDS_PASSWORD=<votre_mot_de_passe_pour_base_mots_de_passe_générés>

REDIS_DB_USERS_SESSIONS_PORT=6399
REDIS_DB_USERS_SESSIONS_USER=<votre_identifiant_pour_base_session_utilisateur>
REDIS_DB_USERS_SESSIONS_PASSWORD=<votre_mot_de_passe_pour_base_session_utilisateur>

FLASK_SECRET=<votre_clé_secrète_Flask>
JWT_SECRET=<votre_clé_secrète_JWT>

SAMPLES_LANGUAGE=<en_ou_fr>
```

</details>

<br>

**6.** Générez les fichiers ACL Redis :
```bash
python utils/generate_users_acl_rd.py
```

**7.** Démarrez les conteneurs Docker :
```bash
docker compose up -d 
```

**8.** Configurez les bases de données :
<details>
  <summary>Configuration PostgreSQL ⬇️</summary>
  <br>

  **8.1.** Accédez à pgAdmin sur <a href="http://localhost:5050/" target="_blank">http://localhost:5050/</a> et entrez votre email/mot_de_passe (ce sont les PGADMIN_DEFAULT_EMAIL et PGADMIN_DEFAULT_PASSWORD créés .env)

  **8.2.** Pour configurer un serveur, cliquez sur "Add new server"

  **8.3.** Configurez le serveur de base de données utilisateurs :
  - Nom du serveur : postgres-users
  - Hôte : 172.25.0.5
  - Port : 5432
  - Nom d'utilisateur : `<votre_identifiant_pour_base_utilisateurs>`
  - Mot de passe : `<votre_mot_de_passe_pour_base_utilisateurs>`

  **8.4.** Configurez le serveur de base de données d'audit :
  - Nom du serveur : postgres-audit
  - Hôte : 172.25.0.6
  - Port : 5432
  - Nom d'utilisateur : `<votre_identifiant_pour_base_audit>`
  - Mot de passe : `<votre_mot_de_passe_pour_base_audit>`

  **8.5.** Créez 3 bases de données dans le serveur postgres-users :
  - Base de tous les utilisateurs : DC_PG_USERS_ADVISORS
  - Base des mots de passe utilisateurs : DC_PG_USERS_PASSWORDS
  - Base des mots de passe conseillers : DC_PG_ADVISORS_PASSWORDS

  **8.6.** Créez la base de données dans le serveur postgres-audit :
  - Base d'audit des paires de mots de passe et des sessions utilisateurs : DC_PG_AUDIT
</details>

<details>
  <summary>Configuration Redis ⬇️</summary>
  <br>

  **8.7.** Accédez à RedisInsight sur <a href="http://localhost:5540/" target="_blank">http://localhost:5540/</a> et cliquez sur "Add Redis database"


  **8.8.** Configurez l'instance de base de données des mots courants :
  - Hôte : 172.25.0.2
  - Port : 6379
  - Alias base de données : DC_RD_WORDS
  - Nom d'utilisateur : `<votre_identifiant_pour_base_mots_courants>`
  - Mot de passe : `<votre_mot_de_passe_pour_base_mots_courants>`

  **8.9.** Configurez l'instance de base de données des mots de passe :
  - Hôte : 172.25.0.3
  - Port : 6379
  - Alias base de données : DC_RD_PASSWORDS
  - Nom d'utilisateur : `<votre_identifiant_pour_base_mots_de_passe_générés>`
  - Mot de passe : `<votre_mot_de_passe_pour_base_mots_de_passe_générés>`

  **8.10.** Configurez l'instance de base de données des sessions :
  - Hôte : 172.25.0.4
  - Port : 6379
  - Alias base de données : DC_RD_SESSIONS_USERS
  - Nom d'utilisateur : `<votre_identifiant_pour_base_session_utilisateur>`
  - Mot de passe : `<votre_mot_de_passe_pour_base_session_utilisateur>`

</details>

**9.** Exécutez le script de configuration des bases de données (le process peut être long, prenez un ☕) :
```bash
python setup_db_creation_population.py
```

**10.** Générez les certificats SSL pour HTTPS (optionnel) :

<details>
<summary>Utilisateurs Windows ⬇️</summary>
<br>
Si votre système d'exploitation est Windows et que OpenSSL n'est pas installé sur votre machine, la solution la plus simple consiste à télécharger et installer la version adaptée à votre système via FireDaemon : https://kb.firedaemon.com/support/solutions/articles/4000121705
</details>

```bash
python utils/setup_ssl.py
```

Modifiez ensuite le fichier `app.py` en fonction de l'utilisation ou non de SSL.

**11.** Ouvrez deux terminaux (vérifiez bien que les deux terminaux ont `.venv` activés) et démarrez l'application :
```bash
# Terminal 1 : Démarrez le service de génération de mots de passe
python passwords_generation.py

# Terminal 2 : Démarrez l'application principale
python app.py
```
</details>

## 🔒 Notes de sécurité - Pour le développement uniquement

- Mots de passe par défaut utilisés pour le projet :
  - Clients : `mypassword`
  - Conseillers : `mypassword2`
- Les déploiements en production doivent utiliser une gestion appropriée des mots de passe
- Les certificats HTTPS sont auto-signés pour le développement

## 🤝 Contribution

Ceci est un projet d'apprentissage et les contributions sont les bienvenues. N'hésitez pas à soumettre des pull requests ou à ouvrir des issues.