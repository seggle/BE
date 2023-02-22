

def get_error_msg(serializer):
    default_errors = serializer.errors
    message = {}
    for field_name, field_errors in default_errors.items():
        error = [field_error[:] for field_error in field_errors]
        print(field_errors, error)
        message[field_name] = field_errors[0]
    return message
