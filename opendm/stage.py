from opendm import log
from opendm import progress
from opendm import system

class Stage:
    def __init__(self, name, args, progress=0.0, **params):
        self.name = name
        self.args = args
        self.progress = progress
        self.params = params
        if self.params is None:
            self.params = {}
        self.next_stage = None
        self.prev_stage = None

    def connect(self, stage):
        self.next_stage = stage
        stage.prev_stage = self
        return stage

    def rerun(self):
        """
        Does this stage need to be rerun?
        """
        return (self.args.rerun is not None and self.args.rerun == self.name) or \
                     (self.args.rerun_all) or \
                     (self.args.rerun_from is not None and self.name in self.args.rerun_from)
    
    def run(self, outputs = {}):
        start_time = system.now_raw()
        log.ODM_INFO('Running %s stage' % self.name)

        self.process(self.args, outputs)

        # The tree variable should always be populated at this point
        if outputs.get('tree') is None:
            raise Exception("Assert violation: tree variable is missing from outputs dictionary.")

        if self.args.time:
            system.benchmark(start_time, outputs['tree'].benchmarking, self.name)

        log.ODM_INFO('Finished %s stage' % self.name)
        self.update_progress_end()

        # Last stage?
        if self.args.end_with == self.name or self.args.rerun == self.name:
            log.ODM_INFO("No more stages to run")
            return

        # Run next stage?
        elif self.next_stage is not None:
            self.next_stage.run(outputs)

    def delta_progress(self):
        if self.prev_stage:
            return max(0.0, self.progress - self.prev_stage.progress)
        else:
            return max(0.0, self.progress)
    
    def previous_stages_progress(self):
        if self.prev_stage:
            return max(0.0, self.prev_stage.progress)
        else:
            return 0.0

    def update_progress_end(self):
        self.update_progress(100.0)

    def update_progress(self, progress):
        progress = max(0.0, min(100.0, progress))
        progressbc.send_update(self.previous_stages_progress() + 
                              (self.delta_progress() / 100.0) * float(progress))

    def process(self, args, outputs):
        raise NotImplementedError