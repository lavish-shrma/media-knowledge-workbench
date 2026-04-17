from app.db.base import Base
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


def test_base_subclass_has_metadata() -> None:
    class ExampleModel(Base):
        __tablename__ = "example_model"
        id: Mapped[int] = mapped_column(primary_key=True)

    assert ExampleModel.metadata is Base.metadata
