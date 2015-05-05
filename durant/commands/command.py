class Command(object):
    config = None

    def __init__(self, config):
        self.config = config

    def execute(self, **kwargs):
        self.before_run()
        self.run(**kwargs)
        self.after_run()

    def before_run(self):
        pass

    def run(self, **kwargs):
        pass

    def after_run(self):
        pass   
