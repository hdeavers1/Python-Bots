External JS Scripts Setup Guide
To download from YouTube, yt-dlp needs to solve JavaScript challenges presented by YouTube using an external JavaScript runtime.

This involves running challenge solver scripts maintained at yt-dlp-ejs. Depending on your yt-dlp installation method, you may need to set up and enable these components manually.

This guide will help you set up and enable the necessary components based on your yt-dlp installation method.

Note

EJS replaces the prior JSInterp and PhantomJS based approach. For YouTube both are no longer used. PhantomJS is still being used for a few other extractors, but is planned to be deprecated in the near future.

Setup steps
Install a supported JavaScript runtime
Install EJS challenge solver scripts
Step 1: Install a supported JavaScript Runtime
JS Runtime	Summary
Deno (recommended)	Enabled by default.
Node	Enable with --js-runtimes node
Bun	Enable with --js-runtimes bun
QuickJS	Enable with --js-runtimes quickjs
deno
Tip

Recommended

https://deno.com

Installation instructions
Minimum supported version: 2.0.0

Download from https://docs.deno.com/runtime/getting_started/installation/ or from your package manager.

When grabbing deno manually from the Github release assets you will need to download deno and not denort.

Enable
Deno is enabled by default. To supply an optional path, use --js-runtimes deno:/path/to/deno

Notes
Code is run with restricted permissions (e.g, no file system or network access)
Supports downloading EJS script dependencies from npm (--remote-components ejs:npm).
node
https://nodejs.org

Installation instructions
Minimum supported version: 20.0.0

Download from https://nodejs.org/en/download/ or from your package manager.

Enable
Enable with --js-runtimes node or --js-runtimes node:/path/to/node.

It is recommended to add this to your yt-dlp configuration file to avoid needing to pass it every time.

Notes
Runs code with some permissions restricted.
bun
https://bun.com

Installation instructions
Minimum supported version: 1.0.31

Download from https://bun.com/docs/installation or from your package manager.

Enable
Enable with --js-runtimes bun or --js-runtimes bun:/path/to/bun.

It is recommended to add this to your yt-dlp configuration file to avoid needing to pass it every time.

Notes
No permission restrictions available. Scripts have full file system and network access.
Supports downloading EJS script dependencies from npm (--remote-components ejs:npm).
No support for SOCKS proxies when downloading EJS script dependencies from npm.
QuickJS / QuickJS-NG
https://bellard.org/quickjs/ / https://quickjs-ng.github.io/quickjs/

Installation instructions
Minimum supported QuickJS version: 2023-12-9

All versions of QuickJS-NG are supported.

Download from https://bellard.org/quickjs/ / https://quickjs-ng.github.io/quickjs/installation or from your package manager.

Enable
Enable with --js-runtimes quickjs or --js-runtimes quickjs:/path/to/qjs.

It is recommended to add this to your yt-dlp configuration file to avoid needing to pass it every time.

Notes
QuickJS versions prior to 2025-4-26 are missing optimizations which can lead to execution times of several minutes.
All QuickJS-NG versions are missing optimizations which can lead to execution times of several minutes.
Both QuickJS and QuickJS-NG do not fully allow executing files from stdin, so yt-dlp will create temporary files for each EJS script execution. This can theoretically lead to time-of-check to time-of-use (TOCTOU) vulnerabilities.
Step 2: Install EJS challenge solver scripts
yt-dlp distribution	EJS scripts installation options
Official PyInstaller-bundled executable (e.g. yt-dlp.exe, yt-dlp_macos, yt-dlp_linux, etc)	No additional action required. All the necessary JavaScript components will be bundled with these executables.
PyPI package (e.g. installed with pip, pipx, etc):	- Install and upgrade yt-dlp with default dependency group
- or enable npm downloads (deno/bun only)
- or enable GitHub downloads
Official zipimport binary (the yt-dlp Unix executable)	No additional action required. All the necessary JavaScript components will be bundled with these executables.
Third-party package users (e.g. installed with pacman, brew, etc)	The will depend on if your third-party package repository ships or bundles the EJS script package with yt-dlp.

If it does not (or it is out of date):
- enable npm downloads (deno/bun only)
- or enable GitHub downloads
Option 1: Install the yt-dlp-ejs python package
yt-dlp ships a companion package, yt-dlp-ejs, which contains all the EJS scripts.

If you installed yt-dlp using the PyPI package (e.g. with pip or pipx), install and upgrade yt-dlp with the default dependency group:

i.e. pip install -U "yt-dlp[default]"

The default dependency group includes the yt-dlp-ejs package.

Refer to https://github.com/yt-dlp/yt-dlp/wiki/Installation#with-pip for more details.

Alternatively, if you only want to install the EJS package, you can install the yt-dlp-ejs package directly from PyPI. The version MUST match the version specified in yt-dlp's pyproject.toml for the version of yt-dlp you are using.

Warning

This library SHOULD be updated alongside yt-dlp to avoid running an outdated version. The version MUST be a supported version as per yt-dlp's pyproject.toml file. yt-dlp may bump the minimum version on updates without warning, and old versions will be ignored by yt-dlp.

Option 2: Enable EJS script downloads from npm
Important

This option only works with Deno and Bun runtimes, which support downloading npm packages on-the-fly.

To enable this, supply --remote-components ejs:npm to yt-dlp. It is recommended to add this to your yt-dlp configuration file to avoid needing to pass it every time and allow automatic updates.

Option 3: Enable EJS script downloads from GitHub
yt-dlp can automatically download the EJS scripts directly from GitHub (https://github.com/yt-dlp/ejs).

To enable this, supply --remote-components ejs:github to yt-dlp. It is recommended to add this to your yt-dlp configuration file to avoid needing to pass it every time and allow automatic updates.

Note

This method may not work if GitHub and GitHub release assets are not accessible from your network. This includes if you are using yt-dlp with a IPv6 IP-only (e.g., --force-ipv6)

Plugins
You can install alternatives to the built-in JS challenge solvers through plugins.

Featured Plugins:
yt-dlp-apple-webkit-jsi by grqz
Experimental Apple WebKit JS Challenge Provider plugin for yt-dlp. Should work on most Apple devices. Maintained by a yt-dlp maintainer
Check out the yt-dlp-jsc-provider GitHub topic for more JSC Provider plugins.

For developers, refer to the JSC Provider developer documentation

Please note: Currently only the base JavaScript Challenge Provider API is public. The API to hook into yt-dlp's EJS scripts is private at this time due to ongoing development with potential breaking changes; it may be made public in the future.
Pages 9
Find a page or section…
Home
EJS
External JS Scripts Setup Guide
Setup steps
Step 1: Install a supported JavaScript Runtime
deno
Installation instructions
Enable
Notes
node
Installation instructions
Enable
Notes
bun
Installation instructions
Enable
Notes
QuickJS / QuickJS-NG
Installation instructions
Enable
Notes
Step 2: Install EJS challenge solver scripts
Option 1: Install the yt-dlp-ejs python package
Option 2: Enable EJS script downloads from npm
Option 3: Enable EJS script downloads from GitHub
Plugins
Featured Plugins:
Extractors
FAQ
Forks
Installation
Plugin Development
Plugins
PO Token Guide
Clone this wiki locally
https://github.com/yt-dlp/yt-dlp.wiki.git
Footer
© 2026 GitHub, Inc.
Footer navigation
Terms
Privacy
Security
Status
Community
Docs
Contact
Manage cookies