import configparser


def create_or_open_conf_file(frontend):
    config = configparser.ConfigParser()
    config.read('conf.ini')

    # Set the selected frontend in the configuration file
    config['General'] = {'frontend': frontend}

    # Save the changes to the configuration file
    with open('conf.ini', 'w') as configfile:
        config.write(configfile)

# Example usage
selected_frontend = 'hyperspin'  # Replace with the frontend selected by the user
create_or_open_conf_file(selected_frontend)
