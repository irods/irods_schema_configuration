import inspect
import json
import optparse
import os
import sys


SCHEMA_VERSION = '3'

def get_script_directory():
    return os.path.dirname(os.path.abspath(
        inspect.stack()[0][1]))

def makedirs_catch_preexisting(*args, **kwargs):
    try:
        os.makedirs(*args, **kwargs)
    except OSError as e:
        if e[0] != 17: # 17 == File exists
            raise

def is_schema_template(filename):
    return filename.endswith('.json') and not filename.startswith('sample')

def update_schema_dict(schema_dict, url_base_with_version, filename):
    schema_dict['id'] = '{url_base_with_version}/{filename}#'.format(**vars())

def main(template_directory, output_directory_base, url_base):
    url_base_with_version = '{0}/v{1}'.format(url_base, SCHEMA_VERSION)
    output_directory_with_version = os.path.join(output_directory_base, 'v' + SCHEMA_VERSION)
    makedirs_catch_preexisting(output_directory_with_version)
    for dirpath, _, filenames in os.walk(template_directory):
        for filename in filenames:
            if is_schema_template(filename):
                with open(os.path.join(dirpath, filename)) as f_in:
                    schema_dict = json.load(f_in)
                    update_schema_dict(schema_dict, url_base_with_version, filename)
                    with open(os.path.join(output_directory_with_version, filename), 'w') as f_out:
                        json.dump(schema_dict, f_out, indent=4, sort_keys=True)

if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option('--output_directory_base')
    parser.add_option('--template_directory')
    parser.add_option('--url_base')
    options, _ = parser.parse_args()

    if not options.output_directory_base:
        parser.print_usage()
        sys.exit(1)

    if not options.template_directory:
        options.template_directory = os.path.join(get_script_directory(), 'schemas')

    if not options.url_base:
        options.url_base = 'file://' + os.path.abspath(options.output_directory_base)

    options.url_base = options.url_base.rstrip('/')

    main(options.template_directory, options.output_directory_base, options.url_base)
