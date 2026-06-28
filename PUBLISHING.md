# Publishing the Keraunos integration on HACS

There are two levels of "publishing" on HACS:

1. **Custom repository** — anyone can add your GitHub repo URL to their HACS and
   install it. No approval needed, works immediately.
2. **HACS default store** — your repo is listed in HACS out of the box. Requires
   a pull request to `hacs/default` and passing automated validation.

This guide covers both, starting from the repo you already have.

---

## 0. Prerequisites

- A **public** GitHub repository (HACS cannot see private repos).
- The repo layout HACS expects (you already have this):
  ```
  hacs.json                         # repo root
  custom_components/keraunos/
    manifest.json
    __init__.py
    ...
  ```
- One integration per repository (HACS rule).

---

## 1. Finalize repository metadata

### `manifest.json`
Replace the placeholders and make sure these keys are correct. For HACS the
important ones are `domain`, `name`, `version`, `documentation`, `issue_tracker`,
and `codeowners`:

```json
{
  "domain": "keraunos",
  "name": "Keraunos Orages",
  "codeowners": ["@your-github-username"],
  "config_flow": true,
  "documentation": "https://github.com/your-github-username/keraunos-ha",
  "issue_tracker": "https://github.com/your-github-username/keraunos-ha/issues",
  "integration_type": "service",
  "iot_class": "cloud_polling",
  "requirements": ["beautifulsoup4>=4.12.0"],
  "version": "0.1.0"
}
```

- `codeowners` must contain at least your `@username` for default-store inclusion.
- `version` must be present for custom integrations and should match your release
  tag (see step 4).

### `hacs.json` (already present)
```json
{
  "name": "Keraunos Orages",
  "content_in_root": false,
  "render_readme": true,
  "homeassistant": "2024.4.0"
}
```
- `homeassistant` is the minimum HA version you support.
- Keep `content_in_root: false` because the integration lives under
  `custom_components/`.

---

## 2. Add validation workflows (recommended, required for default store)

Two GitHub Actions are expected:

- **hassfest** — Home Assistant's own integration validator.
- **HACS action** — validates the repo against HACS rules.

A ready-made workflow is included at `.github/workflows/validate.yml`. Push it and
confirm both jobs pass on the **Actions** tab. Fix any reported issues before
proceeding.

---

## 3. Create the GitHub repository and push

```bash
cd /Users/guillaume/projects/keraunos-ha
git init
git add .
git commit -m "feat: initial Keraunos HACS integration"
gh repo create keraunos-ha --public --source=. --remote=origin --push
```

Then on the repo page:
- Add a short **description**.
- Add **topics** including `home-assistant`, `hacs`, `integration` (HACS shows
  these and the default-store review looks for `home-assistant`/`hacs`).

---

## 4. Publish a release (HACS installs from releases/tags)

HACS installs the version a user selects from your **GitHub releases**. Without a
release, HACS falls back to the default branch, which is discouraged.

```bash
git tag v0.1.0
git push origin v0.1.0
gh release create v0.1.0 --title "v0.1.0" --notes "First release"
```

Keep the tag (`v0.1.0`) and `manifest.json` `version` (`0.1.0`) in sync for every
release. Bump both each time you ship a change.

---

## 5. Install via custom repository (available now)

Share these steps with users (also good for your own testing):

1. In Home Assistant: **HACS → ⋮ (top right) → Custom repositories**.
2. Repository: `https://github.com/your-github-username/keraunos-ha`
   Category: **Integration**.
3. Click **Add**, then find **Keraunos Orages** in HACS and **Download**.
4. **Restart Home Assistant**.
5. **Settings → Devices & Services → Add Integration → Keraunos Orages**, enter
   the INSEE code.

At this point the integration is fully usable. Steps 6–7 are only for getting it
into the HACS default store.

---

## 6. Add a brand (required for default store)

The HACS default store requires the domain to exist in the
[`home-assistant/brands`](https://github.com/home-assistant/brands) repo.

1. Fork `home-assistant/brands`.
2. Add icons under `custom_integrations/keraunos/`:
   - `icon.png` (256×256) and optionally `logo.png`.
3. Open a PR. Once merged, the domain `keraunos` is recognized as a valid brand.

(You can use the Keraunos logo only if you have permission; otherwise use a
neutral storm/lightning icon you are allowed to distribute.)

---

## 7. Submit to the HACS default store

1. Make sure step 2's validation workflows are green on your default branch.
2. Fork [`hacs/default`](https://github.com/hacs/default).
3. Edit the `integration` file and add your repo in the correct alphabetical
   position:
   ```
   your-github-username/keraunos-ha
   ```
4. Open a PR. The HACS bot runs automated checks; address any feedback.
5. After merge, **Keraunos Orages** appears in HACS for everyone without adding a
   custom repository.

---

## Maintenance checklist (every release)

- [ ] Update `version` in `manifest.json`.
- [ ] Commit and push.
- [ ] Create a matching git tag and GitHub release (`vX.Y.Z`).
- [ ] Confirm the validate workflow is green.

---

## References

- HACS publishing docs: https://hacs.xyz/docs/publish/start
- HACS integration requirements: https://hacs.xyz/docs/publish/integration
- HA integration manifest: https://developers.home-assistant.io/docs/creating_integration_manifest
- Brands repo: https://github.com/home-assistant/brands
