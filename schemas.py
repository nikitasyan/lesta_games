from pydantic import BaseModel


class CurrentFile(BaseModel):
    word_count: int
    word_id: int


class AllWords(BaseModel):
    id: int
    word: str
    count_files_with_word: int
    current_file: list[CurrentFile] = []
