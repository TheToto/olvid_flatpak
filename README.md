# Olvid Flatpak (non officiel)

Ce dépôt empaquette **Olvid Desktop** (à partir de l'archive Linux officielle `https://static.olvid.io/linux/olvid-<version>.tar.gz`) au format **Flatpak**, avec :
- Un dépôt OSTree publié automatiquement sur **GitHub Pages** (`olvid.flatpakrepo` et `io.olvid.Olvid.flatpakref`) pour que `flatpak update` mette à jour l'application automatiquement.
- Des **GitHub Releases** contenant à la fois le fichier `.flatpakref` et le bundle autonome `.flatpak`.
- Une vérification quotidienne automatique des nouvelles versions via le flux RSS officiel d'Olvid, qui ouvre une Pull Request prête à fusionner.

---

## Installer Olvid

### Option 1 : Via `.flatpakref` (recommandé, mises à jour automatiques)
Téléchargez `io.olvid.Olvid.flatpakref` depuis la page GitHub Pages ou depuis la dernière [GitHub Release](../../releases/latest), puis :

```bash
flatpak install --user io.olvid.Olvid.flatpakref
```

Ensuite, les mises à jour se font normalement avec :

```bash
flatpak update
```

### Option 2 : Via le bundle `.flatpak` autonome
Téléchargez `io.olvid.Olvid-<version>-x86_64.flatpak` depuis les [GitHub Releases](../../releases/latest) :

```bash
flatpak install --user io.olvid.Olvid-<version>-x86_64.flatpak
```

---

## Configuration initiale sur GitHub (à faire une seule fois)

Après avoir poussé ce dépôt sur GitHub :

### 1. Activer GitHub Pages
Dans **Settings → Pages → Build and deployment → Source**, sélectionnez **GitHub Actions**.

### 2. Autoriser les Pull Requests automatiques
Dans **Settings → Actions → General → Workflow permissions**, cochez **Allow GitHub Actions to create and approve pull requests** (nécessaire pour que le workflow quotidien puisse ouvrir les PR de mise à jour).

### 3. Configurer la signature GPG (fortement recommandé)
Flatpak vérifie les signatures GPG par défaut lors de l'installation d'un `.flatpakref` et lors de `flatpak update`. Sans clé GPG, les utilisateurs devraient passer `--no-gpg-verify` manuellement.

Générez une clé GPG dédiée (sans phrase secrète pour la CI) :

```bash
gpg --batch --passphrase '' --quick-generate-key "Olvid Flatpak Repo <noreply@example.com>" rsa4096 sign never
```

Récupérez l'empreinte de la clé et exportez la clé privée :

```bash
gpg --list-secret-keys --keyid-format=long
gpg --armor --export-secret-keys <ID_DE_LA_CLE>
```

Dans **Settings → Secrets and variables → Actions → New repository secret**, créez le secret :
- Name : `GPG_PRIVATE_KEY`
- Value : tout le bloc `-----BEGIN PGP PRIVATE KEY BLOCK----- ... -----END PGP PRIVATE KEY BLOCK-----`

---

## Mise à jour manuelle (si besoin)

Vous pouvez déclencher le workflow **Check for Olvid Updates** depuis l'onglet **Actions**, ou mettre à jour localement avec :

```bash
python3 scripts/check_update.py
```

(ou `--version X.Y.Z` pour forcer une version précise).
