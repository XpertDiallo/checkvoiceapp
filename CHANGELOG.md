# Changelog

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
