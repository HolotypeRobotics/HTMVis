import json
from htm.bindings.sdr import SDR
from htm.bindings.algorithms import SpatialPooler, TemporalMemory
from htm.bindings.encoders import ScalarEncoder
from htm.bindings.engine_internal import Network, Region
import numpy as np
from Vis import Vis


def main():
    encoders = []
    spRegion = None
    tmRegion = None

    with open('params', 'r') as file:
        content = file.read()
        config = content.replace('\n', '')

    network = Network() # Note: can't call Network().configure()
    network.configure(config)
    regions = network.getRegions()
    # Get a handle on the regions
    for name, region in regions:
        region_type = region.getType()
        if region_type == 'ScalarEncoderRegion':
            encoders.append(region)
        elif region_type == 'SPRegion':
            spRegion = region
        elif region_type == 'TMRegion':
            tmRegion = region
        print(region.getParameters())
    vis  = Vis()
    vis.run()
    value = 0
    while True:
        for enc in encoders:
            enc.setParameterReal64("sensedValue", value)
        network.run(1)
        vis.setRegionData(encoders,spRegion, tmRegion)
        if value >= 100:
            value = 0
        value+=1
        input()
if __name__ == '__main__':
    main()