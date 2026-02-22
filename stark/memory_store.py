"""
stark/memory_store.py – Unified semantic memory store for STARK.

Replaces the fragmented dict/sqlite/memory_module constellation with a
single class that supports both exact-key lookup *and* fuzzy natural-
language recall via word-overlap (Jaccard) scoring.

Example
-------
>>> ms = MemoryStore()
>>> ms.store("sister birthday is June 3")
>>> results = ms.recall("when is my sister birthday")
>>> results[0]["value"]
'sister birthday is June 3'
"""

import datetime
import re
from typing import Optional


# Words that add no search signal
_STOP_WORDS = frozenset({
    "is", "are", "was", "were", "be", "been", "being",
    "the", "a", "an", "and", "or", "but", "in", "on",
    "at", "to", "for", "of", "with", "by", "from",
    "my", "your", "his", "her", "its", "our", "their",
    "i", "you", "he", "she", "it", "we", "they",
    "when", "what", "where", "how", "who", "which", "why",
    "do", "does", "did", "have", "has", "had", "will",
    "would", "could", "should", "may", "might", "can",
    "please", "stark",
})


def _tokenize(text: str) -> list:
    """Lowercase, split on non-word chars, remove stop words and short tokens.

    Apostrophes are stripped so ``"sister's"`` becomes ``"sisters"`` and
    matches queries for ``"sister"``.
    """
    # Strip apostrophes before tokenising so "sister's" → "sisters"
    cleaned = text.replace("'", "").replace("\u2019", "")
    tokens = re.findall(r"[a-zA-Z0-9]+", cleaned.lower())
    return [t for t in tokens if t not in _STOP_WORDS and len(t) > 1]


class MemoryStore:
    """
    Central memory store with semantic recall.

    Storage format per entry::

        {
          "value":     str,          # the stored fact / value
          "timestamp": ISO-8601 str,
          "words":     list[str],    # indexed tokens for recall
        }
    """

    def __init__(self) -> None:
        self._facts: dict = {}       # normalised_key -> entry dict
        self._word_index: dict = {}  # word -> set of keys

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    def store(self, text: str, value: Optional[str] = None) -> str:
        """
        Store *text* (and an optional separate *value*) in memory.

        Parameters
        ----------
        text:
            Natural-language string, e.g. ``"sister birthday is June 3"``.
        value:
            Explicit value to associate with *text* as the key.
            When omitted, *text* itself is both key and value.

        Returns
        -------
        str
            The normalised key under which the entry is stored.
        """
        key = text.lower().strip()
        words = _tokenize(text)
        entry = {
            "value": value if value is not None else text,
            "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
            "words": words,
        }
        # Remove old index entries for this key (update case)
        if key in self._facts:
            for w in self._facts[key]["words"]:
                self._word_index.get(w, set()).discard(key)

        self._facts[key] = entry
        for word in words:
            self._word_index.setdefault(word, set()).add(key)

        return key

    def forget(self, text: str) -> bool:
        """Remove a stored fact.  Returns True if it existed."""
        key = text.lower().strip()
        if key not in self._facts:
            return False
        for w in self._facts[key]["words"]:
            self._word_index.get(w, set()).discard(key)
        del self._facts[key]
        return True

    def clear(self) -> None:
        """Erase all stored memories."""
        self._facts.clear()
        self._word_index.clear()

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def recall(self, query: str, top_k: int = 5) -> list:
        """
        Return the *top_k* most semantically relevant memories for *query*.

        Scoring uses Jaccard similarity between the query token set and the
        stored fact token set, so ``"sister birthday"`` will match
        ``"sister birthday is June 3"`` without requiring an exact key.

        Returns
        -------
        list of dict
            Each dict has keys ``key``, ``value``, ``score``, ``timestamp``.
            Sorted by descending score.  Empty list if nothing matches.
        """
        query_tokens = set(_tokenize(query))
        if not query_tokens:
            return []

        scores: dict = {}
        for key, entry in self._facts.items():
            fact_tokens = set(entry["words"])
            intersection = query_tokens & fact_tokens
            if intersection:
                union = query_tokens | fact_tokens
                scores[key] = len(intersection) / len(union)

        ranked = sorted(scores.items(), key=lambda x: -x[1])
        return [
            {
                "key": k,
                "value": self._facts[k]["value"],
                "score": round(s, 3),
                "timestamp": self._facts[k]["timestamp"],
            }
            for k, s in ranked[:top_k]
        ]

    def recall_exact(self, key: str) -> Optional[str]:
        """Return the value for an exact key, or ``None`` if not found."""
        entry = self._facts.get(key.lower().strip())
        return entry["value"] if entry else None

    def all_facts(self) -> list:
        """Return all stored facts as a list of dicts."""
        return [
            {"key": k, "value": v["value"], "timestamp": v["timestamp"]}
            for k, v in self._facts.items()
        ]

    def summary(self) -> str:
        """Return a human-readable summary of stored memories."""
        if not self._facts:
            return "I do not have any stored memories yet, Sir."
        items = "; ".join(v["value"] for v in self._facts.values())
        return f"I remember: {items}"

    def __len__(self) -> int:
        return len(self._facts)

    def __contains__(self, key: str) -> bool:
        """Support ``key in memory_store`` syntax."""
        return key.lower().strip() in self._facts
