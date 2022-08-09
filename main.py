import modules.filebase as filebase
import modules.musicPlayer as musicPlayer

if __name__ == "__main__":
    filebase.initFilebaseIfNotExists()

    musicPlayer.runApplication()