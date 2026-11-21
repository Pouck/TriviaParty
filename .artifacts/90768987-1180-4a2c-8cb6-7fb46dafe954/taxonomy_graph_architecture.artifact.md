# Trivia Party Taxonomy Graph Architecture

To ensure we get this structural foundation right on the first try without premature iteration, here is the architectural separation of our directed acyclic graph (DAG) into three distinct tiers:

---

## 🏗️ The Three-Tier Graph Architecture

### Tier 1: Selectable Categories (The Setup Nodes)
*These are clean, distinct, user-facing categories and sub-categories that appear in game setup (Random, Vote, and Manual/Topics modes).*
- **Must be broad enough** to aggregate multiple questions (never single-question buckets).
- **Examples**:
  - `arts` -> `arts.painting` -> `arts.painting.romanticism`
  - `history` -> `history.19th_century` -> `history.19th_century.napoleonic`
  - `geography` -> `geography.europe` -> `geography.europe.france`

### Tier 2: Internal Keywords & Facets (The Routing Layer)
*These are deterministic attributes, synonyms, and metadata tags that players do not need to see or select in setup, but which the engine uses to route questions and synonyms automatically.*
- **Facets & Attributes**:
  - `period`: Romanticism, Renaissance, Antiquity
  - `medium`: Oil on canvas, Marble, Fresco
  - `location / museum`: Louvre, Musée d'Orsay, Vatican
  - **Synonyms & Keywords**: Deterministic mapping dictionary (e.g., `"grec"`, `"hellénique"`, `"Athènes"` -> `history.ancient.greece`).

### Tier 3: Leaf Entities (Compact Entities & Facet-Based Question Derivation)
*These are specific, concrete entities (e.g., Le Radeau de la Méduse, Géricault, Tour Eiffel) stored compactly as a single source of truth.*
- **Role**: Each leaf entity links to its parent selectable category (Tier 1) via DAG edges and contains robust structured attributes/facts (Tier 2).
- **Facet-Based Question Derivation & Compactness**: To maintain a compact database and prevent repetitions or bloating, a single rich leaf entity (e.g., *Le Radeau de la Méduse*) acts as the single source of truth from which multiple distinct thematic angles/facets are queried and generated dynamically:
  - *What is it named?* (Title / Subject)
  - *Who painted/created it?* (Author / Creator)
  - *Where is it exposed / located?* (Museum / City)
  - *What art movement / period does it belong to?* (Facet tag)
  By querying different facets of the same leaf entity rather than storing separate duplicate questions, the database remains extremely compact and modular while supporting a massive combinatorial variety of question variants.

---

## 🔗 Graph Connection & Purity Rules
1. **Pure Nodes**: No combined/muddled categories (e.g., no "Classical Greek and Roman frescoes"). Greek art and Roman art are distinct branch nodes under Painting/Architecture.
2. **Deterministic Resolution**: When a user selects `arts.painting.romanticism`, the engine traverses the DAG to gather all leaf entities (like *Le Radeau de la Méduse*) tagged with that facet, guaranteeing robust question sets without relying on AI guesswork.
