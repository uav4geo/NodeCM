#!/usr/bin/python
import os
from opendm import log
from opendm import config
from opendm import system
from opendm import io
from opendm.progress import progressbc
from stages.dataset import DatasetStage

if __name__ == '__main__':

    args = config.config()

    log.ODM_INFO('Initializing NodeCOLMAP app - %s' % system.now())
    log.ODM_INFO(args)


    progressbc.set_project_name(os.path.basename(args.project_path))


    # Initializes the application and defines the pipeline stages
    dataset = DatasetStage('dataset', args, progress=5.0)

    # Normal pipeline
    pipeline = dataset

        # dataset.connect(split) \
    try:
        pipeline.run()
    except Exception as e:
        log.ODM_ERROR(e)
        exit(1)

