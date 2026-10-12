# Installation and Upgrade

All implementation is contained in `masar_mce_hrms`. The app requires ERPNext and compatible HRMS on the bench. HRMS must be available before app installation; Frappe checks declared app dependencies.

## Existing or Partially Installed Site

Deploy this app version and ensure HRMS is installed on the target site. Run:

```bash
bench --site stg-erp.mce.com list-apps
```

If `masar_mce_hrms` is listed, run:

```bash
bench --site stg-erp.mce.com migrate
```

Otherwise run:

```bash
bench --site stg-erp.mce.com install-app masar_mce_hrms
```

Do not use `--force` or manually add database columns. Installation configures Employee after fixture synchronization through Frappe's `after_sync` hook. Migration runs the same setup after fixture synchronization through `after_migrate`.

## Age Rename

The pre-install/pre-migration hook migrates `custom_agg` to `custom_age`, preserves Age values, and updates layout/report references. It refuses conflicting values when both fields exist. The old metadata is removed; Frappe retains the old physical column rather than destructively dropping data.

Setup validates required columns before querying numeric values. Missing fixture/schema dependencies and invalid numeric data produce explicit errors rather than being silently skipped.

## Data Preservation

Installation and migration do not remap Category values, number existing Employees, or backfill service durations. New Employees receive an automatic sequence greater than the existing maximum. Durations retain their existing on-load/on-save and daily-refresh behaviour.

The existing Penalties child DocType is bundled because the Employee fixtures reference it. This is an existing dependency, not a new lookup DocType.

## Source Organization

- `overrides/`: Employee controller extending HRMS.
- `customization/`: Employee fields, Select configuration, and layout application.
- `configuration/`: supplied Select values.
- `services/`: duration calculations and immutable log snapshots.
- `dashboards/`: Employee dashboard connections.
- `patches/`: data-preserving field migrations.
- `tests/`: verification and regression tests.
- `fixtures/`: portable DocType, Custom Field and Property Setter metadata.

## Verification

```bash
bench --site mce.local execute masar_mce_hrms.tests.deployment.run
bench --site mce.local execute masar_mce_hrms.tests.verification.run
```
