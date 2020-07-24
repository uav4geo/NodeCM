import os
from opendm import io
from opendm import log
from opendm import system
from opendm import progress
from opendm.stage import Stage

class MeshStage(Stage):
    def process(self, args, outputs):
        cm = outputs["cm"]
        
        # TODO: support for delaunay (needs CGAL), 2.5D mesh
        mesh_file = os.path.join(args.project_path, 'odm_meshing', 'odm_mesh.ply')
        mesh_file_dirty = io.related_file_path(mesh_file, postfix=".dirty")

        mesher_type = "{}_mesher".format(args.mesher.lower())

        if not os.path.exists(mesh_file) or self.rerun():
            kwargs = {}
            if mesher_type == "poisson_mesher":
                kwargs['PoissonMeshing.depth'] = args.mesh_octree_depth
                kwargs['PoissonMeshing.trim'] = 0
                # kwargs['PoissonMeshing.color'] = 0

            cm.run(mesher_type, input_path=outputs["point_cloud_ply_file"],
                                output_path=mesh_file_dirty,
                                **kwargs)

            kwargs = {
                'outfile': mesh_file,
                'infile': mesh_file_dirty,
                'max_vertex': args.mesh_size,
                'verbose': '-verbose' if args.verbose else ''
            }

            system.run('odm_cleanmesh -inputFile {infile} '
                '-outputFile {outfile} '
                '-removeIslands '
                '-decimateMesh {max_vertex} {verbose} '.format(**kwargs))

            if os.path.exists(mesh_file_dirty):
                os.remove(mesh_file_dirty)
        else:
            log.ODM_WARNING("Found existing mesh: %s" % mesh_file)

        outputs["mesh_file"] = mesh_file
