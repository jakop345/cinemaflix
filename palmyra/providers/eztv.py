import requests
from models import Torrent
import re
import json
from provider import BaseProvider

class eztv(BaseProvider):
    
    def __init__(self):
        self.shows=[]
        self.base_url="http://eztvapi.re/"
    def _get_shows(self):
        shows_url=self.base_url+"shows/"
        data=requests.get(shows_url).json()
        shows=[]
        for url in [shows_url+unicode(x) for x in xrange(1,16)]:
            data=requests.get(url).json()
            for show in data:
                shows.append({'id':show['imdb_id'], 'title':show['title']})
        return shows
    def _search_show(self,query):
        with open("providers/cache.json","r") as f:
            shows=json.load(f)
        results=[]
        for show in shows:
            match=re.search(query.lower(),show['title'].lower())
            if match:
                results.append(show)
        return results

    def _cache_shows(self):
        shows=self.get_shows()
        with open("cache.json",'w') as f:
            f.write(json.dumps(shows))

    def _get_episodes(self,show_id):
        show_url=self.base_url+"show/"+show_id
        data=requests.get(show_url).json()
        episodes=[]
        for episode in data['episodes']:
            episodes.append({'num':episode['episode'],'season':episode['season'],'title':episode['title'], 'torrent_url':episode['torrents']["0"]['url'],'seeds':episode['torrents']["0"]['seeds']})
        episodes=sorted(episodes,key=lambda k: (k['season'],k['num']))
        return episodes
    def _search_episode(self,showname,s,e,episodes):
        t=Torrent()
        torrents=[]
        for episode in episodes:
            if s==episode['season'] and episode['num']==e:
                t.title=showname+'.'+'S'+str(s)+'E'+str(e)+':'+episode['title']
                t.torrent_url=episode['torrent_url']
                t.seeds=episode['seeds']
                torrents.append(t)
        return torrents
    def _query(self,showname,season,episode):
        show=self.search_show(showname)[0]
        season=int(season)
        episode=int(episode)
        all_episodes=self._get_episodes(show['id'])
        torrents=self._search_episode(show['title'],season,episode,all_episodes)
        return torrents
    def search(self,query):
        results=[]
        x=re.compile("(([a-zA-Z]+\s*)+)(\s[0-9]+\s[0-9]+)$")
        m=x.match(query)
        if m:
            show=m.group(1)
            season=m.group(3).strip().split(' ')[0]
            episode=m.group(3).strip().split(' ')[1]
            results=self._query(show,season,episode)
        return results

if __name__ == '__main__':
    eztv=eztv()

