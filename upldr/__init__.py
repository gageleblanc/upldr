if __name__ == '__main__':
    from clilib.util.loader import Loader

    modules = ['put', 'serve', 's3', 'api', 'remote']
    Loader.start_app(modules, "upldr_libs")