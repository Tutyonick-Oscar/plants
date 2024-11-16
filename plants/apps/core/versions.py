from rest_framework.versioning import NamespaceVersioning


class NpVersioning(NamespaceVersioning):

    allowed_versions = ["v1.0", "v1.1"]
    default_version = "v1.0"
    version_param = "v"
    invalid_version_message = "unsuported version given"
