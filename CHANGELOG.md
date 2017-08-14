# Change Log
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## [0.1.3] - 2017-08-13
### Fixed
- bug that created multiple entries per nick

## [0.1.2] - 2017-07-23
### Fixed
- misnamed variable in user_joined hook
- make find_alias return, at minimum, the requested nick in a list

## [0.1.1] - 2017-05-29
### Added
- track nick that join channel
- only allow ops to invoke
- add docstrings
- nick list merging

## [0.1.0] - 2017-04-16
### Added
- added alias data structure that will be saved in mongodb
- track nick changes
- allow manually editing of aliases via irc command
- output entire alias table, or just aliases for one nick
