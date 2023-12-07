with import <nixpkgs> {};
(python311.withPackages (ps: with ps; [
  python311Packages.yt-dlp
  pytelegrambotapi
  requests
  pip
])).env
