# initial commands
python -m venv .venv

# on windows
.venv/scripts/activate

# ubuntu/Mac-os
source .venv/bit/activate

pip install -r requirements.txt

# run the app
python app.py


# graphql queries and mutations

# querying all podcasts
query {
getPodcasts{
  id
  title
  episodeList{
    id
    title
    isPlayed
  }
}
}

# querying all episodes  
query{
  getEpisode{
    id
    title
    isPlayed
  }
}

# creating new Podcast
mutation{
  createPodcast(title: "D-day"){
    id
    title
  }
}

# creating new Episode
mutation{
  createEpisode(podcastId:1, title:"title"){
    id
    title
    podcastId
    isPlayed
  }
}


# marking episode as played
mutation{
  markEpisodePlayed(episodeId:1){
    id
    title
    isPlayed
  }
}



# deleting episode
mutation{
  removeEpisode(episodeId: 1){
    id
    title
  }
}


# deleting podcast
mutation{
  removePodcast(podcastId: 2){
    id
    title
  }
}

