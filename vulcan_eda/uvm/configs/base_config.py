import pyuvm

class BaseConfig:
    def set(self, context, inst_name=""):
        pyuvm.ConfigDB().set(context, inst_name, type(self).key(), self)

    @classmethod
    def get(cls, context):
        try:
            return pyuvm.ConfigDB().get(context, "", cls.key())
        except pyuvm.UVMConfigItemNotFound:
            pass
        try:
            return cls()
        except (TypeError, ValueError) as error:
            path = "the root" if context is None else context.get_full_name()
            raise pyuvm.UVMConfigItemNotFound(f"no {cls.__name__} set for {path} and it has no default") from error

    @classmethod
    def key(cls):
        return f"{cls.__module__}.{cls.__qualname__}"
