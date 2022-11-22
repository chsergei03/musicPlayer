import modules.database as database
import modules.musicPlayer as musicPlayer

if __name__ == "__main__":
    database.initDatabaseIfNotExists()

    musicPlayer.runApplication()