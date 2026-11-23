# Olvid Flatpak (non officiel)

Empaquetage Flatpak d'**Olvid Desktop** à partir de l'archive Linux officielle, avec mises à jour automatiques.

## Installation

### Recommandé (avec mises à jour automatiques)
1. [Télécharger `io.olvid.Olvid.flatpakref`](https://thetoto.github.io/olvid_flatpak/io.olvid.Olvid.flatpakref) et l'ouvrir avec votre boutique d'applications (GNOME Software, KDE Discover…).
2. Ou en ligne de commande :
```bash
flatpak install --user https://thetoto.github.io/olvid_flatpak/io.olvid.Olvid.flatpakref
```

Mettre à jour ensuite avec :
```bash
flatpak update
```

### Bundle autonome (hors-ligne)
Téléchargez le fichier `.flatpak` depuis les [Releases](https://github.com/TheToto/olvid_flatpak/releases/latest) :
```bash
flatpak install --user io.olvid.Olvid-*-x86_64.flatpak
```
