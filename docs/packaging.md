# Packaging

<!-- prism:generate:breadcrumbs -->
[Prism Documentation](README.md) > Packaging
<!-- /prism:generate:breadcrumbs -->

## Pages

<!-- prism:generate:pages -->
- [Packaging](packaging.md)
- [Prism specification](SPEC.md)
- [Changelog](TODO.md)
<!-- /prism:generate:pages -->

## Steps for creating and installing the cli as a pip package

```powershell

# Build
uv build

# Install with system pip
pip install dist/prism-0.1.0-py3-none-any.whl # (Or whatever the build artifact name was)

```

You can then use it anywhere on your machine with just using the `prism` command.

## Aspirational steps for making Winget and Brew packages (doesn't currently work)

- Create binaries.

  ```cmd
  pyinstaller --onefile --name=prism .\src\prism\cli\prism.py
  ```

- Upload binaries to Github releases.
- Winget (`winget install prism-cli`)
  - Create a manifest:

    ```yaml
      Id: payneio.prism-cli
    Name: Prism CLI
    Publisher: PayneIO
    Version: 0.1.0
    License: MIT
    InstallerType: exe
    Installers:
      - Architecture: x64
        InstallerUrl: https://github.com/payneio/prism/releases/download/v0.1.0/prism-cli.exe
        InstallerSha256: <SHA256_HASH_OF_EXE>
    ```

  - Fork microsoft/winget-pkgs
  - Add your YAML file in the correct location
    (manifests/p/payneio/prism-cli/0.1.0.yaml)
  - Create a Pull Request

- Homebrew (`brew install payneio/tap/prism-cli`)
  - Create a formula:

    ```ruby
    class PrismCli < Formula
      desc "A powerful CLI tool for ..."
      homepage "https://github.com/payneio/prism"
      url "https://github.com/payneio/prism/releases/download/v0.1.0/prism-cli.tar.gz"
      sha256 "<SHA256_HASH>"
      license "MIT"

      def install
        bin.install "prism-cli"
      end

      test do
        system "#{bin}/prism-cli", "--version"
      end
    end
    ```

  - Create a tap: `brew tap payneio/tap`.
  - Add formula: `brew install --build-from-source ./prism-cli.rb`
  - Push to github.
  - Sumbit to homebrew.

<!-- prism:metadata
---
title: Packaging
path: packaging.md
generator_types:
  - breadcrumbs
  - pages
---
-->
