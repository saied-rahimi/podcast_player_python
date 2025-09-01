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
    episods_list: List["Episod"] = Relationship(back_populates="podcast")

class Episod(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    podcast_id: int = Field(foreign_key="podcast.id")
    podcast: Optional[Podcast] = Relationship(back_populates="episods_list")
    isPlayed: Optional[bool] = Field(default=False)

SQLModel.metadata.create_all(engine)

@strawberry.type
class EpisodType:
    id: int
    title: str
    podcast_id: int
    isPlayed: bool

@strawberry.type
class PodcastType:
    id: int
    title: str
    episods_list: List[EpisodType]

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
                    episods_list=[
                        EpisodType(id=e.id, title=e.title, podcast_id=e.podcast_id,isPlayed=e.isPlayed)
                        for e in p.episods_list
                    ]
                )
                for p in podcasts
            ]


    @strawberry.field
    def get_episods(self) -> List[EpisodType]:
        with Session(engine) as session:
            episods = session.exec(select(Episod)).all()
            return [
                EpisodType(id=e.id, title=e.title, podcast_id=e.podcast_id, isPlayed=e.isPlayed)
                for e in episods
            ]
    @strawberry.field
    def get_played_episods(self) -> List[EpisodType]:
        with Session(engine) as session:
            episods = session.exec(select(Episod)).all()
            return [
                EpisodType(id=e.id, title=e.title, podcast_id=e.podcast_id, isPlayed=e.isPlayed)
                for e in episods if e.isPlayed
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
            return PodcastType(id=new_podcast.id, title=new_podcast.title, episods_list=[])

    @strawberry.mutation
    def create_episod(self, title: str, podcast_id: int) -> EpisodType:
        with Session(engine) as session:
            new_episod = Episod(title=title, podcast_id=podcast_id)
            session.add(new_episod)
            session.commit()
            session.refresh(new_episod)
            return EpisodType(id=new_episod.id, title=new_episod.title, podcast_id=new_episod.podcast_id, isPlayed=False)
        


    @strawberry.mutation
    def mark_episod_played(self, episod_id: int, played: bool = True) -> EpisodType:
        with Session(engine) as session:
            episod = session.get(Episod, episod_id)
            if not episod:
                raise ValueError("Episode not found")
            episod.isPlayed = played
            session.add(episod)
            session.commit()
            session.refresh(episod)
            return EpisodType(
                id=episod.id,
                title=episod.title,
                podcast_id=episod.podcast_id,
                isPlayed=episod.isPlayed
            )
schema = strawberry.Schema(query=Query, mutation=Mutation)

app = Flask(__name__)
app.add_url_rule("/", view_func=GraphQLView.as_view("graphql_view", schema=schema, graphiql=True))

if __name__ == "__main__":
    app.run(debug=True)
