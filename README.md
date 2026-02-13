# Dynatrace Backup & Restore Manager - Multi-Tenant Edition

![Windows](https://img.shields.io/badge/Windows-Supported-blue)
![Python](https://img.shields.io/badge/Python-3.10%2B-green)
![Dynatrace](https://img.shields.io/badge/Dynatrace-Managed-orange)
![Multi-Tenant](https://img.shields.io/badge/Multi--Tenant-✓-brightgreen)

Application Windows complète pour gérer les **sauvegardes et restaurations** des configurations **Dynatrace Monaco** dans les environnements **Managed** (on-premise) avec **support multi-environnement et opérations en masse**.

## 🎯 Objectif

Fournir une solution intuitive pour:
- 📦 **Sauvegarder** automatiquement les configurations Monaco
- ♻️ **Restaurer** sélectivement les configurations
- 🌍 **Gérer plusieurs environnements Dynatrace** (Production, Staging, Dev)
- 📊 **Opérations en masse** (bulk backup, restore, compare) sur plusieurs tenants
- ⏰ **Planifier** les backups (quotidiens, hebdomadaires, etc.)
- 🗂️ **Gérer** les backups (archivage, retention, recherche)
- 👁️ **Monitorer** l'état en temps réel

## ⚡ Démarrage rapide (2 minutes)

```bash
# 1. Installation automatique
install.bat

# 2. Configuration
# Éditer .env avec vos paramètres Dynatrace

# 3. Démarrage
start.bat  # GUI
```

**Note**: Monaco CLI est déjà inclus - aucun téléchargement requis!  
**Voir [QUICKSTART.md](QUICKSTART.md) pour plus de détails**

## 🏗️ Architecture Multi-Tenant

```
PyQt6 GUI (Multi-Tenant)
    ├─ Environment Management
    ├─ Environment Groups
    └─ Bulk Operations
         ↓ HTTP/REST
    FastAPI Backend (Multi-Tenant API)
         ├─ /api/environments (CRUD + groups)
         ├─ /api/bulk-operations (backup, restore, compare)
         └─ /api/backups, /api/restore
         ↓
    SQLite DB (Multi-Tenant Schema)
         ├─ DynatraceEnvironment
         ├─ EnvironmentGroup
         ├─ Backup (+ environment_id)
         ├─ RestoreHistory (+ src/dst environment_id)
         └─ BulkOperation (+ per-env results)
         +
    Monaco CLI + Dynatrace Managed API (Multi-Env)
```

## ✅ Fonctionnalités principales

| Fonctionnalité | Status | Notes |
|---|---|---|
| Sauvegarde configs | ✅ | Export via Monaco CLI |
| Restauration | ✅ | Mode dry-run supporté |
| Planification | ✅ | Intégration Windows Scheduler |
| Gestion backups | ✅ | Archivage, retention |
| Interface GUI | ✅ | PyQt6 native Windows |
| API REST | ✅ | FastAPI avec docs Swagger |
| Multi-zone | ✅ | Filtrage par Management Zone |
| **🌍 Multi-environnement** | ✅ | Gestion multiple Dynatrace tenants |
| **📊 Opérations en masse** | ✅ | Bulk backup/restore/compare |
| **👥 Groupes d'environnement** | ✅ | Grouping pour opérations collectives |
| **🔍 Comparaison configs** | ✅ | Diff entre environnements |

## 📋 Installation

### Prérequis
- Windows 10/11 ou Windows Server 2016+
- Python 3.10+
- Dynatrace Managed (v235+)

### Steps
```bash
install.bat              # Setup automatique
# Éditer .env           # Renseigner credentials
start.bat              # Lancer l'application
```

## 📊 Interface

**6 onglets principaux:**
1. **Dashboard** - Statistiques et historique
2. **🌍 Environments** - Gestion multi-tenant (NOUVEAU)
3. **New Backup** - Créer une sauvegarde
4. **Restore** - Restaurer une configuration
5. **Connections** - Gérer connexions Dynatrace (hérité)
6. **Schedules** - Planifier les backups

### Onglet Environments - Multi-Tenant Management

**Sous-onglets:**

1. **Environments**
   - Ajouter/éditer/supprimer environnements Dynatrace
   - Voir état en temps réel (Healthy/Down)
   - Tester connexions
   - Tags pour organisation (team-a, region-us, critical, etc.)
   - Support multiple types (Production, Staging, Dev, Testing, Training, Custom)

2. **Environment Groups**
   - Créer des groupes pour opérations collectives
   - Ex: "All Production", "Team A Environments", etc.
   - Utiliser pour cibler bulk operations

3. **Bulk Operations**
   - 📦 **Bulk Backup** - Sauvegarder tous les environnements d'un groupe
   - ♻️ **Bulk Restore** - Restaurer sur plusieurs environnements
   - 🔍 **Bulk Compare** - Comparer configurations entre environnements
   - Voir historique avec statut par-environnement

## 🔧 Configuration

Éditer `.env`:
```env
DYNATRACE_ENVIRONMENT_URL=https://dynatrace.example.com/e/12345678
DYNATRACE_API_TOKEN=your-token-here
BACKUP_DIR=./backups
BACKUP_RETENTION_DAYS=30
```

## 📚 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Guide rapide
- **[DOCUMENTATION.md](DOCUMENTATION.md)** - Docs complètes
- **[API Swagger](http://localhost:8000/docs)** - API interactive

## 🚀 Utilisation

### Créer un backup
```
GUI → New Backup
  → Sélectionner connexion
  → Choisir type (All, Alerting, Dashboards, etc.)
  → "▶ Start Backup"
```

### Restaurer
```
GUI → Restore
  → Sélectionner backup
  → Choisir env. cible
  → "▶ Start Restore"
```

### Automatiser
```
GUI → Schedules
  → "➕ New Schedule"
  → Daily à 02:00
  → Save
```

## 📁 Structure

```
dynatrace-backup-manager/
├── backend/          # FastAPI + services
├── desktop_ui/       # PyQt6 interface
├── backups/          # Stockage backups
├── bin/              # Monaco CLI
├── .env              # Configuration
└── README.md         # Ce fichier
```

## 🐛 Dépannage

**Monaco not found?**
```
1. Télécharger desde GitHub
2. Placer dans bin/monaco.exe
```

**Connection failed?**
```
1. Vérifier URL et token
2. Tester dans UI (Connections)
3. Si certificat custom: DYNATRACE_INSECURE_SSL=true
```

## 📞 Support

Consulter [DOCUMENTATION.md](DOCUMENTATION.md) pour aide détaillée.
