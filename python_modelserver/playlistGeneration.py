import pandas as pd
import requests
import time 

df_audio = pd.read_csv('df_audio.csv')

def extract_id(filename):
    try:
        return int(filename.split('_')[0])
    except (IndexError, ValueError):
        return None

df_audio['id'] = df_audio['filename'].apply(extract_id)
df_audio.dropna(subset=['id'], inplace=True)
df_audio['id'] = df_audio['id'].astype(int)

def has_deezer_preview(track_id: int) -> bool:

    try:
        response = requests.get(f"https://api.deezer.com/track/{track_id}", timeout=5)
        response.raise_for_status()  

        data = response.json()

        if 'preview' in data and data['preview']:
            print(f"✅ ID {track_id}: Preview trouvée.")
            return True
        else:
            print(f"❌ ID {track_id}: Pas de preview.")
            return False

    except requests.exceptions.RequestException as e:
        print(f"🔥 Erreur API pour l'ID {track_id}: {e}")
        return False
    except KeyError:
        print(f"❌ ID {track_id}: Réponse invalide ou morceau non trouvé sur Deezer.")
        return False

def find_valid_tracks(candidate_df: pd.DataFrame, num_required: int) -> list:
    valid_ids = []
    shuffled_candidates = candidate_df.sample(frac=1)

    for _, row in shuffled_candidates.iterrows():
        track_id = int(row['id'])

        if has_deezer_preview(track_id):
            valid_ids.append(track_id)
            time.sleep(0.1) 
        if len(valid_ids) == num_required:
            break
            
    return valid_ids

def playlist_generator_music(genre: str, mood: str):
    filtered_df = df_audio[
        (df_audio['genre'].str.lower() == genre.lower()) &
        (df_audio['mood'].str.lower().str.contains(mood.lower()))
    ]

    print(f"\n--- Recherche de 8 morceaux pour '{genre} {mood}' ---")
    print(f"{len(filtered_df)} candidats potentiels trouvés avec le genre et le mood.")
    
    final_playlist = find_valid_tracks(filtered_df, num_required=8)

    if len(final_playlist) < 8:
        needed = 8 - len(final_playlist)
        print(f"\nPas assez de morceaux valides. Il en manque {needed}. Élargissement de la recherche...")
        genre_df = df_audio[
            (df_audio['genre'].str.lower() == genre.lower()) &
            (~df_audio['id'].isin(final_playlist))
        ]
        
        print(f"{len(genre_df)} candidats supplémentaires trouvés avec seulement le genre.")
        
        if not genre_df.empty:
            extra_ids = find_valid_tracks(genre_df, num_required=needed)
            final_playlist.extend(extra_ids)

    if not final_playlist:
        print(f"Aucun morceau valide trouvé pour le genre '{genre}' et le mood '{mood}'.")

    print(f"\n✅ Playlist finale générée avec {len(final_playlist)} morceaux.")
    return final_playlist

def playlist_generator_mood(mood: str):
    filtered_df = df_audio[
        df_audio['mood'].str.lower().str.contains(mood.lower())
    ]
    
    print(f"\n--- Recherche de 8 morceaux pour le mood '{mood}' ---")
    print(f"{len(filtered_df)} candidats potentiels trouvés.")

    if filtered_df.empty:
        print(f"Aucun morceau trouvé pour le mood '{mood}'.")
        return []

    final_playlist = find_valid_tracks(filtered_df, num_required=8)

    print(f"\n✅ Playlist finale générée avec {len(final_playlist)} morceaux.")
    return final_playlist

