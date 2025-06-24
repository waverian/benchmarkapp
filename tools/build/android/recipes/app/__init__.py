from pythonforandroid.recipe import CythonRecipe, IncludedFilesBehaviour
from pythonforandroid.toolchain import current_directory, shprint
from pythonforandroid import logger


class AppRecipe(IncludedFilesBehaviour, CythonRecipe):
    version = None
    url = None

    src_filename = 'src'

    config_env = {}

    depends = ['kivy', 'libevolution-benchmark', 'setuptools']

    def get_recipe_env(self, arch):
        env = super().get_recipe_env(arch)
        env.update(self.config_env)
        return env

    def cythonize_build(self, env, build_dir='.'):
        super().cythonize_build(env, build_dir=build_dir)
        print('cythonising MyApp Done!')
        

    def cythonize_file(self, env, build_dir, filename):
        super().cythonize_file(env, build_dir, filename)

    def get_recipe_env(self, arch):
        env = super().get_recipe_env(arch)
        # NDKPLATFORM is our switch for detecting Android platform, so can't be None
        env['NDKPLATFORM'] = "NOTNONE"
        return env


recipe = AppRecipe()
