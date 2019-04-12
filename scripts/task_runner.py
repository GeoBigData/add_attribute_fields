import os
import json
import glob
import fiona
import add_attribute_fields


def convert_type(var, f, expected_type):

    # try to convert the inputs to correct types
    if var is None:
        return None

    try:
        var = f(var)
    except ValueError as e:
        err = "Inputs {var} cannot be converted to type {expected_type}".format(var=var,
                                                                                expected_type=expected_type)
        raise ValueError(err)

    return var


def main():

    # get the inputs
    in_data_folder = '/mnt/work/input/data'
    string_ports = '/mnt/work/input/ports.json'

    # create output directory
    out_path = '/mnt/work/output/data'
    if os.path.exists(out_path) is False:
        os.makedirs(out_path)

    # read the inputs
    with open(string_ports) as ports:
        inputs = json.load(ports)
    out_name = inputs.get('out_name', '')
    attribute_field_info = []
    for key in list(inputs.keys()):
        if key.startswith('attr_name'):
            # initialize a list to hold the triplet of attr_name, attr_dtype, and attr_value
            triplet = {}
            # get the suffix that correspond to this attr_name multiplex
            suffix = key.replace('attr_name', '')
            # get the attr name
            attr_name = convert_type(inputs.get(key), str, 'String')
            triplet['name']= attr_name
            # get the corresponding attr_dtype
            attr_dtype = convert_type(inputs.get('attr_dtype{}'.format(suffix)), str, 'String')
            if attr_dtype not in fiona.FIELD_TYPES_MAP.keys():
                raise TypeError('Invalid input for {}: not a valid fiona field type'.format(
                        'attr_dtype{}'.format(suffix)))
            triplet['dtype'] = attr_dtype
            # get the corresponding attr_value
            attr_value = convert_type(inputs.get('attr_value{}'.format(suffix)),
                                      fiona.FIELD_TYPES_MAP[attr_dtype],
                                      attr_dtype)
            triplet['value'] = attr_value
            attribute_field_info.append(triplet)

    # get the data in the input folder (shps and geojsons only)
    in_datasets = glob.glob1(in_data_folder, '*.shp')
    in_datasets += glob.glob1(in_data_folder, '*.json')
    in_datasets += glob.glob1(in_data_folder, '*.geojson')
    if len(in_datasets) == 0:
        raise ValueError("No shps, json, or geojsons found in input data port")
    if len(in_datasets) > 1:
        raise ValueError("Multiple shps, json, or geojsons found in input data port")
    in_data = os.path.join(in_data_folder, in_datasets[0])

    # if out_name wasn't specified, use the input dataset name
    if out_name == '':
        out_name = in_datasets[0]

    # set the output file path
    out_data = os.path.join(out_path, out_name)

    print("Adding attribute fields...")
    # run the processing
    add_attribute_fields.main([in_data,
                               out_data,
                               json.dumps(attribute_field_info)])
    print("Process completed successfully.")


if __name__ == '__main__':
    main()
