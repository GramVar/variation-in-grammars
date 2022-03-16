{pkgs ? import <nixpkgs> {}}:
with pkgs; let
  dev = ps: [ps.black ps.mypy ps.pylint ps.flake8];
  deps = ps: [ps.pdftotext];
in
  mkShell {
    packages = [(python3.withPackages (ps: (deps ps) ++ (dev ps)))];
  }
