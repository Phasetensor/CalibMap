# Release checklist

- Review the module matrix and scientific limitations against the release scope.
- Verify every required job on the chosen release commit, including separate coverage gates.
- Build wheel and source distribution, run strict Twine checks, install each in a fresh environment outside the checkout and smoke-test public imports.
- Obtain project-owner approval for merge and publication.
- Configure the PyPI publisher for the approved repository, environment and release workflow.
- Verify the tag, publish the same approved distribution bytes on GitHub and PyPI, compare SHA-256 digests and run a public install smoke test.
