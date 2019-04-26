import spotipy
import spotipy.oauth2 as oauth
import datetime
import random
import auth
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

@app.route('/auth/sp/login')
def auth_sp_login():
    oauth = auth.OAuthSignIn.get_provider("spotify")
    return redirect(oauth.authorize())

@app.route('/auth/sp/authenticate')
def auth_sp_authenticate():
    auth_code = request.args.get('code')
    oauth = auth.OAuthSignIn.get_provider("spotify")
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
    path_randomization = [1,0,-1]
    path_deviation = random.choice(path_randomization)
    api_echonest = 'http://frog.playlistmachinery.com:4682/frog/path?src={}&dest={}'.format(src, dest)
    raw_path = requests.get(api_echonest).json()['raw_path']
    middle_list = len(raw_path)//2
    recommendation_seed = raw_path[middle_list-path_deviation]

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
    songs = request.get_json(silent=True)

    datestring = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # CREATE PLAYLIST OBJECT
    personal_client = spotipy.Spotify(auth=session['user']['access_token'])
    playlist = personal_client.user_playlist_create(user='duylam.nguyen',name='___tiptone___ {}'.format(datestring))

    # INSERT SONG IDS INTO PLAYLIST OBJECT
    playlist_tracks = personal_client.user_playlist_add_tracks(user='duylam.nguyen', playlist_id=playlist['id'], tracks=songs, position=None)
    print(playlist)
    # RETURN PLAYLIST ID
    return jsonify({'status':'ok','recommendations':playlist['external_urls']['spotify']})

if __name__ == "__main__":
    app.run(debug = True)
