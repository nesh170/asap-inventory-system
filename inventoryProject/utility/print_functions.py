SERIALIZER_PRETTY_PRINT_FORMAT = "{key} : {data}\n".format
SERIALIZER_PRETTY_PRINT_COMPARE_FORMAT = "{key} : OLD={old_data}, NEW={new_data}\n".format


def serializer_pretty_print(serializer, title=None, validated=True):
    data = serializer.validated_data if validated else serializer.data
    title_string = "" if title is None else title + "\n"
    return title_string + "".join([SERIALIZER_PRETTY_PRINT_FORMAT(key=key, data=data.get(key)) for key in data])


def serializer_compare_pretty_print(old_serializer, new_serializer, title=None):
    old_data = old_serializer.data
    new_data = new_serializer.validated_data
    title_string = "" if title is None else title + "\n"
    string_array = [SERIALIZER_PRETTY_PRINT_FORMAT(key=key, data=old_data.get(key))
                    if new_data.get(key) is None else
                    SERIALIZER_PRETTY_PRINT_COMPARE_FORMAT(key=key, old_data=old_data.get(key),
                                                           new_data=new_data.get(key)) for key in old_data]
    return title_string + "".join(string_array)
