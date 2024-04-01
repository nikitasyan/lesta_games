import models
from sqlalchemy.orm import Session


def update_table(db: Session, calculated_text: dict[str, int]) -> None:
    update_common_statistics(db=db,
                             counted_words=calculated_text,
                             model=models.AllWords)
    update_statistics_current_file(db=db,
                                   counted_words=calculated_text,
                                   model=models.CurrentFile)


def update_statistics_current_file(db: Session, counted_words: dict[str, int], model) -> None:
    clear_table(db=db,
                table=models.CurrentFile)
    for word, count in counted_words.items():
        model_word = db.query(models.AllWords).filter(models.AllWords.word == word).first()
        new_word = models.CurrentFile(word_id=model_word.id,
                                      word_count=count)
        db.add(new_word)
    db.commit()


def update_common_statistics(db: Session, counted_words: dict[str, int], model) -> None:
    for word in counted_words.keys():
        word_already_exist = db.query(models.AllWords).filter(models.AllWords.word == word).first()
        if not word_already_exist:
            new_word = models.AllWords(word=word,
                                       count_files_with_word=0)
            db.add(new_word)
        refreshing_word = db.query(models.AllWords).filter(models.AllWords.word == word).first()
        refreshing_word.count_files_with_word += 1
    db.commit()


def clear_table(db: Session, table) -> None:
    db.query(table).delete()
    db.commit()


def get_statistics(db: Session) -> list[models.AllWords]:
    all_statistics = (db.query(models.AllWords)
                      .join(models.CurrentFile)
                      .all())
    return all_statistics
