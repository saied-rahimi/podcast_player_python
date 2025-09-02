from flask import Flask
from sqlmodel import SQLModel, Field, Session, create_engine, select, Relationship
from typing import Optional, List
import strawberry
from strawberry.flask.views import GraphQLView


DATABASE_URL = "sqlite:///./podcast.db"
engine = create_engine(DATABASE_URL, echo=True)

class Podcast(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    episode_list: List["Episode"] = Relationship(back_populates="podcast")

class Episode(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    podcast_id: int = Field(foreign_key="podcast.id")
    podcast: Optional[Podcast] = Relationship(back_populates="episode_list")
    isPlayed: Optional[bool] = Field(default=False)

SQLModel.metadata.create_all(engine)

@strawberry.type
class EpisodeType:
    id: int
    title: str
    podcast_id: int
    isPlayed: bool

@strawberry.type
class PodcastType:
    id: int
    title: str
    episode_list: List[EpisodeType]

@strawberry.type
class Query:
    @strawberry.field
    def get_podcasts(self) -> List[PodcastType]:
        with Session(engine) as session:
            podcasts = session.exec(select(Podcast)).all()
            return [
                PodcastType(
                    id=p.id,
                    title=p.title,
                    episode_list=[
                        EpisodeType(id=e.id, title=e.title, podcast_id=e.podcast_id,isPlayed=e.isPlayed)
                        for e in p.episode_list
                    ]
                )
                for p in podcasts
            ]


    @strawberry.field
    def get_episode(self) -> List[EpisodeType]:
        with Session(engine) as session:
            episode = session.exec(select(Episode)).all()
            return [
                EpisodeType(id=e.id, title=e.title, podcast_id=e.podcast_id, isPlayed=e.isPlayed)
                for e in episode
            ]
    @strawberry.field
    def get_played_episode(self) -> List[EpisodeType]:
        with Session(engine) as session:
            episode = session.exec(select(Episode)).all()
            return [
                EpisodeType(id=e.id, title=e.title, podcast_id=e.podcast_id, isPlayed=e.isPlayed)
                for e in episode if e.isPlayed
            ]

@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_podcast(self, title: str) -> PodcastType:
        with Session(engine) as session:
            new_podcast = Podcast(title=title)
            session.add(new_podcast)
            session.commit()
            session.refresh(new_podcast)
            return PodcastType(id=new_podcast.id, title=new_podcast.title, episode_list=[])

    @strawberry.mutation
    def create_episode(self, title: str, podcast_id: int) -> EpisodeType:
        with Session(engine) as session:
            new_episode = Episode(title=title, podcast_id=podcast_id)
            session.add(new_episode)
            session.commit()
            session.refresh(new_episode)
            return EpisodeType(id=new_episode.id, title=new_episode.title, podcast_id=new_episode.podcast_id, isPlayed=False)
        


    @strawberry.mutation
    def mark_episode_played(self, episode_id: int) -> EpisodeType:
        with Session(engine) as session:
            episode = session.get(Episode, episode_id)
            if not episode:
                raise ValueError("Episode not found")
            episode.isPlayed = True
            session.add(episode)
            session.commit()
            session.refresh(episode)
            return EpisodeType(
                id=episode.id,
                title=episode.title,
                podcast_id=episode.podcast_id,
                isPlayed=episode.isPlayed
            )
    

    @strawberry.mutation
    def remove_podcast(self, podcast_id: int) -> PodcastType:
        with Session(engine) as session:
            podcast = session.get(Podcast, podcast_id)
            if not podcast:
                raise Exception("Podcast not found")
            deleted_podcast = PodcastType(id=podcast.id, title=podcast.title, episode_list=podcast.episode_list)
            session.delete(podcast)
            session.commit()
            return deleted_podcast

    @strawberry.mutation
    def remove_episode(self, episode_id: int) -> EpisodeType:
        with Session(engine) as session:
            episode = session.get(Episode, episode_id)
            if not episode:
                raise Exception("Episode not found")
            deleted_episode = EpisodeType(id=episode.id, title=episode.title, isPlayed=episode.isPlayed, podcast_id=episode.podcast_id)
            session.delete(episode)
            session.commit()
            return deleted_episode
schema = strawberry.Schema(query=Query, mutation=Mutation)

app = Flask(__name__)
app.add_url_rule("/", view_func=GraphQLView.as_view("graphql_view", schema=schema, graphiql=True))

if __name__ == "__main__":
    app.run(debug=True)
