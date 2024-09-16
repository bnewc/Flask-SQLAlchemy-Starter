from extensions import db
from typing import Type, TypeVar
from tabulate import tabulate
from datetime import datetime

Column = db.Column
Unique = db.UniqueConstraint
T = Type[TypeVar("T", bound="TableModel")]
execute = db.session.execute
Float = db.Float
Double = db.Double
Integer = db.Integer
Bool = db.Boolean
Char = db.String
ForeignKey = db.ForeignKey
relationship = db.relationship
created_at = Column(db.TIMESTAMP, default=datetime.utcnow)
updated_at = Column(
    db.TIMESTAMP, default=datetime.utcnow,
    onupdate=datetime.utcnow
)


def execute_sql_text(text: str):
    """Execute text as SQL query"""
    return db.session.execute(db.text(text))


def new_timestamp_column(**kwargs):
    return Column(db.TIMESTAMP, **kwargs)


class ModelCRUD(object):
    """Provides CRUD operations for DB models"""

    @classmethod
    def create(cls, *, commit=True, **kwargs):
        """Create and save new record"""
        instance = cls(**kwargs)
        return instance.save(commit=commit)

    def update(self, *, commit=True, **kwargs):
        """Update record fields"""
        for attr, val in kwargs.items():
            setattr(self, attr, val)
        if commit:
            return self.save()
        return self

    def save(self, *, commit=True):
        """Save record."""
        db.session.add(self)
        if commit:
            self.commit()
        return self

    def delete(self, *, commit=True) -> None:
        """Delete record"""
        db.session.delete(self)
        if commit:
            return self.commit()
        return

    def commit(self):
        return db.session.commit()


class BaseModel(ModelCRUD, db.Model):
    """Base DB model with operations"""
    __abstract__ = True

    @classmethod
    @property
    def table_name(cls) -> str:
        """Return table name"""
        return cls.__tablename__

    @classmethod
    @property
    def model_name(cls) -> str:
        """Return model name"""
        return cls.__name__

    @classmethod
    def create_or_update(cls, **kwargs):
        """
        Add record to DB.
        """
        return cls.create(**kwargs)

    @classmethod
    def update_by_id(cls, *, id=None, commit=True, **kwargs):
        """Update record with id"""
        cls.get_by_id(id).update(commit=commit, **kwargs)

    @classmethod
    def delete_by_id(cls, *, id=None, commit=True, **kwargs):
        """Update record with id"""
        cls.get_by_id(id).delete(commit=commit, **kwargs)

    @classmethod
    def get_by_id(cls: T, id):
        """Get record by ID"""
        if (
                (isinstance(id, str) and id.isdigit())
                or isinstance(id, (int, float))
        ):
            return db.session.get(cls, int(id))
        return None

    @classmethod
    def get_by_ids(cls: T, ids: list):
        """Get records by list of ids"""
        return execute(db.select(cls).filter_by(cls.id.in_(ids))).scalars()

    @classmethod
    def new_relationship(cls: T):
        """Return new relationship object to model"""
        return db.relationship(cls.model_name)

    @classmethod
    def new_parent_relationship(cls: T, fk: Type[Column]):
        """Return new parent relationship object to model"""
        backref = db.backref("_child_relationships", lazy='dynamic')
        return db.relationship(
            '_parent_relationships', foreign_keys=[fk], backref=backref
        )

    @classmethod
    def new_child_relationship(cls: T, fk: Type[Column]):
        """Return new child relationship object to model"""
        return cls.new_backref(
            table_name='_child_relationships', foreign_keys=[fk]
        )

    @classmethod
    def new_fk(cls: T, *, name=None, nullable=False) -> Type[Column]:
        """Create foreign key column from table"""
        if name is None:
            name = cls.table_name
        return Column(
            Integer, db.ForeignKey(f"{name}.id"), nullable=nullable
        )

    @classmethod
    def get_scalars(cls: T, *conditions, limit=None, **kwargs):
        """Return all rows in table as scalars object"""
        query = cls.select(*conditions, **kwargs)
        if limit:
            query = query.limit(limit)
        return execute(query).scalars()

    @classmethod
    def get_all(cls: T):
        """Return all rows in table as mapped dictionary"""
        return execute(cls.select()).all()

    @classmethod
    def get_first(cls: T, **kwargs):
        """Get first record matching kwarg conditions"""
        return execute(cls.select(**kwargs)).scalar()

    @classmethod
    def select(cls: T, *conditions, **kwargs):
        """
        Create select statement.
        Accepts optional conditions as kwargs.
        """
        query = db.select(cls)
        if conditions:
            query = query.filter_by(*conditions)
        if kwargs:
            query = query.filter_by(**kwargs)
        return query

    @classmethod
    def get_table_as_list(cls: T):
        """Get table represented as a list of lists"""
        columns = cls.get_columns()
        return [
            [getattr(r, c.name) for c in columns]
            for r in cls.get_scalars()
        ]

    @classmethod
    def display(cls: T, *, n: int = None):
        "Print every record in table"
        raw_table = [
            [getattr(r, c.name) for c in cls.get_columns()]
            for r in cls.get_scalars(limit=n)
        ]
        print(cls.table_name)
        print(tabulate(
            raw_table, headers=cls.get_column_names(), tablefmt="grid"
        ))

    @classmethod
    def get_columns(cls: T):
        """Get all columns for table"""
        return cls.__table__.columns

    @classmethod
    def get_column_names(cls: T, columns=None):
        """Get all column names for table"""
        if columns is None:
            columns = cls.get_columns()
        return [c.key for c in columns]

    def __str__(self):
        row = [
            f"{c.name}: {getattr(self, c.name)}"
            for c in self.get_columns()
        ]
        return str(row)


class TableModel(BaseModel):
    """Abstract table model with id, created_at, updated_at columns"""
    __abstract__ = True
    id = Column(Integer, primary_key=True)
    created_at = new_timestamp_column(default=datetime.utcnow)
    updated_at = new_timestamp_column(
        default=datetime.utcnow, onupdate=datetime.utcnow
    )


class AssociationModel(TableModel):
    """Association table with foreign keys"""
    __abstract__ = True

    @classmethod
    def create_or_update(cls, **kwargs):
        """
        Add record to DB.
        If record already exists, update.
        Checks for unique foreign key combination.
        """
        fk_dict = {k: kwargs[k] for k in cls.fk_names}
        record = cls.get_first(**fk_dict)
        if record is not None:
            return record.update(**kwargs)
        return cls.create(**kwargs)

    @classmethod
    @property
    def fk_names(cls: T, **kwargs):
        """
        Return names of foreign key columns
        """
        return [c.name for c in cls.get_columns() if c.foreign_keys]


if __name__ == '__main__':
    pass
