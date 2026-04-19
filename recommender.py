"""
recommender.py — Weighted Multi-Signal Recommendation Engine
CareerBridge v4

DESIGN PHILOSOPHY
-----------------
The engine scores each listing against the user's profile using four
independent signals, each with a calibrated weight:

  Signal              Weight   Rationale
  ──────────────────  ──────   ─────────────────────────────────────────────
  Title match           0.40   Title is the most information-dense field.
                               A skill appearing in the title is a very
                               strong signal of relevance.
  Domain match          0.30   Exact domain match catches broad alignment
                               (e.g. user says "data" → Data Science listings).
  Description match     0.20   Descriptions contain more prose; partial
                               matches here are weaker signals.
  Popularity boost      0.10   Listings with more applications are more
                               "proven" — a proxy for quality.

Final score is normalised to [0, 100] for easy display.

WHY THIS IS INTERVIEW-IMPRESSIVE
---------------------------------
1. Multi-signal scoring mirrors production recommendation systems
   (e.g. YouTube weights recency, click-through rate, and watch time).
2. Weights are explicit and tunable — a single dict to change.
3. Score normalisation makes outputs comparable and displayable.
4. The function is pure (no side effects), making it trivially testable.
5. The upgrade path to TF-IDF or embeddings requires changing only the
   _field_score() helper — the rest of the pipeline stays identical.
"""

from __future__ import annotations


# ── Tunable weights (must sum to 1.0) ─────────────────────────────────────────
WEIGHTS = {
    "title":       0.40,
    "domain":      0.30,
    "description": 0.20,
    "popularity":  0.10,
}


def recommend(
    skills: list[str],
    listings: list[dict],
    application_counts: dict[str, int] | None = None,
    top_n: int = 8,
) -> list[dict]:
    """
    Score every listing and return the top_n results.

    Parameters
    ----------
    skills              : user's skill strings (from profile or manual input)
    listings            : full list of listing dicts
    application_counts  : {listing_id: count} — used for popularity signal.
                          Pass None to skip the popularity boost.
    top_n               : maximum results to return

    Returns
    -------
    List of result dicts, sorted by final_score descending:
        {
          "listing":        <the original listing dict>,
          "final_score":    <int 0-100>,
          "matched_skills": <list of skills that contributed to the score>,
          "signal_scores":  <dict of per-signal raw scores, for transparency>,
        }

    Only results with final_score > 0 are included.
    """
    skills_clean = _normalise(skills)
    if not skills_clean:
        return []

    app_counts = application_counts or {}
    max_apps   = max(app_counts.values(), default=1) or 1  # avoid div-by-zero

    results = []
    for listing in listings:
        # ── Per-signal scores (each in range [0, 1]) ──
        title_score, title_matches = _field_score(skills_clean, listing.get("title", ""))
        domain_score, domain_matches = _field_score(skills_clean, listing.get("domain", ""))
        desc_score, desc_matches = _field_score(skills_clean, listing.get("description", ""))
        pop_score = app_counts.get(listing["id"], 0) / max_apps

        raw = (
            WEIGHTS["title"]       * title_score  +
            WEIGHTS["domain"]      * domain_score +
            WEIGHTS["description"] * desc_score   +
            WEIGHTS["popularity"]  * pop_score
        )

        if raw == 0:
            continue

        final_score  = round(raw * 100)
        matched_skills = sorted(set(title_matches + domain_matches + desc_matches))

        results.append({
            "listing":       listing,
            "final_score":   final_score,
            "matched_skills": matched_skills,
            "signal_scores": {
                "title":      round(title_score * 100),
                "domain":     round(domain_score * 100),
                "description": round(desc_score * 100),
                "popularity": round(pop_score * 100),
            },
        })

    results.sort(key=lambda r: r["final_score"], reverse=True)
    return results[:top_n]


# ── Internal helpers ───────────────────────────────────────────────────────────

def _normalise(skills: list[str]) -> list[str]:
    """Lowercase, strip, deduplicate, drop empty strings."""
    seen = set()
    out  = []
    for s in skills:
        s = s.lower().strip()
        if s and s not in seen:
            seen.add(s)
            out.append(s)
    return out


def _field_score(skills: list[str], field_text: str) -> tuple[float, list[str]]:
    """
    Score a single text field against the user's skill list.

    Returns
    -------
    (score, matched_skills)
        score         : fraction of skills that matched [0.0, 1.0]
        matched_skills: list of the skills that matched

    Matching logic: a skill matches if it appears as a substring of the
    field text (case-insensitive).  This handles:
      - exact matches:   "python"  in "Python for Beginners"  ✓
      - partial matches: "ml"      in "ML Engineer"           ✓
      - compound terms:  "machine learning" in "... machine learning ..."  ✓

    Upgrade path: replace the `skill in text` check with cosine similarity
    between TF-IDF or embedding vectors for semantic matching.
    """
    if not field_text or not skills:
        return 0.0, []

    text    = field_text.lower()
    matched = [s for s in skills if s in text]
    score   = len(matched) / len(skills)
    return score, matched


# ── Convenience: build application_counts from storage ────────────────────────

def build_app_counts(applications: list[dict]) -> dict[str, int]:
    """
    Convert the raw applications list into {listing_id: count}.
    Pass this to recommend() to activate the popularity signal.

    Example
    -------
    >>> from storage import load_applications
    >>> counts = build_app_counts(load_applications())
    >>> results = recommend(skills, listings, application_counts=counts)
    """
    counts: dict[str, int] = {}
    for app in applications:
        lid = app.get("listing_id", "")
        counts[lid] = counts.get(lid, 0) + 1
    return counts


# ══════════════════════════════════════════════════════════════════════════════
# UPGRADE ROADMAP
# ══════════════════════════════════════════════════════════════════════════════
#
# STAGE 1 — TF-IDF (no training, ~5 lines):
#   from sklearn.feature_extraction.text import TfidfVectorizer
#   from sklearn.metrics.pairwise import cosine_similarity
#   Replace _field_score() with:
#       docs   = [listing["description"] for listing in listings]
#       query  = " ".join(skills)
#       vec    = TfidfVectorizer()
#       matrix = vec.fit_transform(docs + [query])
#       scores = cosine_similarity(matrix[-1], matrix[:-1])[0]
#   This catches synonyms and vocabulary variation.
#
# STAGE 2 — Sentence Transformers (semantic similarity):
#   from sentence_transformers import SentenceTransformer, util
#   model = SentenceTransformer('all-MiniLM-L6-v2')
#   listing_vecs = model.encode([l["description"] for l in listings])
#   query_vec    = model.encode([" ".join(skills)])
#   scores       = util.cos_sim(query_vec, listing_vecs)[0]
#   Now "Flask" matches "Web Development" even without the keyword.
#
# STAGE 3 — Collaborative Filtering (once you have click/apply history):
#   Use the `implicit` library with user-item interaction matrices.
#   "Students who applied to X also applied to Y" pattern.
#
# STAGE 4 — Hybrid scoring (production-grade):
#   final = α * content_score + β * collab_score + γ * recency_score
#   Tune α, β, γ using A/B test results.x