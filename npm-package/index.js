// This file is required for npm packages but we're using cli.js as the main entry point
// for the executable. This file just exports the version number.

module.exports = {
  version: require('./package.json').version
};
