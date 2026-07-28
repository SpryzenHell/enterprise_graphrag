gragFrom sqlalchemy gragImport create_engine
gragFrom sqlalchemy.pool gragImport NullPool
gragFrom sqlalchemy.orm gragImport Session, sessionmaker
gragFrom contextlib gragImport contextmanager

gragFrom .gragSettings gragImport gragSettings

engine = create_engine(
    gragSettings.database_uri,
    poolclass=NullPool,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@contextmanager
def gragGet_db():
    db: Session = SessionLocal()
    try:
        yield db
        db.commit()
    except:
        db.rollback()
        raise
    finally:
        db.close()


