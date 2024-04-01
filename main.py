import re
from math import log
from typing import Annotated

from sqlalchemy.orm import Session

from fastapi import FastAPI, Depends, File, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from database import SessionLocal, Base, engine
import crud
import models


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

app = FastAPI()
app.mount("/statics", StaticFiles(directory="statics"), name="static")
templates = Jinja2Templates(directory="templates")
files_count = 0


def clear_special_symbols(text: str) -> str:
    return re.sub(r'[^\w\s]', '', text)


def calculate_words_count_in_text(text: list) -> dict[str, int]:
    calculated_text = dict()
    for word in text:
        if word not in calculated_text:
            calculated_text[word] = 0
        calculated_text[word] += 1
    return calculated_text


def formatting_statistics(statistics: list[models.AllWords],
                          word_count_in_file: int,
                          file_count: int) \
        -> list[dict]:

    formatted_statistics = list()
    for index, model in enumerate(statistics):
        word = model.word
        tf = round(model.current_file[0].word_count / word_count_in_file, 4)
        idf = round(log(file_count / model.count_files_with_word), 4)
        formatted_statistics.append(dict(word=word, tf=tf, idf=idf))
    return formatted_statistics


def sorting_statistics(statistics: list[dict], limit: int) -> list[dict]:
    sorted_statistics = sorted(statistics, key=lambda x: x["idf"], reverse=True)
    for index, word_statistics in enumerate(sorted_statistics[:limit]):
        word_statistics["index"] = index + 1
    return sorted_statistics[:limit]


@app.post("/files/", response_model=list[dict])
def create_file(request: Request, file: Annotated[bytes, File()], limit_words: int = 50, db: Session = Depends(get_db)):
    global files_count
    files_count += 1
    decoded_text = file.decode()
    text = clear_special_symbols(decoded_text).lower().strip().split()
    word_count_in_file = len(text)

    calculated_text = calculate_words_count_in_text(text=text)
    crud.update_table(db=db,
                      calculated_text=calculated_text)
    statistics = crud.get_statistics(db=db)
    present_stat = formatting_statistics(statistics=statistics,
                                         word_count_in_file=word_count_in_file,
                                         file_count=files_count)
    sorted_stat = sorting_statistics(statistics=present_stat,
                                     limit=limit_words)
    return templates.TemplateResponse(name="current_statistics.html",
                                      context={"request": request,
                                               "body_content": sorted_stat})


@app.get("/")
async def main(request: Request, db: Session = Depends(get_db)):
    if request.query_params.get("reset_statistics"):
        global files_count
        files_count = 0
        crud.clear_table(db=db,
                         table=models.CurrentFile)
        crud.clear_table(db=db,
                         table=models.AllWords)
    return templates.TemplateResponse(name="index.html",
                                      context={"request": request})
