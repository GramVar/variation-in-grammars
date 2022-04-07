{pkgs ? import <nixpkgs> {}}:
with pkgs; let
  dev = ps: [ps.black ps.isort ps.mypy ps.pylint ps.flake8];
  deps = ps: [ps.matplotlib];
in
  mkShell {
    packages = [(python3.withPackages (ps: (deps ps) ++ (dev ps)))];
  }
