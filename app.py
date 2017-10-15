import spotipy
import spotipy.oauth2 as oauth
import datetime
import auth as tsa
import pprint
import requests
from flask import Flask, request, session, redirect, render_template,jsonify

app = Flask(__name__, static_url_path='')
app.config['DEBUG'] = True
app.secret_key = 'tiptone'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 604800


musimap = {'id':'aqwo4qett8c1s1ah','secret':'9yobvlm1mmnrkrxafysa1oaq28mfjdfi'}
url = 'https://api.musimap.net/oauth/access_token'
grant_type = 'client_credentials'
musimap_data = requests.post(url,data={'grant_type':grant_type,'client_id':musimap['id'],'client_secret':musimap['secret']})
SPOTIFY_INFO = {
    'id':'4f8c3338b0b443a8895358db33763c6f',
    'secret':'76cf6ff10bb041dbb0b11a3e7dd89fe1'
}
@app.route('/')
def index():
    session.permanent = True
    pprint.pprint(session)
    return render_template('index.html')

@app.route('/data', methods=['POST'])
def data():
    track_one_artist = request.json[0][0]['value']
    track_one_track = request.json[0][1]['value']
    track_two_artist = request.json[1][0]['value']
    track_two_track = request.json[1][1]['value']
    sp_token = oauth.SpotifyClientCredentials(client_id='4f8c3338b0b443a8895358db33763c6f',client_secret='76cf6ff10bb041dbb0b11a3e7dd89fe1')
    spotify_client = spotipy.Spotify(auth=sp_token.get_access_token())
    results = spotify_client.search(q='artist:'+track_one_artist + ' AND ' + 'track:'+track_one_track, type='track')
    if len(results['tracks']['items'])>0:
        data_one = {
            'sp_uri':results['tracks']['items'][0]['id'],
            'track': results['tracks']['items'][0]['name'],
            'artist': results['tracks']['items'][0]['artists'][0]['name']
        }

    results = spotify_client.search(q='artist:'+track_two_artist + ' AND ' + 'track:'+track_two_track, type='track')
    if len(results['tracks']['items'])>0:
        data_two = {
            'sp_uri':results['tracks']['items'][0]['id'],
            'track': results['tracks']['items'][0]['name'],
            'artist': results['tracks']['items'][0]['artists'][0]['name']
        }
    audio = spotify_client.audio_features(tracks=[data_one['sp_uri'],data_two['sp_uri']])
    recommendations = spotify_client.recommendations(seed_tracks=[data_one['sp_uri'],data_two['sp_uri']],limit=12)
    recommendations = recommendations['tracks']
    pprint.pprint(recommendations)
    recommendations_ids = []
    for i in recommendations:
        recommendations_ids.append(i['id'])
    personal_client = spotipy.Spotify(auth='BQDJ_B0q8yzcHfpFWLQjlI8ZVTreeaM3LIetawcg5czMV3z7sX17ts-bgECuudXm3Y2uog57iluGNyYJZ6mk2bqyc8Bd9jFJ87cd6m8ZazF9_dzP2AhGtC5hA7nFjSA9VrwscCxzYZ5g4cjVN_vDXNDyJVIzxhkPiMTA1FrU6plUgyqVlTR5tOqj_xWb9Y7hMdWIlyy_wGDsDlMbIO7-HDCZZx9u7EGf7r4sDRVKg_Ic8pd-bPisOhTg-HTsmFi8WJ7Gofhx_-A')
    playlist = personal_client.user_playlist_create('duylam.nguyen','tiptone playlist')
    playlist_tracks = personal_client.user_playlist_add_tracks(user='duylam.nguyen', playlist_id=playlist['id'], tracks=recommendations_ids, position=None)
    return jsonify({'status':'ok'})

@app.route('/auth/sp/login')
def auth_sp_login():
    oauth = tsa.OAuthSignIn.get_provider("spotify")
    return redirect(oauth.authorize())

@app.route('/auth/sp/authenticate')
def auth_sp_authenticate():

    # d = datetime.datetime.now(pytz.utc)
    oauth = tsa.OAuthSignIn.get_provider("spotify")
    oauth.callback()
    user_email = oauth.results['spotify_user_id']
    user_refresh_token = oauth.results['refresh_token']
    user_refresh_expiration = oauth.results['expires_at']
    user_access_token = oauth.results['access_token']
    user_name = oauth.results['name']
    user_spid_but_actually_its_their_email = oauth.results['email']
    session['user'] = {}
    session['user']['access_token'] =  user_access_token
    session['user']['refresh_token'] =  user_refresh_token
    session['user']['email'] =  user_email
    return jsonify({'status':'ok','sender_playlist':user_email})


if __name__ == "__main__":
    app.run(debug = True)
