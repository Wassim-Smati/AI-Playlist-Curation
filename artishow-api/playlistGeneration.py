import requests
import random

# Fonction utilitaire pour chercher des playlists et extraire des tracks
def fetch_tracks_from_deezer_query(query, limit=4):
    """
    Cherche une playlist correspondant à la requête (ex: 'Rock Sad'),
    et récupère 'limit' morceaux valides (avec preview).
    """
    print(f"  🔎 Deezer : Recherche pour '{query}'", flush=True)
    
    try:
        # 1. Chercher des playlists
        search_url = "https://api.deezer.com/search/playlist"
        params = {'q': query, 'limit': 15}
        resp = requests.get(search_url, params=params, timeout=5)
        playlists = resp.json().get('data', [])

        if not playlists:
            print(f"  ❌ Aucune playlist trouvée pour '{query}'", flush=True)
            return []

        # 2. Choisir une playlist aléatoire
        valid_playlists = [p for p in playlists if p.get('nb_tracks', 0) > 5]
        if not valid_playlists:
            valid_playlists = playlists

        selected_playlist = random.choice(valid_playlists)
        playlist_id = selected_playlist['id']
        playlist_title = selected_playlist.get('title', 'Unknown')
        print(f"  📂 Playlist Deezer : \"{playlist_title}\" (ID: {playlist_id})", flush=True)

        # 3. Récupérer les pistes de cette playlist
        tracks_url = f"https://api.deezer.com/playlist/{playlist_id}/tracks"
        tracks_resp = requests.get(tracks_url, params={'limit': 50}, timeout=5)
        tracks_data = tracks_resp.json().get('data', [])

        # 4. Filtrer les pistes avec PREVIEW valide
        valid_tracks_ids = []
        for t in tracks_data:
            if t.get('preview') and t.get('readable', True):
                valid_tracks_ids.append(t['id'])
                if len(valid_tracks_ids) >= limit:
                    break
        
        print(f"  ✅ {len(valid_tracks_ids)} titres récupérés avec preview.", flush=True)
        return valid_tracks_ids

    except Exception as e:
        print(f"  🔥 Erreur Deezer sur '{query}': {e}", flush=True)
        return []

def playlist_generator_music(genre1, genre2, mood):
    """
    Génère une playlist de 8 titres :
    - 4 titres basés sur Genre1 + Mood
    - 4 titres basés sur Genre2 + Mood
    """
    final_playlist = []
    
    # 1. Recherche Principale (Genre 1 + Mood) -> 4 titres
    q1 = f"{genre1} {mood}"
    tracks1 = fetch_tracks_from_deezer_query(q1, limit=4)
    final_playlist.extend(tracks1)

    # 2. Recherche Secondaire (Genre 2 + Mood) -> 4 titres
    if genre2 and genre2.lower() != "unknown" and genre2 != genre1:
        q2 = f"{genre2} {mood}"
        tracks2 = fetch_tracks_from_deezer_query(q2, limit=4)
        final_playlist.extend(tracks2)
    else:
        print("  ℹ️ Pas de 2ème genre distinct, complément via mood.", flush=True)
        q_fallback = f"{mood} vibe"
        tracks_fallback = fetch_tracks_from_deezer_query(q_fallback, limit=8 - len(final_playlist))
        final_playlist.extend(tracks_fallback)

    # 3. S'il manque des titres, recherche de secours
    if len(final_playlist) < 8:
        missing = 8 - len(final_playlist)
        print(f"  ⚠️ Manque {missing} titres. Recherche de secours sur '{genre1}'...", flush=True)
        extras = fetch_tracks_from_deezer_query(f"Best of {genre1}", limit=missing)
        final_playlist.extend(extras)

    # Mélanger pour alterner
    random.shuffle(final_playlist)
    return final_playlist[:8]

def playlist_generator_mood(mood):
    """
    Génère une playlist basée uniquement sur le Mood (pour la fonctionnalité texte)
    """
    print(f"  🎭 Génération 100% Mood : {mood}", flush=True)
    tracks = fetch_tracks_from_deezer_query(f"{mood} mood", limit=8)
    
    if len(tracks) < 8:
        extras = fetch_tracks_from_deezer_query(f"{mood} music", limit=8 - len(tracks))
        tracks.extend(extras)

    return tracks[:8]