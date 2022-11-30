import modules.database as db
import modules.musicPlayer as mp

from os import path

if __name__ == "__main__":
    db.initDatabaseIfNotExists()

    mp.runApplication()