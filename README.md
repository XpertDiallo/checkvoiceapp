# CheckVoice

Application Streamlit de reconnaissance vocale, transcription audio longue duree et traduction.

## Nouveautes de cette version

- Choix obligatoire de la langue parlee avant transcription.
- Enregistrement vocal depuis le navigateur avec arret manuel par l'utilisateur.
- Lecture de l'audio enregistre avant transcription.
- Import de fichier audio avec detection automatique du format.
- Conversion et normalisation audio via `pydub` et `ffmpeg`.
- Transcription par segments pour mieux traiter les audios longs.
- Traduction de la transcription vers une langue choisie dans une liste deroulante.
- Interface modernisee: sidebar de parametres, onglets, boutons plus visibles, couleurs et cartes.
- Export du resultat complet au format `.txt`.

## Fonctionnalites

L'application propose deux parcours.

### Enregistrer

1. Choisir la langue parlee dans la liste.
2. Cliquer sur le champ d'enregistrement vocal Streamlit.
3. Parler aussi longtemps que necessaire.
4. Arreter l'enregistrement depuis le navigateur.
5. Ecouter l'audio si besoin.
6. Cliquer sur `Transcrire l'enregistrement`.
7. Lire la transcription et, si une langue cible a ete choisie, la traduction.

### Importer un audio

1. Choisir la langue parlee dans le fichier.
2. Charger un fichier audio.
3. Verifier le format detecte et ecouter l'audio.
4. Cliquer sur `Transcrire le fichier audio`.
5. Consulter la transcription, la traduction et telecharger le resultat.

Formats courants pris en charge: `wav`, `mp3`, `m4a`, `mp4`, `ogg`, `webm`, `flac`, `aac`, `aiff`.

## Langues disponibles

Langues de transcription incluses:

- Francais
- Anglais US et UK
- Espagnol
- Allemand
- Italien
- Portugais
- Arabe
- Neerlandais
- Turc
- Chinois simplifie
- Japonais

Langues de traduction incluses:

- Aucune traduction
- Francais
- Anglais
- Espagnol
- Allemand
- Italien
- Portugais
- Arabe
- Neerlandais
- Turc
- Chinois simplifie
- Japonais

## Installation locale

```bash
pip install -r requirements.txt
streamlit run appvoice.py
```

Pour la prise en charge des formats compresses comme MP3, M4A, OGG, WEBM ou FLAC, installez aussi `ffmpeg` sur la machine locale.

## Deploiement Streamlit Cloud

Le projet est pret pour Streamlit Cloud.

Fichiers importants:

- `appvoice.py`: application principale.
- `requirements.txt`: dependances Python.
- `packages.txt`: installe `ffmpeg` sur Streamlit Cloud.

Dans Streamlit Cloud, selectionner:

- Repository: `XpertDiallo/checkvoiceapp`
- Branch: `main`
- Main file path: `appvoice.py`

## Notes techniques

- La reconnaissance vocale utilise `SpeechRecognition` avec le service Google.
- La traduction utilise `deep-translator`.
- Les audios longs sont decoupes en segments configurables depuis la sidebar.
- L'enregistrement s'appuie sur `st.audio_input`, donc le micro est celui du navigateur de l'utilisateur.
- La reconnaissance et la traduction necessitent une connexion internet.

## Depannage

Si un format audio importe n'est pas lisible:

- verifier que le fichier audio n'est pas corrompu;
- verifier que `ffmpeg` est installe en local;
- sur Streamlit Cloud, verifier que `packages.txt` contient bien `ffmpeg`.

Si aucune parole n'est reconnue:

- verifier que la langue source choisie correspond a la langue parlee;
- tester avec un audio plus clair;
- reduire le bruit de fond;
- augmenter le volume de la voix.
