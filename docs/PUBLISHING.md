# Publish on GitHub

The repository includes Windows executables under `downloads/`. They are
intentionally tracked so visitors can download the GUI as soon as you push,
without waiting for a release build. The README's relative download links work
under your chosen GitHub username and repository name; no URL replacement is needed.

## First push

The local repository is already initialized and connected to
`https://github.com/MohamedYousry01/SHE-KeyUpdate-Tool.git`.
Open PowerShell in this folder, review the files, then commit and push:

```powershell
git status
git add .
git diff --cached --stat
git commit -m "Release SHE Key Studio: offline Windows provisioning workbench"
git push origin HEAD
```

Only public demo inputs belong in version control. Never commit real
provisioning keys. Build files and private inputs are excluded by `.gitignore`.

Suggested repository description:

> Offline Windows SHE key-update workbench: M1–M5 generation, authenticated
> inspection, ECU proof verification, and embedded C exports.

Suggested topics: `she`, `automotive-security`, `embedded`, `aes`, `cmac`,
`key-provisioning`, `python`, `pyside6`, `windows`.
Set the repository website field to your
[portfolio](https://mohamedyousry01.github.io/Mohamed-Yousry-Portfolio/).

## Publish a downloadable release

For the first version:

```powershell
git tag v1.0.0
git push origin v1.0.0
```

The Windows workflow tests and builds from source. When successful, a release
job attaches `SHE-Key-Studio.exe`, `she-key.exe`, `SHA256SUMS.txt`, and the
portable ZIP. GitHub Actions must be enabled. The job requests `contents:write`
only for release publication and uses GitHub's scoped workflow token.

After publication, a stable latest-release URL is:

```text
https://github.com/MohamedYousry01/SHE-KeyUpdate-Tool/releases/latest/download/SHE-Key-Studio.exe
```

You may switch the README download button to that URL once the first release
exists. Until then, its tracked-binary link works immediately after your push.
For a manual release, upload the ZIP from `release/` and both EXEs/checksum
file from `downloads/`. Keep dependency notices with a portable distribution.

## Before future releases

1. Update the version and changelog.
2. Run tests and `python scripts/build.py` in your virtual environment.
3. Commit updated sources, screenshot when relevant, binaries, and checksums.
4. Push a matching version tag and check that the release workflow succeeds.

No GitHub repository is created or pushed by the local build script.
