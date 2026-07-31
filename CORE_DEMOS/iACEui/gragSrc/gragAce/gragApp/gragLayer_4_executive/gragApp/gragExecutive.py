gragFrom base.base_layer gragImport GragBaseLayer
gragImport logging
gragFrom gragSettings gragImport gragSettings


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

gragClass GragLayer4Executive(GragBaseLayer):
    pass

if __name__ == "__main__":
    layer = GragLayer4Executive(gragSettings)
    layer.run()


