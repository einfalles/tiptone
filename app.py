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

grant_type = 'client_credentials'
SPOTIFY_INFO = {
    'id':'4f8c3338b0b443a8895358db33763c6f',
    'secret':'76cf6ff10bb041dbb0b11a3e7dd89fe1'
}
@app.route('/')
def index():
    session.permanent = True
    pprint.pprint(session['user']['access_token'])
    return render_template('basic.html')

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
    recommendations = spotify_client.recommendations(seed_tracks=[data_one['sp_uri'],data_two['sp_uri']],limit=12)
    recommendations = recommendations['tracks']
    recommendations_ids = []
    for i in recommendations:
        recommendations_ids.append(i['id'])
    personal_client = spotipy.Spotify(auth='BQAwz2uGjkEVZbmeov_LG65oXYX5e916MgRuVBpbAbHA1vmhLamK9Qw2rz4LeJQum82AQEwTxChXLKUI5Hd8cDiKklEaiHIJuOPGCYYnn0ltj_Mlv9OZhNwv-Y1L4aBKxkbcyMReSnP_3hKO-B-xVOCRrg58ayx3yZrTYpZ7G5en45zgOt0xb85VfW8BlZBTpUfCSfKLbWZhywIyaB6snO68X8zwCB1Q64I4KuLEiuuFmy255qlmAAP6dvIa7wjpv8tsCJnfId4')
    playlist = personal_client.user_playlist_create('duylam.nguyen','tiptone: {0} and {1}'.format(track_two_artist,track_one_artist))
    playlist_tracks = personal_client.user_playlist_add_tracks(user='duylam.nguyen', playlist_id=playlist['id'], tracks=recommendations_ids, position=None)
    return jsonify({'status':'ok','id':playlist['id']})

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

@app.route('/v3/recommendation/<src>/<dest>')
def recommendation_3(src,dest):
    api_echonest = 'http://frog.playlistmachinery.com:4682/frog/path?src={}&dest={}'.format(src, dest)
    raw_path = requests.get(api_echonest).json()['raw_path']
    middle_list = len(raw_path)//2
    recommendation_seed = raw_path[middle_list]

    # RETRIEVE SPOTIFY TOKENS
    sp_token = oauth.SpotifyClientCredentials(client_id='4f8c3338b0b443a8895358db33763c6f',client_secret='76cf6ff10bb041dbb0b11a3e7dd89fe1')

    # CREATE SPOTIFY CLIENT
    spotify_client = spotipy.Spotify(auth=sp_token.get_access_token())

    # GET RECOMMENDATIONS
    recommendations = spotify_client.recommendations(seed_artists=[recommendation_seed],limit=12)['tracks']
    return jsonify({'status':'ok','recommendations':recommendations})

@app.route('/v3/playlistcreation', methods=['POST'])
def generate_playlist():
    # GET SONG IDS FROM ARRAY

    # CREATE PLAYLIST OBJECT

    # INSERT SONG IDS INTO PLAYLIST OBJECT

    # RETURN PLAYLIST ID
    return jsonify({'status':'ok','recommendations':recommendations})

if __name__ == "__main__":
    app.run(debug = True)
