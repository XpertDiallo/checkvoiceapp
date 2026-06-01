# Changelog

## 2.0.3 - 2026-06-01

### Corrige

- Correction du cache des zones de texte Streamlit: la traduction affichée change maintenant réellement quand la langue cible ou la transcription change.
- Empêche l'affichage d'une ancienne traduction sous un nouveau libellé de langue.

## 2.0.2 - 2026-06-01

### Corrige

- Retraduction automatique d'une transcription existante lorsque la langue cible est modifiée après l'enregistrement ou l'import audio.
- Ajout d'une version de traduction en session pour éviter l'affichage d'une ancienne traduction avec un nouveau libellé de langue.

## 2.0.1 - 2026-06-01

### Corrige

- Correction de la traduction qui pouvait renvoyer le texte source sans erreur.
- Utilisation explicite de la langue source choisie pour traduire.
- Ajout d'un fallback Google Translate quand le premier moteur renvoie une traduction identique au texte original.
- Conservation de la transcription même si la traduction est temporairement indisponible.

## 2.0.0 - 2026-06-01

### Ajoute

- Enregistrement vocal depuis le navigateur avec arret manuel.
- Selection de la langue source avant l'enregistrement ou l'import audio.
- Import audio multi-format avec detection automatique.
- Transcription des audios longs par segments.
- Traduction optionnelle dans une langue choisie par liste deroulante.
- Export texte du resultat complet.
- Documentation de deploiement Streamlit Cloud.

### Ameliore

- Interface modernisee avec sidebar, onglets, cartes et couleurs.
- Ergonomie de lecture audio avant transcription.
- Gestion des erreurs de format audio et de reconnaissance vocale.

### Modifie

- Remplacement de `googletrans` par `deep-translator`.
- Ajout de `pydub` et `ffmpeg` pour la conversion audio.
- Suppression de l'ancien flux microphone serveur limite a 60 secondes.
