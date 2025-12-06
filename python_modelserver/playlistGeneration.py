import pandas as pd
import requests
<<<<<<< HEAD
import time 

df_audio = pd.read_csv('df_audio.csv')

=======
import time # Pour être un bon citoyen de l'API et ne pas la surcharger

# --- CONFIGURATION ---
# 🔧 Charger le CSV contenant les infos (pas de changement ici)
df_audio = pd.read_csv('df_audio.csv')

# 🔗 Extraire l'ID depuis le filename (pas de changement ici)
>>>>>>> ddd625d97fddd4a5e96fd9183369401ea3821d4f
def extract_id(filename):
    try:
        return int(filename.split('_')[0])
    except (IndexError, ValueError):
        return None

df_audio['id'] = df_audio['filename'].apply(extract_id)
<<<<<<< HEAD
df_audio.dropna(subset=['id'], inplace=True)
df_audio['id'] = df_audio['id'].astype(int)

def has_deezer_preview(track_id: int) -> bool:

    try:
        response = requests.get(f"https://api.deezer.com/track/{track_id}", timeout=5)
        response.raise_for_status()  

        data = response.json()

=======
# Supprimer les lignes où l'ID n'a pas pu être extrait
df_audio.dropna(subset=['id'], inplace=True)
df_audio['id'] = df_audio['id'].astype(int)


# --- NOUVELLE FONCTION DE VÉRIFICATION AUPRÈS DE DEEZER ---
def has_deezer_preview(track_id: int) -> bool:
    """
    Interroge l'API Deezer pour un ID de morceau donné et vérifie
    si un lien de preview non-vide existe.
    Retourne True si c'est le cas, False sinon.
    """
    try:
        # On utilise un timeout pour ne pas bloquer le serveur indéfiniment
        response = requests.get(f"https://api.deezer.com/track/{track_id}", timeout=5)
        response.raise_for_status()  # Lève une exception pour les erreurs HTTP (4xx, 5xx)

        data = response.json()

        # On vérifie si la clé 'preview' existe ET si sa valeur n'est pas une chaîne vide
>>>>>>> ddd625d97fddd4a5e96fd9183369401ea3821d4f
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
<<<<<<< HEAD
        print(f"❌ ID {track_id}: Réponse invalide ou morceau non trouvé sur Deezer.")
        return False

def find_valid_tracks(candidate_df: pd.DataFrame, num_required: int) -> list:
    valid_ids = []
=======
        # Si la réponse de l'API est inattendue (ex: ID non trouvé, clé 'error')
        print(f"❌ ID {track_id}: Réponse invalide ou morceau non trouvé sur Deezer.")
        return False

# --- NOUVELLE FONCTION D'AIDE POUR CONSTRUIRE LA PLAYLIST ---
def find_valid_tracks(candidate_df: pd.DataFrame, num_required: int) -> list:
    """
    Prend un DataFrame de morceaux candidats, les mélange, et vérifie un par un
    s'ils ont une preview Deezer jusqu'à en trouver le nombre requis.
    """
    valid_ids = []
    
    # Mélanger les candidats pour s'assurer que les résultats sont variés
>>>>>>> ddd625d97fddd4a5e96fd9183369401ea3821d4f
    shuffled_candidates = candidate_df.sample(frac=1)

    for _, row in shuffled_candidates.iterrows():
        track_id = int(row['id'])

        if has_deezer_preview(track_id):
            valid_ids.append(track_id)
<<<<<<< HEAD
            time.sleep(0.1) 
=======
            # Petite pause pour ne pas surcharger l'API Deezer (rate limiting)
            time.sleep(0.1) 

        # Si on a trouvé notre compte, on arrête la boucle pour gagner du temps
>>>>>>> ddd625d97fddd4a5e96fd9183369401ea3821d4f
        if len(valid_ids) == num_required:
            break
            
    return valid_ids

<<<<<<< HEAD
def playlist_generator_music(genre: str, mood: str):
=======
# --- FONCTIONS PRINCIPALES REFACTORISÉES ---

# 🎧 Générer une playlist en fonction du genre et du mood (MODIFIÉE)
def playlist_generator_music(genre: str, mood: str):
    # 1. Premier filtre, plus strict (genre + mood)
>>>>>>> ddd625d97fddd4a5e96fd9183369401ea3821d4f
    filtered_df = df_audio[
        (df_audio['genre'].str.lower() == genre.lower()) &
        (df_audio['mood'].str.lower().str.contains(mood.lower()))
    ]

    print(f"\n--- Recherche de 8 morceaux pour '{genre} {mood}' ---")
    print(f"{len(filtered_df)} candidats potentiels trouvés avec le genre et le mood.")
    
<<<<<<< HEAD
    final_playlist = find_valid_tracks(filtered_df, num_required=8)

    if len(final_playlist) < 8:
        needed = 8 - len(final_playlist)
        print(f"\nPas assez de morceaux valides. Il en manque {needed}. Élargissement de la recherche...")
=======
    # On utilise notre nouvelle fonction pour trouver des morceaux valides
    final_playlist = find_valid_tracks(filtered_df, num_required=8)

    # 2. Si on n'a pas 8 morceaux, on élargit la recherche (genre seul)
    if len(final_playlist) < 8:
        needed = 8 - len(final_playlist)
        print(f"\nPas assez de morceaux valides. Il en manque {needed}. Élargissement de la recherche...")
        
        # On prend les morceaux du même genre, en excluant ceux qu'on a déjà validés
>>>>>>> ddd625d97fddd4a5e96fd9183369401ea3821d4f
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

<<<<<<< HEAD
=======

# 🎧 Générer une playlist uniquement en fonction du mood (MODIFIÉE)
>>>>>>> ddd625d97fddd4a5e96fd9183369401ea3821d4f
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

<<<<<<< HEAD
=======

# 🔥 Exemple d'utilisation
print("Exemple avec genre et mood:")
final_list = playlist_generator_music("rock", "happy")
print("IDs retournés:", final_list)

print("\n" + "="*30 + "\n")

print("Exemple avec mood seul:")
final_list_mood = playlist_generator_mood("sad")
print("IDs retournés:", final_list_mood)
>>>>>>> ddd625d97fddd4a5e96fd9183369401ea3821d4f
