with import <nixpkgs> {};
(python310.withPackages (ps: with ps; [
  pytelegrambotapi
  requests
  pip
])).env
