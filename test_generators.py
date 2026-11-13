"""Check the sampler code in the submitted S2 notebooks against reference laws."""

import json
import math
import os
import unittest
from pathlib import Path

import numpy as np
import pandas as pd


os.environ.setdefault("MPLBACKEND", "Agg")
ROOT = Path(__file__).resolve().parents[1]
N = 30_000
ALPHA = 1e-6  # per CDF comparison; deliberately conservative for a test suite
MODES = (None, "Mexico", "Guatemala")


def load_cells(filename, cell_ids):
    """Run the notebook's setup and sampler cells, without long analyses."""
    nb = json.loads((ROOT / filename).read_text(encoding="utf-8"))
    selected = {c["id"]: c for c in nb["cells"] if c["cell_type"] == "code"}
    if missing := set(cell_ids).difference(selected):
        raise RuntimeError(f"{filename}: missing test entry points {sorted(missing)}")
    ns = {"__name__": "__main__", "display": lambda _: None, "print": lambda *_, **__: None}
    for cell_id in cell_ids:
        source = "".join(selected[cell_id]["source"])
        exec(compile(source, f"{filename}:{cell_id}", "exec"), ns)
    return ns


class GeneratorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Use the repository's checked-in dataset; no download during tests.
        raw = pd.read_csv(ROOT / "coffee_ratings.csv")
        prepared = raw.loc[
            raw["species"].eq("Arabica")
            & raw["moisture"].gt(0)
            & raw["acidity"].gt(0)
            & raw["body"].gt(0)
        ]
        cls.reference = {}
        for country in MODES:
            rows = prepared if country is None else prepared.loc[prepared["country_of_origin"].eq(country)]
            counts = rows["moisture"].value_counts().sort_index()
            cls.reference[country] = (counts.index.to_numpy(), counts.to_numpy() / len(rows))

        previous = Path.cwd()
        try:
            os.chdir(ROOT)
            cls.main = load_cells("stat-lab1-s2.ipynb", ("s2-03", "s2-05"))
            cls.bonus = load_cells(
                "stat-lab1-s2-bonus-alias.ipynb",
                ("bonus-03", "bonus-05", "bonus-09", "bonus-17", "bonus-23"),
            )
        finally:
            os.chdir(previous)

    def samplers(self):
        return {
            "inverse_cdf": self.main["generate_moisture"],
            "alias": self.bonus["generate_moisture_alias"],
            "rejection": self.bonus["generate_moisture_rejection"],
        }

    def assert_cdf_matches(self, sample, levels, probability):
        observed = np.searchsorted(np.sort(sample), levels, side="right") / len(sample)
        distance = np.max(np.abs(observed - np.cumsum(probability)))
        bound = math.sqrt(math.log(2 / ALPHA) / (2 * len(sample)))
        self.assertLessEqual(distance, bound, f"CDF gap {distance:.4f} exceeds {bound:.4f}")

    def test_inverse_cdf_assigns_interval_edges(self):
        u = np.array([0, np.nextafter(.25, 0), .25, .75, np.nextafter(1, 0)])
        result = self.main["inverse_cdf"](u, np.array([.09, .11, .13]), np.array([.25, .75, 1.]))
        np.testing.assert_array_equal(result, [.09, .09, .11, .13, .13])
        for invalid in (-.01, 1., np.nan):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                self.main["inverse_cdf"](invalid, np.array([.11]), np.array([1.]))

    def test_empirical_samplers_reject_invalid_requests(self):
        for name, sampler in self.samplers().items():
            with self.subTest(method=name):
                with self.assertRaises(ValueError):
                    sampler(-1, seed=42)
                with self.assertRaises(TypeError):
                    sampler(2.5, seed=42)
                with self.assertRaises(ValueError):
                    sampler(5, seed=42, country="Unknown")

    def test_empirical_samplers_empty_and_seeded(self):
        for name, sampler in self.samplers().items():
            with self.subTest(method=name):
                empty = sampler(0, seed=42)
                first = sampler(64, seed=42, country="Mexico")
                again = sampler(64, seed=42, country="Mexico")
                other = sampler(64, seed=43, country="Mexico")
                if name == "rejection":
                    self.assertEqual(empty[1], 0)
                    self.assertEqual(first[1], again[1])
                    empty, first, again, other = empty[0], first[0], again[0], other[0]
                self.assertEqual(empty.size, 0)
                self.assertEqual(first.shape, (64,))
                np.testing.assert_array_equal(first, again)
                self.assertFalse(np.array_equal(first, other))

    def test_empirical_samplers_reproduce_all_three_profiles(self):
        for method_index, (name, sampler) in enumerate(self.samplers().items()):
            for mode_index, country in enumerate(MODES):
                with self.subTest(method=name, country=country):
                    sample = sampler(N, seed=701 + 10 * method_index + mode_index, country=country)
                    if name == "rejection":
                        sample, attempts = sample
                        self.assertGreaterEqual(attempts, N)
                    levels, probability = self.reference[country]
                    self.assertEqual(sample.shape, (N,))
                    self.assertTrue(np.isin(sample, levels).all())
                    self.assert_cdf_matches(sample, levels, probability)

    def test_alias_table_preserves_exact_probabilities(self):
        build = self.bonus["build_alias"]
        draw = self.bonus["alias_indices"]
        for counts in ([1], [1, 1, 1], [0, 1, 3, 6]):
            with self.subTest(counts=counts):
                cutoff, alias, capacity = build(counts)
                buckets, tickets = np.indices((len(counts), sum(counts)))
                values = draw(buckets, tickets, cutoff, alias)
                self.assertEqual(capacity, sum(counts))
                np.testing.assert_array_equal(np.bincount(values.ravel(), minlength=len(counts)),
                                              len(counts) * np.array(counts))

    def test_rejection_counts_attempts_until_last_acceptance(self):
        # Accepted positions are 2 and 4 in a batch of six. The last two
        # proposals must not count toward the reported number of attempts.
        class ScriptedRng:
            def __init__(self):
                self.arrays = iter(([1, 0, 1, 0, 1, 0], [2, 0, 2, 0, 0, 0]))

            def integers(self, low, high, size):
                arr = np.array(next(self.arrays))
                assert size == arr.size and ((low <= arr) & (arr < high)).all()
                return arr

        class NumpyWithScriptedRng:
            def __getattr__(self, name):
                return getattr(np, name)

            class random:
                @staticmethod
                def default_rng(seed):
                    return ScriptedRng()

        sampler = self.bonus["generate_moisture_rejection"]
        # Counts [6, 1, 1, 1] give a six-proposal batch for two results.
        profile = self.bonus["fit_profile"]([.10] * 6 + [.11, .12, .13])
        namespace = sampler.__globals__
        previous_profile, previous_np = namespace["profiles"][None], namespace["np"]
        try:
            namespace["profiles"][None] = profile
            namespace["np"] = NumpyWithScriptedRng()
            sample, attempts = sampler(2, seed=1)
        finally:
            namespace["profiles"][None], namespace["np"] = previous_profile, previous_np
        np.testing.assert_array_equal(sample, [.10, .10])
        self.assertEqual(attempts, 4)

    def test_superposition_reproduces_joint_country_and_moisture_law(self):
        sampler = self.bonus["generate_moisture_mixture"]
        for i, weight in enumerate((.5, .8)):
            with self.subTest(weight=weight):
                sample, labels = sampler(N, mexico_weight=weight, seed=810 + i)
                self.assertEqual(sample.shape, (N,))
                self.assertEqual(labels.shape, (N,))
                self.assertTrue(np.isin(labels, ["Mexico", "Guatemala"]).all())
                for country, proportion in (("Mexico", weight), ("Guatemala", 1 - weight)):
                    levels, probability = self.reference[country]
                    mask = labels == country
                    self.assertTrue(np.isin(sample[mask], levels).all())
                    # +inf for the other country tests P(country, moisture <= x)
                    # on the full sample; the last level also checks the country weight.
                    self.assert_cdf_matches(np.where(mask, sample, np.inf), levels, proportion * probability)

    def test_superposition_endpoints_and_bad_weights(self):
        sampler = self.bonus["generate_moisture_mixture"]
        self.assertTrue(all(part.size == 0 for part in sampler(0, seed=84)))
        for weight, country in ((0, "Guatemala"), (1, "Mexico")):
            with self.subTest(weight=weight):
                sample, labels = sampler(64, mexico_weight=weight, seed=84)
                self.assertTrue((labels == country).all())
                self.assertTrue(np.isin(sample, self.reference[country][0]).all())
        for weight in (-.1, 1.1, np.nan):
            with self.subTest(invalid=weight), self.assertRaises(ValueError):
                sampler(1, mexico_weight=weight, seed=84)

    def test_rounded_beta_against_known_conditional_cdf(self):
        # Beta(2, 1) has F(x)=x². Use the analytic result independently of
        # SciPy and the notebook's fit; this checks the generator, not the fit.
        levels = np.arange(1, 101)
        upper = np.minimum(1, (levels + .5) / 100)
        expected_cdf = (upper**2 - .005**2) / (1 - .005**2)
        expected = np.diff(np.r_[0, expected_cdf])
        sample = self.bonus["generate_rounded_beta"](N, 2, 1, seed=911)
        self.assertEqual(sample.shape, (N,))
        self.assertTrue(np.issubdtype(sample.dtype, np.integer))
        self.assertTrue(((1 <= sample) & (sample <= 100)).all())
        self.assert_cdf_matches(sample, levels, expected)
        np.testing.assert_allclose(self.bonus["beta_record_prob"](2, 1), expected, atol=1e-14, rtol=0)

    def test_fitted_beta_sampler_reproduces_its_model(self):
        a, b = self.bonus["beta_a"], self.bonus["beta_b"]
        sample = self.bonus["generate_rounded_beta"](N, a, b, seed=912)
        probability = self.bonus["beta_expected"]
        self.assertEqual(sample.shape, (N,))
        self.assertTrue(((1 <= sample) & (sample <= 100)).all())
        self.assertTrue((probability >= 0).all())
        self.assertAlmostEqual(float(probability.sum()), 1.0)
        self.assert_cdf_matches(sample, np.arange(1, 101), probability)


if __name__ == "__main__":
    unittest.main(verbosity=2)
