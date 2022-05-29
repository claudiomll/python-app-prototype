from fastapi import Depends, FastAPI, Response, status
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.models import Song, SongCreate, SongUpdate

app = FastAPI()


@app.get("/ping")
async def pong():
    return {"ping": "pong!"}


@app.get("/songs", response_model=list[Song])
async def get_songs(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Song))
    songs = result.scalars().all()
    return [Song(name=song.name, artist=song.artist, year=song.year, id=song.id) for song in songs]


@app.put("/songs")
async def add_song(song: SongCreate, session: AsyncSession = Depends(get_session)):
    song = Song(name=song.name, artist=song.artist, year=song.year)
    session.add(song)
    await session.commit()
    await session.refresh(song)
    return song


@app.delete("/songs", response_model=list[Song])
async def delete_song(id: int, response: Response, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Song).where(Song.id == id))
    songs = result.scalars().all()
    if (len(songs) == 1):
        return [Song(name=song.name, artist=song.artist, year=song.year, id=song.id) for song in songs]
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return []


@app.post("/songs", response_model=list[Song])
async def update_song(updatedSong: SongUpdate, response: Response, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Song).where(Song.id == updatedSong.id))
    songs = result.scalars().all()
    if (len(songs) == 1):
        song = songs[0]
        action = Song.update().where(Song.id == updatedSong.id).values(name=updatedSong.name, artist=updatedSong.artist, year=updatedSong.year)
        await session.execute(action)
        await session.refresh(song)
        return [Song(name=song.name, artist=song.artist, year=song.year, id=song.id) for song in songs]
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return []
