# Release checklist

- Review the module matrix and scientific limitations against the release scope.
- Verify every required job on the chosen release commit, including separate coverage gates.
- Build wheel and source distribution, run strict Twine checks, install each in a fresh environment outside the checkout and smoke-test public imports.
- Obtain project-owner approval for merge and publication.
- Configure the PyPI publisher for the approved repository, environment and release workflow.
- Verify the tag, publish the same approved distribution bytes on GitHub and PyPI, compare SHA-256 digests and run a public install smoke test.

The prepared release workflow is release.yml with the pypi environment. The PyPI-side pending publisher must match owner Phasetensor and repository CalibMap. The workflow validates a stable tag at the current main commit, checks the validation workflow result, builds once and reuses those distributions. An owner must approve the release before dispatch.
