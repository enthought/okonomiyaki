_JULIA_V1 = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "title": "PythonRuntimeMetadata v1.0",
    "description": "PythonRuntimeMetadata runtime/metadata.json schema.",
    "type": "object",
    "properties": {
        "metadata_version": {
            "description": "The metadata version.",
            "type": "string"
        },
        "language": {
            "description": "The language (e.g. python, julia)",
            "type": "string"
        },
        "implementation": {
            "description": "The implementation (e.g. cpython)",
            "type": "string"
        },
        "version": {
            "description": "The full version (upstream + build)",
            "type": "string"
        },
        "platform": {
            "description": ("The platform string (as can be parsed by"
                            "EPDPlatform.from_epd_string"),
            "type": "string"
        },
        "build_revision": {
            "description": "Build revision (internal only).",
            "type": "string",
        },
        "executable": {
            "description": "The full path to the actual runtime executable.",
            "type": "string",
        },
        "paths": {
            "description": "The list of path to have access to this runtime.",
            "type": "array",
            "items": {"type": "string"},
        },
        "post_install": {
            "description": ("The command (as a list) to execute after "
                            "installation."),
            "type": "array",
            "items": {"type": "string"},
        },
    }
}

_PYTHON_V1 = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "title": "PythonRuntimeMetadata v1.0",
    "description": "PythonRuntimeMetadata runtime/metadata.json schema.",
    "type": "object",
    "properties": {
        "metadata_version": {
            "description": "The metadata version.",
            "type": "string"
        },
        "language": {
            "description": "The language (e.g. python, julia)",
            "type": "string"
        },
        "implementation": {
            "description": "The implementation (e.g. cpython)",
            "type": "string"
        },
        "version": {
            "description": "The full version (upstream + build)",
            "type": "string"
        },
        "platform": {
            "description": ("The platform string (as can be parsed by"
                            "EPDPlatform.from_epd_string"),
            "type": "string"
        },
        "build_revision": {
            "description": "Build revision (internal only).",
            "type": "string",
        },
        "executable": {
            "description": "The full path to the actual runtime executable.",
            "type": "string",
        },
        "paths": {
            "description": "The list of path to have access to this runtime.",
            "type": "array",
            "items": {"type": "string"},
        },
        "post_install": {
            "description": ("The command (as a list) to execute after "
                            "installation."),
            "type": "array",
            "items": {"type": "string"},
        },
        "scriptsdir": {
            "description": "Full path to scripts directory.",
            "type": "string",
        },
        "site_packages": {
            "description": "The full path to the python site packages.",
            "type": "string",
        },
    }
}
