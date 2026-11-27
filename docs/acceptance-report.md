# Scientific acceptance record

Baseline c31157c had 25 passing tests and coverage of 77.71% of statements and 70.83% of branches. The development workflow now tests coverage independently from lint, formatting, type checking and distribution installation.

The principal API benchmark reproduced the original seeded false-alarm rate (0.0530), post-change detection frequency (1.0000), mean zero-based post-change delay (0.9908), binomial interval coverage (0.9592) and exact single-change recovery (185/200). An observed rate of one has sampling uncertainty. The scenario benchmark supplies exact binomial limits and reports missed and prematurely terminated trajectories separately.

Correlated-parameter readout variance was 4.9870e-6 by linearization and 4.9396e-6 in 10,000 Gaussian replicates. Under this specified covariance the cross terms reduce variance relative to conditioning on the calibration. This direction need not hold for a different covariance.

See the traceability matrix for individual scope limits. Local fit conditioning, scaled Jacobians and residuals now accompany decay estimates. A real IBM Runtime provider object passed the offline adapter test with 101 records. Sensitivity beyond the documented benchmark regimes remains a scientific limitation. The project owner approved version 0.1.0 for publication following the passing release-candidate gates.

Two correlated metrics under prespecified Gaussian reference parameters produced 417 familywise alarms in 10,000 trajectories. Using a reference mean and variance estimated from 12 external observations gave 1,546 alarms in 10,000 trajectories. The latter result is a counterexample to treating plug-in reference estimates as known parameters.
