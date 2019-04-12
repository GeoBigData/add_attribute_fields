import fiona
import click
import os
import json


def validate_attribute_field_info(attribute_field_info):

    # make sure it's a list
    if not isinstance(attribute_field_info, list):
        raise TypeError("attribute_field_info must be a list")

    # make sure each element is a dictionary with the correct attributes
    expected_keys = ['name', 'dtype', 'value']
    for d in attribute_field_info:
        if isinstance(d, dict) is False:
            raise TypeError("Elements of attribute_field_info must be a dictionary.")
        if sorted(expected_keys) != sorted(list(d.keys())):
            raise KeyError("Keys in attributed_field_info do not match the expected set: {}".format(expected_keys))
        try:
            fiona.prop_type(d['dtype'])
            fiona.prop_width(d['dtype'])
        except Exception as e:
            raise TypeError("Specified dtype {dtype} is invalid: {e}".format(dtype=d['dtype'],
                                                                             e=str(e)))
@click.command()
@click.argument('in_data')
@click.argument('out_data')
@click.argument('attribute_field_info')
def main(in_data, out_data, attribute_field_info):

    # check the input exists
    if os.path.exists(in_data) is False:
        raise FileNotFoundError(in_data)

    # validate the attributed field info
    attribute_field_info = json.loads(attribute_field_info)
    validate_attribute_field_info(attribute_field_info)

    with fiona.open(in_data, 'r') as src:
        dst_schema = src.schema.copy()
        # add the new fields to the output schema
        for field_info in attribute_field_info:
            field_name = field_info['name']
            field_dtype = field_info['dtype']
            # note: if the field already exists, the dtype will be changes
            if field_name in dst_schema['properties'].keys():
                print("Warning: field {} already exists and will be overwritten with new dtype and values.".format(
                        field_name))
            dst_schema['properties'][field_name] = field_dtype
        dst_crs = src.crs
        dst_driver = src.driver

        with fiona.open(out_data, 'w',
                        schema=dst_schema,
                        crs=dst_crs,
                        driver=dst_driver) as dst:
            new_properties = {d['name']: d['value'] for d in attribute_field_info}
            for feat in src:
                feat['properties'].update(new_properties)
                dst.write(feat)


if __name__ == '__main__':

    main()

