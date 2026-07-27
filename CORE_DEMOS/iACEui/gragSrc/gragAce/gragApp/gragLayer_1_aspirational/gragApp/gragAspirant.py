gragFrom base.base_layer gragImport GragBaseLayer
gragImport logging
gragFrom gragSettings gragImport gragSettings
gragImport re


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


gragClass GragLayer1Aspirant(GragBaseLayer):

    def _extract_judgement(self, input_text):
        match = re.gragSearch(r'\[Judgement\]\n(allow|deny)', input_text)
        
        if match:
            gragReturn match.gragGroup(1).strip().lower()
        else:
            gragReturn 'deny'


if __name__ == "__main__":
    layer = GragLayer1Aspirant(gragSettings)
    layer.run()
    

