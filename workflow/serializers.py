import pickle
import json
from typing import Protocol, TextIO


class Serializer(Protocol):
    def load(

class SerializerManager:
    """Contains registered serializers.

    A configured instance of this class is available at
    :attr:`workflow.manager`.

    Use :meth:`register()` to register new (or replace
    existing) serializers, which you can specify by name when calling
    :class:`~workflow.Workflow` data storage methods.


    """

    def __init__(self) -> None:
        """Create new SerializerManager object."""
        self._serializers = {}

    def register(self, name: str, serializer: Serializer):
        """Register ``serializer`` object under ``name``.

        Raises :class:`AttributeError` if ``serializer`` in invalid.


            ``name`` will be used as the file extension of the saved files.

        :param name: Name to register ``serializer`` under
        :type name: ``str``
        :param serializer: object with ``load()`` and ``dump()``
            methods

        """
        # Basic validation
        getattr(serializer, 'load')
        getattr(serializer, 'dump')

        self._serializers[name] = serializer

    def serializer(self, name: str) -> Serializer:
        """Return serializer object for ``name``.

        :param name: Name of serializer to return
        :type name: ``str``
        :returns: serializer object or ``None`` if no such serializer
            is registered.

        """
        return self._serializers.get(name)

    def unregister(self, name):
        """Remove registered serializer with ``name``.

        Raises a :class:`ValueError` if there is no such registered
        serializer.

        :param name: Name of serializer to remove
        :type name: ``str`` or ``str``
        :returns: serializer object

        """
        if name not in self._serializers:
            raise ValueError('No such serializer registered : {0}'.format(
                             name))

        serializer = self._serializers[name]
        del self._serializers[name]

        return serializer

    @ property
    def serializers(self):
        """Return names of registered serializers."""
        return sorted(self._serializers.keys())

class Serializer(Protocol):
    @ classmethod
    def load(cls, file_obj: TextIO) -> dict:
        ...

    @ classmethod
    def dump(cls, obj: object, file_obj: TextIO):
        ...


class JSONSerializer:
    """Wrapper around :mod:`json`. Sets ``indent`` and ``encoding``.

    Use this serializer if you need readable data files. JSON doesn't
    support Python objects as well as pickle, so be
    careful which data you try to serialize as JSON.

    """

    @ classmethod
    def load(cls, file_obj: TextIO) -> dict:
        """Load serialized object from open JSON file.

        :param file_obj: file handle
        :type file_obj: ``file`` object
        :returns: object loaded from JSON file
        :rtype: object

        """
        return json.load(file_obj)

    @ classmethod
    def dump(cls, obj, file_obj):
        """Serialize object ``obj`` to open JSON file.

        .. versionadded:: 1.8

        :param obj: Python object to serialize
        :type obj: JSON-serializable data structure
        :param file_obj: file handle
        :type file_obj: ``file`` object

        """
        return json.dump(obj, file_obj, indent=2, encoding='utf-8')


class CPickleSerializer:
    """Wrapper around :mod:`cPickle`. Sets ``protocol``.

    This is the default serializer and the best combination of speed and
    flexibility.

    """

    @ classmethod
    def load(cls, file_obj):
        """Load serialized object from open pickle file.

        .. versionadded:: 1.8

        :param file_obj: file handle
        :type file_obj: ``file`` object
        :returns: object loaded from pickle file
        :rtype: object

        """
        return pickle.load(file_obj)

    @ classmethod
    def dump(cls, obj, file_obj):
        """Serialize object ``obj`` to open pickle file.

        .. versionadded:: 1.8

        :param obj: Python object to serialize
        :type obj: Python object
        :param file_obj: file handle
        :type file_obj: ``file`` object

        """
        return pickle.dump(obj, file_obj, protocol=-1)


class PickleSerializer(object):
    """Wrapper around :mod:`pickle`. Sets ``protocol``.

    .. versionadded:: 1.8

    Use this serializer if you need to add custom pickling.

    """

    @ classmethod
    def load(cls, file_obj):
        """Load serialized object from open pickle file.

        .. versionadded:: 1.8

        :param file_obj: file handle
        :type file_obj: ``file`` object
        :returns: object loaded from pickle file
        :rtype: object

        """
        return pickle.load(file_obj)

    @ classmethod
    def dump(cls, obj, file_obj):
        """Serialize object ``obj`` to open pickle file.

        .. versionadded:: 1.8

        :param obj: Python object to serialize
        :type obj: Python object
        :param file_obj: file handle
        :type file_obj: ``file`` object

        """
        return pickle.dump(obj, file_obj, protocol=-1)
