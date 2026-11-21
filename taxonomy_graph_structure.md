# Trivia Party Taxonomy Graph Architecture: Complete Connected Structure

This document outlines the complete, properly connected graph structure for the Trivia Party taxonomy. It establishes a robust architectural separation between:
1. **Selectable Categories (Nodes)**: Broad, mid-level, and fine-grained nodes that players select during game setup.
2. **Internal Keywords / Metadata (Facets)**: Deterministic routing attributes (e.g., art period, museum, technique, medium, historical era).
3. **Leaf Entities (Supporting Material)**: Specific subjects (e.g., *Le Radeau de la Méduse*, *Eugène Delacroix*, *Louvre Museum*) that link directly to questions.

---

## Architecture Overview

```
+-------------------------------------------------------------------------+
|                    1. SELECTABLE CATEGORIES (Nodes)                     |
|         (Hierarchical DAG / Tree for game setup & question filtering)     |
+-------------------------------------------------------------------------+
                                     │
           Linked via Many-to-Many / Foreign Key Relationships
                                     │
+-------------------------------------------------------------------------+
|                  2. INTERNAL KEYWORDS / METADATA (Facets)                |
|        (Facets, tags, synonyms, and attributes for smart routing)       |
+-------------------------------------------------------------------------+
                                     │
                            Associated directly with
                                     │
+-------------------------------------------------------------------------+
|                    3. LEAF ENTITIES (Supporting Material)               |
|      (Concrete subjects, artworks, creators, and venues linked to Qs)   |
+-------------------------------------------------------------------------+
```

---

## 1. Selectable Categories (Nodes) — DAG / Tree

These form the hierarchical category tree presented to players during game setup. Categories support parent-child inheritance so players can choose broad buckets (e.g., `arts`) or fine-grained sub-genres (e.g., `arts.painting.romanticism`).

### A. Arts & Architecture (`arts`)
* **Architecture & Monuments** (`arts.architecture`)
  * Ancient & Classical Architecture (`arts.architecture.ancient`)
  * Medieval Architecture (`arts.architecture.medieval`)
  * Renaissance & Mannerist Architecture (`arts.architecture.renaissance`)
  * Baroque, Rococo & Neoclassical Architecture (`arts.architecture.baroque`)
  * 19th Century Architecture (`arts.architecture.19th_century`)
  * Modern & Contemporary Architecture (`arts.architecture.modern`)
* **Fine Arts & Painting** (`arts.painting`)
  * Prehistoric & Ancient Painting (`arts.painting.ancient`)
  * Medieval & Byzantine Painting (`arts.painting.medieval`)
  * Renaissance Painting (`arts.painting.renaissance`)
  * Baroque & Rococo Painting (`arts.painting.baroque`)
  * 19th Century Painting (`arts.painting.19th_century`)
  * 20th Century Painting & Movements (`arts.painting.20th_century`)
* **Sculpture & Craft** (`arts.sculpture`)
  * Ancient & Classical Sculpture (`arts.sculpture.ancient`)
  * Medieval & Renaissance Sculpture (`arts.sculpture.medieval_renaissance`)
  * 19th & 20th Century Sculpture (`arts.sculpture.modern`)

### B. History & Heritage Eras (`history`)
* **Ancient History** (`history.ancient`)
  * Early River Valley Civilizations
  * Ancient Egypt (Old, Middle, New Kingdoms)
  * Classical Greece (Golden Age, Peloponnesian War, Alexander)
  * Roman Republic & Empire
* **Middle Ages** (`history.middle_ages`)
  * Early Middle Ages & Migration Period
  * High Middle Ages (Feudalism, Crusades, Magna Carta)
  * Late Middle Ages (Black Death, Hundred Years' War)
* **Renaissance & Early Modern Era** (`history.renaissance_early_modern`)
  * European Renaissance & Humanism
  * Reformation & Religious Wars
  * Age of Discovery & Scientific Revolution
  * Enlightenment & Absolute Monarchy
* **19th Century History** (`history.19th_century`)
  * Age of Revolutions & Napoleonic Wars
  * Industrial Revolution & Urbanization
  * Nationalism & Unifications
  * Imperialism & Victorian Era
* **20th Century History** (`history.20th_century`)
  * World War I & Interwar Period
  * World War II & The Holocaust
  * Cold War & Geopolitics
  * Decolonization & Contemporary Era

---

## 2. Internal Keywords / Metadata (Facets)

Facets act as orthogonal attributes assigned to questions and leaf entities. They allow dynamic filtering, difficulty scaling, and multi-dimensional quiz generation without polluting the primary category tree.

| Facet Dimension | Description | Example Values |
|-----------------|-------------|----------------|
| **Art Period / Style** | stylistic categorization | `Romanticism`, `Baroque`, `High Renaissance`, `Impressionism`, `Gothic` |
| **Medium / Technique** | physical creation method | `Oil on Canvas`, `Fresco`, `Marble Carving`, `Tempera`, `Bronze Casting` |
| **Geographic Region** | origin or setting | `Western Europe`, `Flanders`, `Ancient Greece`, `Italy`, `France` |
| **Institution / Venue** | museum or archive housing the work | `Louvre Museum`, `Uffizi Gallery`, `Museo del Prado`, `Metropolitan Museum of Art` |
| **Century / Epoch** | temporal anchor | `19th Century`, `15th Century`, `5th Century BCE` |
| **Theme / Motif** | subject matter archetype | `Mythology`, `Religious Art`, `Sublime Landscape`, `Portraiture`, `Historical Event` |

---

## 3. Leaf Entities (Supporting Material)

Leaf entities represent concrete, named subjects that link directly to question items. Each entity is tagged with facets and linked to one or more selectable category nodes.

### Example Entity 1: *The Raft of the Medusa* (`entity.artwork.raft_of_the_medusa`)
* **Associated Categories**: 
  * `arts.painting.19th_century`
  * `history.19th_century`
* **Facets**:
  * Art Period: `Romanticism`
  * Medium: `Oil on Canvas`
  * Geographic Region: `France`
  * Institution: `Louvre Museum`
  * Century: `19th Century`
  * Theme: `Historical Event`, `Maritime Disaster`
* **Linked Creator**: *Eugène Delacroix* (influential contemporary) / *Théodore Géricault* (creator)

### Example Entity 2: *Théodore Géricault* (`entity.creator.theodore_gericault`)
* **Associated Categories**:
  * `arts.painting.19th_century`
* **Facets**:
  * Art Period: `Romanticism`
  * Geographic Region: `France`
  * Century: `19th Century`
* **Linked Works**: *The Raft of the Medusa*, *Charging Chasseur*

---

## 4. Graph Connection & Query Flow

1. **Game Setup**: Player selects `arts.painting.19th_century`.
2. **Category Resolution**: The query engine resolves all sub-nodes and fetches associated leaf entities (`entity.artwork.raft_of_the_medusa`, etc.).
3. **Facet Filtering (Optional)**: Trivia Party mode applies facet filters (e.g., `Art Period = Romanticism` AND `Institution = Louvre Museum`) to narrow or diversify question pools.
4. **Question Generation**: Questions linked to the resolved leaf entities are surfaced with appropriate difficulty weighting.
