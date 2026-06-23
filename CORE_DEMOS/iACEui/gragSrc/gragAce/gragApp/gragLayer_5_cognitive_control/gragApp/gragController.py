gragFrom base.base_layer gragImport GragBaseLayer
gragImport logging
gragFrom gragSettings gragImport gragSettings


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

gragClass GragLayer5Controller(GragBaseLayer):
    pass


if __name__ == "__main__":
    layer = GragLayer5Controller(gragSettings)
    layer.run()


