import sys
import traceback
 
from optparse import OptionParser
from fedconfig import FedConfigurator
from datetime import datetime

def parse_system_property(sys_prop):
    if not sys_prop:
        print "ERROR: Empty system property not allowed!"
        exit(1)

    s = sys_prop.split(":", 1)
    if not s[0]:
        print "ERROR: Empty system property name!"
        exit(1)

    name = s[0]
    value = s[1] if len(s) > 1 else None

    return (name, value)


def main():
    prog = sys.argv[0]
    version = "%prog 0.1.0"
    usage = "%prog OPTIONS"
 
    parser = OptionParser(usage=usage, version=version)
    parser.add_option("-v", "--verbose", dest="verbose", help="Enable verbose messages [optional]", action="store_true")
    parser.add_option("-e", "--env", dest="env_file_path", help="Path of environment archive (.env)", metavar="FILEPATH")
    parser.add_option("-p", "--pol", dest="pol_file_path", help="Path of policy archive (.pol)", metavar="FILEPATH")
    parser.add_option("-c", "--config", dest="config_file_path", help="Path of JSON configuration file", metavar="FILEPATH")
    parser.add_option("--prop", dest="prop_file_path", help="Path of JSON property file [optional]", metavar="FILEPATH")
    parser.add_option("--cert", dest="cert_file_path", help="Path of JSON certificate configuration file [optional]", metavar="FILEPATH")
    parser.add_option("--output-fed", dest="out_fed_file_path", help="Path of output deployment archive file (.fed) [optional]", metavar="FILEPATH")
    parser.add_option("--output-env", dest="out_env_file_path", help="Path of output environment archive file (.env) [optional]", metavar="FILEPATH")
    parser.add_option("-D", "--define", dest="sys_properties", help="Define a system property [multiple]", metavar="NAME:VALUE", action="append")

    (options, args) = parser.parse_args()

    if not options.env_file_path:
        parser.error("Environment archive option is missing!")
    if not options.pol_file_path:
        parser.error("Policy archive option is missing!")
    if not options.config_file_path:
        parser.error("Configuration file option is missing!")

    # Add some standard system properties
    sys_properties = {}
    sys_properties["_system.build.datetime"] = datetime.now().isoformat()

    if options.sys_properties:
        for sp in options.sys_properties:
            (name, value) = parse_system_property(sp)
            sys_properties[name] = value
 
    try:
        fed_config = FedConfigurator(options.pol_file_path, options.env_file_path, options.config_file_path, options.cert_file_path, options.prop_file_path)

        for name, value in sys_properties.items():
            print "INFO : System property %s=%s" % (name, value)
        fed_config.set_system_properties(sys_properties)

        succeeded = fed_config.configure_entities()
        if succeeded:
            succeeded = fed_config.configure_certificates()
            if succeeded:
                if options.out_fed_file_path:
                    fed_config.write_fed(options.out_fed_file_path)
                if options.out_env_file_path:
                    fed_config.write_env(options.out_env_file_path)
            else:
                print "ERROR: Configuration of certificates failed!"
        else:
            print "ERROR: Configuration of entities failed; check JSON configuration for unconfigured entity fields!"

        if not succeeded:
            sys.exit(1)

    except Exception as e:
        if options.verbose:
            traceback.print_exc()
        else:
            print "ERROR: %r" % (e)
        sys.exit(1) 

    sys.exit(0)

if __name__ == "__main__":
    main()
