# Scientific acceptance record

Baseline c31157c had 25 passing tests and coverage of 77.71% of statements and 70.83% of branches. The development workflow now tests coverage independently from lint, formatting, type checking and distribution installation.

The principal API benchmark reproduced the original seeded false-alarm rate (0.0530), post-change detection frequency (1.0000), mean zero-based post-change delay (0.9908), binomial interval coverage (0.9592) and exact single-change recovery (185/200). An observed rate of one has sampling uncertainty. The scenario benchmark supplies exact binomial limits and reports missed and prematurely terminated trajectories separately.

Correlated-parameter readout variance was 4.9870e-6 by linearization and 4.9396e-6 in 10,000 Gaussian replicates. Under this specified covariance the cross terms reduce variance relative to conditioning on the calibration. This direction need not hold for a different covariance.

See the traceability matrix for individual scope limits. Weak-identification diagnostics for decay, evidence from actual provider objects, coverage of additional benchmark regimes and the complete visualization set require review before release. The current development package is not approved for publication.
