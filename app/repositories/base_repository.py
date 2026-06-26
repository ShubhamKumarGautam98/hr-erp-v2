from app.models.models import db


class BaseRepository:
    """Shared save / delete helpers for all repositories."""

    def save(self, instance):
        db.session.add(instance)
        db.session.commit()
        return instance

    def save_all(self, instances):
        for obj in instances:
            db.session.add(obj)
        db.session.commit()

    def delete(self, instance):
        db.session.delete(instance)
        db.session.commit()

    def flush(self):
        db.session.flush()

    def commit(self):
        db.session.commit()
