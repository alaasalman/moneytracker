# Money Tracker Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/) and this project adheres to [Semantic Versioning](http://semver.org/).

## [Unreleased]

## [1.0.2] - 2020-04-22
### Changed
- Split up the Vue components and removed the charts into their own bundle to make the bundles smaller.
- General fixes for typos and styles.

## [1.0.1] - 2020-04-17
### Added
- Added this changelog to start keeping track of releases and functionality.
- Lots of tests which should make the codebase a bit more stable moving forward. At the very least, I can upgrade libraries with more peace of mind.
- JS errors should now be reported to Sentry.io.
- A visual indicator for required fields in forms.

### Changed
- Upgrades all around, most notable moved to Django version 2.2.
- Started versioning from 1.0.1 after publicly releasing the source code; after many years of private development.
- The UI is now more consistent and hopefully prettier after a round of CSS fixes and modifying markup to work with the newer Bulma version.
- Account last transaction date now finally shows on the account listing page.
- The dashboard is now showing much more useful information about current month's spending vs last month's.

### Removed
- The TransactionTag model hasn't been used for quite a while and is now removed.

