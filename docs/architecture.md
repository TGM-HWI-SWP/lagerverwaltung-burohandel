# Architektur-Dokumentation

## Architektur-Übersicht

Das Projekt folgt der **Port-Adapter-Architektur** (Hexagonal Architecture) für maximale Testbarkeit und Wartbarkeit.

## Schichten-Modell

```
┌─────────────────────────────────────────────────────────┐
│                    UI-Layer (PyQt6)                     │
│              WarehouseMainWindow, Dialoge               │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│                  Service-Layer                          │
│              WarehouseService, BusinessLogic            │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│                  Domain-Layer                           │
│          Product, Movement, Warehouse (Entities)        │
└──────────────────────┬──────────────────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
┌───────▼────────┐          ┌────────▼──────────┐
│  Ports         │          │   Adapters       │
│  (Abstract)    │          │ (Implementations)│
│                │          │                   │
│RepositoryPort │◄────────►│InMemoryRepository│
│ ReportPort     │          │(sqlite, json, ...|
└────────────────┘          └───────────────────┘
```

# 📁 Datei-Struktur

### 🔧 Konfiguration
```
pyproject.toml          Python-Projektconfig & Dependencies
.gitignore              Git-Ignore-Regeln
.pylintrc               Linting-Konfiguration
.flake8                 Code-Style-Konfiguration
```

### 📚 Dokumentation
```
README.md               Komplette Projekt-Übersicht
TEMPLATE_INFO.md        Info über diese Vorlage
GIT_WORKFLOW.md        Git Best Practices & Workflow

docs/
  ├── architecture.md    Architektur-Dokumentation
  ├── contracts.md       Schnittstellen-Dokumentation (Rolle 1)
  ├── tests.md           Test-Strategie
  ├── projektmanagement.md  PM-Dokumente (PSP, Gantt, etc.)
  ├── retrospective.md   Retrospektive-Vorlage
  ├── changelog_template.md  Persönliche Changelog-Vorlage
  └── known_issues.md    Known Issues & Limitations
```

### 💻 Quellcode
```
src/
  ├── domain/           Geschäftslogik (Product, Warehouse)
  │   ├── product.py    Produktklasse
  │   └── warehouse.py  Lagerverwaltung
  ├── ports/            Schnittstellen-Definitionen
  ├── adapters/         Konkrete Implementierungen
  │   ├── repository.py  In-Memory, SQLite, JSON
  │   └── report.py     Report-Generierung
  ├── services/         Business Logic Service
  ├── ui/               PyQt6 Benutzeroberfläche
  └── reports/          Report-Module
```

### 🧪 Tests
```
tests/
  ├── unit/            Unit-Tests
  ├── integration/      Integration-Tests
  └── conftest.py      Pytest-Konfiguration
```

### 📦 Daten
```
data/                   Speicherort für Daten (SQLite, JSON, etc.)
```

---

**Letzte Aktualisierung:** 2025-01-20
**Version:** 0.1
