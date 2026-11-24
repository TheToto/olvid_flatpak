# AGENTS.md

Instructions pour les agents travaillant sur ce dépôt (`olvid_flatpak`).

## Règles strictes

- **Pas de `git push` automatique** : ne jamais exécuter `git push` (ni modifier l'historique distant) sans l'autorisation explicite de l'utilisateur.
- **Aucun secret en clair** : ne jamais écrire de mot de passe, clé privée GPG ou token dans les fichiers du dépôt.

## Structure du dépôt

- `io.olvid.Olvid.yml` : manifeste Flatpak (`org.freedesktop.Platform` / `org.freedesktop.Sdk` `25.08`, `x86_64`).
- `io.olvid.Olvid.desktop` : lanceur bureau et schémas d'URI (`olvid://`, `olvid.openid://`).
- `io.olvid.Olvid.metainfo.xml` : métadonnées AppStream et historique des versions.
- `scripts/check_update.py` : vérification des nouvelles versions Linux via le flux RSS officiel (`https://olvid.io/rss/en.xml`) et mise à jour du manifeste / metainfo.
- `.github/workflows/build-and-publish.yml` : build OSTree signé GPG, déploiement GitHub Pages (`.flatpakrepo`, `.flatpakref`, `repo/`) et publication GitHub Release (`.flatpak`).
- `.github/workflows/check-update.yml` : vérification quotidienne ouvrant une PR en cas de nouvelle version.

## Notes techniques

- **Accès fichiers (`--filesystem=home`)** : Olvid utilise JavaFX 21 dont le sélecteur de fichiers GTK3 (`GtkFileChooserDialog`) ne passe pas par `xdg-desktop-portal` (`GTK_USE_PORTAL=1` est ignoré). L'accès `home` est donc nécessaire pour ouvrir/enregistrer des fichiers hors de `Downloads`.
- **Variables X11** : `--socket=x11` et `--env=GDK_BACKEND=x11` sont requis pour le bon fonctionnement de JavaFX.

## Commandes utiles en local

```bash
# Compiler et installer en --user
flatpak run org.flatpak.Builder --user --install -y --force-clean build-dir io.olvid.Olvid.yml

# Lancer l'application
flatpak run io.olvid.Olvid

# Vérifier les mises à jour sans modifier les fichiers
python3 scripts/check_update.py --dry-run

# Valider les métadonnées
desktop-file-validate io.olvid.Olvid.desktop
appstreamcli validate --no-net --explain io.olvid.Olvid.metainfo.xml
```
