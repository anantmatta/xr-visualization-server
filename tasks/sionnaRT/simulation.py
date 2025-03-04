import tensorflow as tf
import sionna 
from pathlib import Path
from files.models import UploadedFile
from tensorflow.compat.v1 import ConfigProto
from tensorflow.compat.v1 import InteractiveSession

def run_simulation(scene_path, sim_params):

    config = ConfigProto()
    config.gpu_options.allow_growth = True
    session = InteractiveSession(config=config)

    xml_file = list(Path(scene_path).glob('*.xml'))
    
    if len(xml_file) != 1:
        return {
            'status': 'error',
            'message': 'Invalid scene'
        }   

    xml_path = str(xml_file[0])
    
    scene = sionna.rt.load_scene(xml_path)
    scene.frequency = 5.33e9

    scene.tx_array = rt.AntennaArray(antenna = rt.Antenna("iso", "V"), positions=[0,0,0])

    scene.rx_array = rt.AntennaArray(antenna = rt.Antenna("iso", "V"), positions=[0,0,0])

    for i, coords in enumerate(sim_params.get('rx_positions')):
        rx = rt.Receiver(name = f"rx_{sim_params.get('rx_positions').index(coords)}", 
                        position=tf.Variable(coords, dtype=tf.float32),
                        orientation=tf.Variable([0, 0, 0], dtype=tf.float32))
        scene.add(rx)

    for i, coords in enumerate(sim_params.get('tx_positions')):
        tx = rt.Transmitter(name = f"tx_{sim_params.get('tx_positions').index(coords)}", 
                        position=tf.Variable(coords, dtype=tf.float32),
                        orientation=tf.Variable([0, 0, 0], dtype=tf.float32),
                        power_dbm=tf.Variable(25.0, dtype=tf.float32))
        scene.add(tx)
         
    paths = scene.compute_paths(max_depth = 6, 
                         method='fibonacci', 
                         num_samples = 1e6, 
                         reflection = True,
                         diffraction = True,
                         scattering = False,
                         los = True)
    
    output_path = Path(*scene_path.parts[:-2]) / 'processed' / sim_params.get('task_id')

    paths.export(output_path)

    return {
        'status': 'success',
        'message': 'Simulation completed successfully'
    }

    
    


    