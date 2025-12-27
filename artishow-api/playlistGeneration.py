import requests
import random

# Fonction utilitaire pour chercher des playlists et extraire des tracks
def fetch_tracks_from_deezer_query(query, limit=4):
    """
    Cherche une playlist correspondant à la requête (ex: 'Rock Sad'),
    et récupère 'limit' morceaux valides (avec preview).
    """
    print(f"🔎 Recherche Deezer pour : '{query}'")
    
    try:
        # 1. Chercher des playlists
        search_url = "https://api.deezer.com/search/playlist"
        params = {'q': query, 'limit': 15} # On en prend 15 pour avoir du choix
        resp = requests.get(search_url, params=params)
        playlists = resp.json().get('data', [])

        if not playlists:
            print(f"❌ Aucune playlist trouvée pour '{query}'")
            return []

        # 2. Choisir une playlist aléatoire (pour varier les résultats à chaque fois)
        # On évite les playlists vides ou nulles
        valid_playlists = [p for p in playlists if p.get('nb_tracks', 0) > 5]
        
        if not valid_playlists:
            valid_playlists = playlists # Fallback

        selected_playlist = random.choice(valid_playlists)
        playlist_id = selected_playlist['id']
        playlist_title = selected_playlist['title']
        print(f"📂 Playlist sélectionnée : {playlist_title} (ID: {playlist_id})")

        # 3. Récupérer les pistes de cette playlist
        tracks_url = f"https://api.deezer.com/playlist/{playlist_id}/tracks"
        # On en demande 50 pour être sûr d'en avoir assez avec des previews
        tracks_resp = requests.get(tracks_url, params={'limit': 50})
        tracks_data = tracks_resp.json().get('data', [])

        # 4. Filtrer les pistes qui ont une PREVIEW valide
        valid_tracks_ids = []
        for t in tracks_data:
            if t.get('preview') and t.get('readable', True):
                valid_tracks_ids.append(t['id'])
                if len(valid_tracks_ids) >= limit:
                    break
        
        print(f"✅ {len(valid_tracks_ids)} titres récupérés.")
        return valid_tracks_ids

    except Exception as e:
        print(f"🔥 Erreur Deezer sur '{query}': {e}")
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
    # Si le genre2 est le même ou 'Unknown', on change la stratégie
    if genre2 and genre2.lower() != "unknown" and genre2 != genre1:
        q2 = f"{genre2} {mood}"
        tracks2 = fetch_tracks_from_deezer_query(q2, limit=4)
        final_playlist.extend(tracks2)
    else:
        # Si pas de 2ème genre, on complète avec le Genre 1 mais une playlist différente (si possible)
        # Ou on cherche juste le Mood pour varier
        print("⚠️ Pas de 2ème genre distinct, on complète avec le Mood seul.")
        q_fallback = f"{mood} vibe"
        tracks_fallback = fetch_tracks_from_deezer_query(q_fallback, limit=8 - len(final_playlist))
        final_playlist.extend(tracks_fallback)

    # 3. S'il manque des titres (ex: playlists vides), on comble avec juste le Genre 1
    if len(final_playlist) < 8:
        missing = 8 - len(final_playlist)
        print(f"⚠️ Manque {missing} titres. Recherche de secours sur '{genre1}'...")
        extras = fetch_tracks_from_deezer_query(f"Best of {genre1}", limit=missing)
        final_playlist.extend(extras)

    # Mélanger pour ne pas avoir bloc A puis bloc B
    random.shuffle(final_playlist)
    
    # On coupe à 8 titres max
    return final_playlist[:8]

def playlist_generator_mood(mood):
    """
    Génère une playlist basée uniquement sur le Mood (pour la fonctionnalité texte)
    """
    print(f"\n--- Génération 100% Mood : {mood} ---")
    
    # On essaie de récupérer 8 titres
    # On peut faire 2 requêtes pour varier les plaisirs
    
    tracks = fetch_tracks_from_deezer_query(f"{mood} mood", limit=8)
    
    if len(tracks) < 8:
        # Fallback si requête trop précise
        extras = fetch_tracks_from_deezer_query(f"{mood} music", limit=8 - len(tracks))
        tracks.extend(extras)

    return tracks[:8]