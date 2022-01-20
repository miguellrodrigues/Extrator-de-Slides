from lib.slide_extractor import SlideExtractor, ConfigParser

config = ConfigParser()
config = config.parse_args()

extractor = SlideExtractor(config)
extractor.extract()
