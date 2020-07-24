# NodeCM

An end-to-end GPU-enabled photogrammetry pipeline to generate point clouds, orthophotos and elevation models from aerial images using [COLMAP](https://github.com/colmap/colmap/).

It's compatible with the [NodeODM API](https://github.com/OpenDroneMap/NodeODM) so it works out of the box with many of the tools of the OpenDroneMap ecosystem such as [WebODM](https://github.com/OpenDroneMap/WebODM), [ClusterODM](https://github.com/OpenDroneMap/ClusterODM) and [CloudODM](https://github.com/OpenDroneMap/CloudODM).

While a GPU can speed up certain steps of the pipeline, it is not required for use. CPU algorithms are implemented in case a GPU is not available.

## Getting Started

We recommend that you setup NodeCM using [Docker](https://www.docker.com/).

* From a shell, simply run:

```
docker run -p 3000:3000 uav4geo/nodecm
```

* Open a Web Browser to `http://localhost:3000` (or the IP of your docker machine)
* Load [some images](https://github.com/OpenDroneMap/ODM/tree/master/tests/test_data/images)
* Press "Start Task"
* Go for a walk :)

## Using an External Hard Drive

If you want to store results on a separate drive, map the `/app/NodeODM/data` folder to the location of your drive:

```bash
docker run -p 3000:3000 -v /mnt/external_hd:/app/NodeODM/data uav4geo/nodecm
```

This can be also used to access the computation results directly from the file system.

### Test Images

You can find some test drone images [here](https://github.com/OpenDroneMap/odm_data).

## Contributing

We welcome contributions! Send pull requests and let's build something cool together.

## Roadmap

NodeCM is in beta. It hasn't been battle-tested and issues are expected. We are aware of the following list of things that still need to be improved (help us improve them)!

 - [ ] DSM/DTM interpolation (currently DEMs don't look so good)
 - [ ] Better meshing algorithms (currently PoissonRecon is less than ideal)
 - [ ] GSD estimates. Currently they are not taken in consideration, so memory is potentially wasted and output resolutions cannot be automatically calculated
 - [ ] GCPs support. COLMAP has basic support for geo-registration which will align the reconstruction based on an affine transformation of the camera centers, but no support for GCPs.
 - [ ] Bug fixing (help us and report them on the issue tracker)

## License

This codebase: Affero GPL
COLMAP: BSD.
OpenDroneMap/NodeODM modules: GPL

## GPU License Restrictions

If you use the GPU features of NodeCM, you **cannot** use NodeCM for purposes other than educational, research and non-profit purposes without obtaining permission from the `University of North Carolina at Chapel Hill`. COLMAP uses the SIFT GPU library, which is released under the following [license](https://github.com/colmap/colmap/blob/dev/lib/SiftGPU/LICENSE):

```
////////////////////////////////////////////////////////////////////////////
//
//  Copyright (c) 2007 University of North Carolina at Chapel Hill
//  All Rights Reserved
//
//  Permission to use, copy, modify and distribute this software and its
//  documentation for educational, research and non-profit purposes, without
//  fee, and without a written agreement is hereby granted, provided that the
//  above copyright notice and the following paragraph appear in all copies.
//
//  The University of North Carolina at Chapel Hill make no representations
//  about the suitability of this software for any purpose. It is provided
//  'as is' without express or implied warranty.
//
//  Please send BUG REPORTS to ccwu@cs.unc.edu
//
////////////////////////////////////////////////////////////////////////////
```

We understand this is unfortunate. Contribute a PR to replace SIFT GPU?
