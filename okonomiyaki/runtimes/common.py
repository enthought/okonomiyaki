from okonomiyaki.platforms import EPDPlatform
from okonomiyaki.versions import SemanticVersion


RuntimeVersion = SemanticVersion


def _platform_string(platform):
    disp_platform = EPDPlatform(platform).platform_name
    disp_platform += "_" + str(platform.arch)
    return disp_platform
