# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2023-03-07

### Added
- `to_dict()` method and `from_dict()` class method to osm_object_primitive. (An object that is inherited by a Node, Way, Relation). [#3](https://github.com/docentYT/osm_easy_api/issues/3)
- Support for historical anonymous edits and edits made by deleted accounts. [#4](https://github.com/docentYT/osm_easy_api/issues/4)

## [0.1.4] - 2023-03-05

### Fixed
- Improvement of utils.join_url() function.
- Spelling errors corrected [@matkoniecz](https://github.com/matkoniecz)

## [0.1.3] - 2023-03-03

### Fixed

- Fixed the non-setting of the "visible" attribute.

## [0.1.2] - 2023-03-03

### Fixed

- Fixed return type of generator in Diff.get() method.

## [0.1.1] - 2023-03-03

### Added

- License

## [0.1.0] - 2023-03-03

### Added

- Initial import