SERIALIZER_PRETTY_PRINT_FORMAT = "{key} : {data}\n".format
SERIALIZER_PRETTY_PRINT_COMPARE_FORMAT = "{key} : OLD={old_data}, NEW={new_data}\n".format


def pretty_print_non_str(parent_key, data):
    if isinstance(data, list):
        return "{key}: \n".format(key=parent_key) + "".join(["".join(
            ["".join([SERIALIZER_PRETTY_PRINT_FORMAT(key=key, data=order_dict.get(key))
                      for key in order_dict])]) for order_dict in data])
    else:
        return ""


def serializer_pretty_print(serializer, title=None, validated=True):
    data = serializer.validated_data if validated else serializer.data
    title_string = "" if title is None else title + "\n"
    return title_string + "".join([SERIALIZER_PRETTY_PRINT_FORMAT(key=key, data=data.get(key)) if
                                   isinstance(data.get(key), str) or isinstance(data.get(key), int) else
                                   pretty_print_non_str(key, data.get(key)) for key in data])


def serializer_compare_pretty_print(old_serializer, new_serializer, title=None, validated=True):
    old_data = old_serializer.data
    new_data = new_serializer.validated_data if validated else new_serializer.data
    title_string = "" if title is None else title + "\n"
    string_array = [(SERIALIZER_PRETTY_PRINT_FORMAT(key=key, data=old_data.get(key))
                    if new_data.get(key) is None or new_data.get(key) == old_data.get(key) else
                    SERIALIZER_PRETTY_PRINT_COMPARE_FORMAT(key=key, old_data=old_data.get(key),
                                                           new_data=new_data.get(key)))
                    if isinstance(old_data.get(key), str) or isinstance(old_data.get(key), int)
                    or old_data.get(key) is None else "" for key in old_data]
    return title_string + "".join(string_array)
